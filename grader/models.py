from django.db import models
from django.contrib.auth.models import User


class QuestionPaper(models.Model):
    teacher     = models.ForeignKey(User, on_delete=models.CASCADE)
    title       = models.CharField(max_length=200)
    subject     = models.CharField(max_length=100)
    class_name  = models.CharField(max_length=20)
    total_marks = models.IntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.subject}"

    def compute_total(self):
        self.total_marks = sum(q.max_marks for q in self.questions.all())
        self.save()

class Question(models.Model):
    TYPE_CHOICES = [('mcq','MCQ'), ('short','Short Answer'), ('long','Long Answer')]

    paper       = models.ForeignKey(QuestionPaper, on_delete=models.CASCADE, related_name='questions')
    question_no = models.IntegerField()
    question_text = models.TextField()
    q_type      = models.CharField(max_length=10, choices=TYPE_CHOICES)
    correct_answer = models.TextField(help_text="MCQ: A/B/C/D | Short/Long: model answer")
    options     = models.TextField(blank=True, help_text="MCQ options comma-separated: A,B,C,D")
    keywords    = models.TextField(blank=True, help_text="Comma-separated important keywords")
    max_marks   = models.FloatField(default=1)

    class Meta:
        ordering = ['question_no']

    def __str__(self):
        return f"Q{self.question_no} ({self.q_type})"

    def keyword_list(self):
        return [k.strip().lower() for k in self.keywords.split(',') if k.strip()]


class Student(models.Model):
    teacher     = models.ForeignKey(User, on_delete=models.CASCADE)
    name        = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20)
    class_name  = models.CharField(max_length=20)
    phone       = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.name} (Roll: {self.roll_number})"


class CopySubmission(models.Model):
    STATUS = [('pending','Pending'), ('processing','Processing'), ('done','Done'), ('failed','Failed')]

    student     = models.ForeignKey(Student, on_delete=models.CASCADE)
    paper       = models.ForeignKey(QuestionPaper, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    status      = models.CharField(max_length=20, choices=STATUS, default='pending')
    total_marks_obtained = models.FloatField(default=0)
    percentage  = models.FloatField(default=0)
    whatsapp_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.name} - {self.paper.title}"

    def grade(self):
        p = self.percentage
        if p >= 90: return 'A+'
        if p >= 80: return 'A'
        if p >= 70: return 'B+'
        if p >= 60: return 'B'
        if p >= 50: return 'C'
        return 'F'


class SubmissionPage(models.Model):
    submission  = models.ForeignKey(CopySubmission, on_delete=models.CASCADE, related_name='pages')
    page_number = models.IntegerField()
    image       = models.ImageField(upload_to='submissions/')
    processed_image = models.ImageField(upload_to='processed/', blank=True, null=True)

    class Meta:
        ordering = ['page_number']


class AnswerResult(models.Model):
    submission     = models.ForeignKey(CopySubmission, on_delete=models.CASCADE, related_name='results')
    question       = models.ForeignKey(Question, on_delete=models.CASCADE)
    extracted_text = models.TextField(blank=True)
    keywords_found = models.TextField(blank=True)
    keywords_missing = models.TextField(blank=True)
    keyword_score  = models.FloatField(default=0)
    ai_marks       = models.FloatField(default=0)
    final_marks    = models.FloatField(default=0)
    ai_feedback    = models.TextField(blank=True)
    checked_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['question__question_no']

    def kw_found_list(self):
        return [k for k in self.keywords_found.split(',') if k.strip()]

    def kw_missing_list(self):
        return [k for k in self.keywords_missing.split(',') if k.strip()]
