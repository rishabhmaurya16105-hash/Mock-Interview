from django.contrib import admin
from .models import Answer, Evaluation, InterviewSession, Question, UploadedResume

admin.site.register(InterviewSession)
admin.site.register(UploadedResume)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Evaluation)
