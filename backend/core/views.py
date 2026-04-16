from django.shortcuts import get_object_or_404
import httpx
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .ai_client import evaluate_session as ai_evaluate_session
from .ai_client import generate_questions
from .models import Answer, Evaluation, InterviewSession, Question, UploadedResume
from .resume_parser import extract_text_from_resume
from .serializers import (
    AnswerSerializer,
    AnswerSubmitSerializer,
    InterviewSessionSerializer,
    QuestionSerializer,
    ResumeUploadSerializer,
)


class InterviewSessionCreateView(APIView):
    def post(self, request):
        serializer = InterviewSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class InterviewResumeUploadView(APIView):
    def post(self, request, pk):
        session = get_object_or_404(InterviewSession, pk=pk)
        serializer = ResumeUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uploaded_resume, _ = UploadedResume.objects.update_or_create(
            session=session,
            defaults={'file': serializer.validated_data['file']},
        )
        uploaded_resume.extracted_text = extract_text_from_resume(uploaded_resume.file.path)
        uploaded_resume.save(update_fields=['extracted_text'])

        return Response(
            {'session_id': str(session.id), 'resume_id': str(uploaded_resume.id)},
            status=status.HTTP_200_OK,
        )


class InterviewSessionDetailView(APIView):
    def get(self, request, pk):
        session = get_object_or_404(InterviewSession, pk=pk)
        session_data = InterviewSessionSerializer(session).data

        resume_data = None
        if hasattr(session, 'resume'):
            resume_data = {
                'id': str(session.resume.id),
                'file': session.resume.file.name,
                'created_at': session.resume.created_at,
            }

        questions = QuestionSerializer(session.questions.all(), many=True).data

        return Response(
            {
                'session': session_data,
                'resume': resume_data,
                'questions': questions,
            },
            status=status.HTTP_200_OK,
        )


class InterviewAnswerCreateView(APIView):
    def post(self, request, pk):
        session = get_object_or_404(InterviewSession, pk=pk)
        serializer = AnswerSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question_id = serializer.validated_data['question_id']
        answer_text = serializer.validated_data['answer'].strip()
        if not answer_text:
            return Response(
                {'detail': 'Answer text cannot be empty.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        question = get_object_or_404(
            Question,
            pk=question_id,
            session=session,
        )

        answer, _ = Answer.objects.update_or_create(
            question=question,
            defaults={'text': answer_text},
        )

        return Response(
            AnswerSerializer(answer).data,
            status=status.HTTP_200_OK,
        )


class InterviewGenerateQuestionsView(APIView):
    def post(self, request, pk):
        session = get_object_or_404(InterviewSession, pk=pk)
        resume = getattr(session, 'resume', None)

        if not resume or not resume.extracted_text.strip():
            return Response(
                {'detail': 'Resume text is required before question generation.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            num_questions = int(request.data.get('num_questions', 5))
        except (TypeError, ValueError):
            return Response(
                {'detail': 'num_questions must be an integer.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if num_questions < 1 or num_questions > 20:
            return Response(
                {'detail': 'num_questions must be between 1 and 20.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            ai_response = generate_questions(
                resume_text=resume.extracted_text,
                difficulty=session.difficulty,
                num_questions=num_questions,
            )
        except (httpx.HTTPError, ValueError) as exc:
            return Response(
                {'detail': f'AI service request failed: {exc}'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        generated_questions = ai_response.get('questions', [])
        if not isinstance(generated_questions, list) or not all(
            isinstance(item, str) and item.strip() for item in generated_questions
        ):
            return Response(
                {'detail': 'AI service returned invalid questions payload.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        session.questions.all().delete()
        question_objects = [
            Question(session=session, order=index + 1, text=question_text.strip())
            for index, question_text in enumerate(generated_questions)
        ]
        Question.objects.bulk_create(question_objects)

        serializer = QuestionSerializer(session.questions.all(), many=True)
        return Response(
            {
                'session_id': str(session.id),
                'questions': serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class InterviewCompleteView(APIView):
    def post(self, request, pk):
        session = get_object_or_404(InterviewSession, pk=pk)
        questions = list(session.questions.all())

        if not questions:
            return Response(
                {'detail': 'No questions found for this session.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        items = []
        for question in questions:
            answer_text = ''
            if hasattr(question, 'answer'):
                answer_text = question.answer.text
            items.append({'question': question.text, 'answer': answer_text})

        try:
            ai_response = ai_evaluate_session(
                difficulty=session.difficulty,
                items=items,
            )
        except (httpx.HTTPError, ValueError) as exc:
            return Response(
                {'detail': f'AI service request failed: {exc}'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        total_score = ai_response.get('total_score')
        if not isinstance(total_score, int):
            return Response(
                {'detail': 'AI service returned invalid evaluation payload.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        evaluation, _ = Evaluation.objects.update_or_create(
            session=session,
            defaults={
                'total_score': total_score,
                'feedback': ai_response,
            },
        )

        session.status = InterviewSession.Status.COMPLETED
        session.save(update_fields=['status'])

        return Response(
            {
                'session_id': str(session.id),
                'status': session.status,
                'evaluation_id': str(evaluation.id),
                'total_score': evaluation.total_score,
                'feedback': evaluation.feedback,
            },
            status=status.HTTP_200_OK,
        )


class InterviewResultView(APIView):
    def get(self, request, pk):
        session = get_object_or_404(InterviewSession, pk=pk)

        if session.status != InterviewSession.Status.COMPLETED:
            return Response(
                {'detail': 'Session is not completed yet.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not hasattr(session, 'evaluation'):
            return Response(
                {'detail': 'Evaluation is not available for this session.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        evaluation = session.evaluation
        return Response(
            {
                'session_id': str(session.id),
                'status': session.status,
                'evaluation_id': str(evaluation.id),
                'total_score': evaluation.total_score,
                'feedback': evaluation.feedback,
            },
            status=status.HTTP_200_OK,
        )
