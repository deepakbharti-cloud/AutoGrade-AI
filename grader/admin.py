from django.contrib import admin
from .models import QuestionPaper, Question, Student, CopySubmission, SubmissionPage, AnswerResult


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(QuestionPaper)
class QuestionPaperAdmin(admin.ModelAdmin):
    list_display  = ['title', 'subject', 'class_name', 'total_marks', 'teacher', 'created_at']
    list_filter   = ['subject', 'teacher']
    inlines       = [QuestionInline]


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'roll_number', 'class_name', 'phone', 'teacher']
    list_filter  = ['class_name', 'teacher']
    search_fields = ['name', 'roll_number']


@admin.register(CopySubmission)
class CopySubmissionAdmin(admin.ModelAdmin):
    list_display  = ['student', 'paper', 'status', 'total_marks_obtained', 'percentage', 'submitted_at']
    list_filter   = ['status', 'paper__subject']
    readonly_fields = ['total_marks_obtained', 'percentage', 'whatsapp_sent']


@admin.register(AnswerResult)
class AnswerResultAdmin(admin.ModelAdmin):
    list_display = ['submission', 'question', 'final_marks', 'keyword_score', 'checked_at']
    readonly_fields = ['extracted_text', 'ai_feedback', 'keyword_score', 'ai_marks']
