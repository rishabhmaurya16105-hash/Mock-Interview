import json
import os

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schemas import (
    EvaluateRequest,
    EvaluateResponse,
    GenerateQuestionsRequest,
    GenerateQuestionsResponse,
)

load_dotenv()

app = FastAPI(title='Mock Interview AI Service')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173', 'http://localhost:8000'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/health')
def health_check():
    return {'status': 'ok'}


def get_groq_config():
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail='GROQ_API_KEY is not configured.',
        )

    model_name = os.getenv('GROQ_MODEL', 'llama-3.1-8b-instant')
    return api_key, model_name


def call_groq_json(system_prompt: str, user_prompt: str):
    api_key, model_name = get_groq_config()

    try:
        response = httpx.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            },
            json={
                'model': model_name,
                'temperature': 0.4,
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt},
                ],
            },
            timeout=45.0,
        )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail=f'LLM request failed: {exc}',
        ) from exc

    if response.status_code != 200:
        error_detail = ''
        try:
            error_detail = response.text
        except Exception:
            error_detail = 'No error body returned by provider.'

        raise HTTPException(
            status_code=502,
            detail=(
                'LLM request failed with status '
                f'{response.status_code}. Provider response: {error_detail}'
            ),
        )

    try:
        response_json = response.json()
        message_content = response_json['choices'][0]['message']['content'].strip()
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail='Unexpected Groq response format.',
        ) from exc

    if message_content.startswith('```'):
        message_content = message_content.strip('`')
        message_content = message_content.replace('json', '', 1).strip()

    return message_content


@app.post('/generate-questions', response_model=GenerateQuestionsResponse)
def generate_questions(payload: GenerateQuestionsRequest):
    prompt = (
        'Generate interview questions as a strict JSON array of strings.\n'
        f'Difficulty: {payload.difficulty}\n'
        f'Count: {payload.num_questions}\n'
        f'Resume context:\n{payload.resume_text}\n'
        'Return only valid JSON. Do not use markdown code fences.'
    )
    message_content = call_groq_json(
        system_prompt=(
            'You are an interview generator. '
            'Return only a valid JSON array of question strings.'
        ),
        user_prompt=prompt,
    )

    try:
        parsed_questions = json.loads(message_content)
        if (
            not isinstance(parsed_questions, list)
            or not all(isinstance(item, str) for item in parsed_questions)
        ):
            raise ValueError('LLM output is not list[str].')
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail='Failed to parse LLM output as JSON list of strings.',
        ) from exc

    questions = parsed_questions[: payload.num_questions]
    if len(questions) < payload.num_questions:
        raise HTTPException(
            status_code=502,
            detail='LLM returned fewer questions than requested.',
        )

    return GenerateQuestionsResponse(questions=questions)


@app.post('/evaluate-session', response_model=EvaluateResponse)
def evaluate_session(payload: EvaluateRequest):
    items_text = '\n'.join(
        [
            f'Question {index + 1}: {item.question}\nAnswer: {item.answer}'
            for index, item in enumerate(payload.items)
        ]
    )
    prompt = (
        'Evaluate interview answers and return strict JSON object with keys:\n'
        '- total_score (0-100 integer)\n'
        '- overall_feedback (string)\n'
        '- per_question (array of objects with question_index, score, feedback)\n'
        f'Difficulty: {payload.difficulty}\n'
        f'Number of items: {len(payload.items)}\n'
        f'Q&A:\n{items_text}\n'
        'Return only valid JSON. Do not use markdown.'
    )
    message_content = call_groq_json(
        system_prompt=(
            'You are an interview evaluator. '
            'Score answers fairly and return only valid JSON.'
        ),
        user_prompt=prompt,
    )

    try:
        parsed_evaluation = json.loads(message_content)
        validated = EvaluateResponse(**parsed_evaluation)
    except (json.JSONDecodeError, ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=502,
            detail='Failed to parse LLM evaluation output with required schema.',
        ) from exc

    return validated
