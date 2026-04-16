from django.urls import path

from .views import (
    InterviewAnswerCreateView,
    InterviewCompleteView,
    InterviewGenerateQuestionsView,
    InterviewResumeUploadView,
    InterviewResultView,
    InterviewSessionCreateView,
    InterviewSessionDetailView,
)

urlpatterns = [
    path('sessions/', InterviewSessionCreateView.as_view(), name='create-session'),
    path('sessions/<uuid:pk>/', InterviewSessionDetailView.as_view(), name='session-detail'),
    path(
        'sessions/<uuid:pk>/questions/generate/',
        InterviewGenerateQuestionsView.as_view(),
        name='generate-questions',
    ),
    path(
        'sessions/<uuid:pk>/answers/',
        InterviewAnswerCreateView.as_view(),
        name='submit-answer',
    ),
    path(
        'sessions/<uuid:pk>/complete/',
        InterviewCompleteView.as_view(),
        name='complete-session',
    ),
    path(
        'sessions/<uuid:pk>/result/',
        InterviewResultView.as_view(),
        name='session-result',
    ),
    path(
        'sessions/<uuid:pk>/resume/',
        InterviewResumeUploadView.as_view(),
        name='upload-resume',
    ),
]
