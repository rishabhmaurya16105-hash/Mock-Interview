from django.conf import settings
import httpx


def _base_url() -> str:
    return getattr(settings, 'AI_SERVICE_URL', 'http://127.0.0.1:8001').rstrip('/')


def generate_questions(
    resume_text: str,
    difficulty: str,
    num_questions: int,
    timeout: float = 60.0,
) -> dict:
    url = f'{_base_url()}/generate-questions'
    payload = {
        'resume_text': resume_text,
        'difficulty': difficulty,
        'num_questions': num_questions,
    }
    with httpx.Client(timeout=timeout) as client:
        response = client.post(url, json=payload)
    response.raise_for_status()
    return response.json()


def evaluate_session(
    difficulty: str,
    items: list[dict],
    timeout: float = 60.0,
) -> dict:
    url = f'{_base_url()}/evaluate-session'
    payload = {'difficulty': difficulty, 'items': items}
    with httpx.Client(timeout=timeout) as client:
        response = client.post(url, json=payload)
    response.raise_for_status()
    return response.json()
