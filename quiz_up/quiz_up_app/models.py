from django.db import models

class Users(models.Model):
    username = models.CharField(max_length=30)
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    email = models.EmailField(max_length=30)
    password = models.CharField(max_length=128) 
    
class Document(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


class Question(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    correct_answer = models.CharField(max_length=255)
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

class QuizAnalysis(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    correct = models.IntegerField()
    total = models.IntegerField()
    percentage = models.FloatField()
    feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)    

class QuizAttempt(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)  # e.g., "Practice Quiz #1"
    correct = models.IntegerField()
    total = models.IntegerField()
    percentage = models.FloatField()
    feedback = models.TextField()
    documents = models.ManyToManyField(QuizAnalysis)  # Link to individual document analyses
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title