from rest_framework import serializers

from .models import Answer, Evaluation, InterviewSession, Question

ALLOWED_RESUME_EXTENSIONS = {'.pdf', '.docx'}
MAX_RESUME_SIZE_BYTES = 5 * 1024 * 1024


class InterviewSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewSession
        fields = ['id', 'difficulty', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'session', 'order', 'text']
        read_only_fields = ['id']


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'question', 'text', 'created_at']
        read_only_fields = ['id', 'created_at']


class EvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields = ['id', 'session', 'total_score', 'feedback', 'created_at']
        read_only_fields = ['id', 'created_at']


class ResumeUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        file_name = value.name.lower()
        if not any(file_name.endswith(extension) for extension in ALLOWED_RESUME_EXTENSIONS):
            raise serializers.ValidationError('Only PDF and DOCX files are allowed.')

        if value.size > MAX_RESUME_SIZE_BYTES:
            raise serializers.ValidationError('Resume file size must be 5 MB or smaller.')

        return value


class AnswerSubmitSerializer(serializers.Serializer):
    question_id = serializers.UUIDField()
    answer = serializers.CharField()
