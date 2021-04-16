from django.db import models

# Create your models here.
class MCQQuestion(models.Model):
	QuestionId = models.CharField(max_length = 30)
	AnswerId = models.CharField(max_length = 30)

class SAQuestion(models.Model):
	QuestionId = models.CharField(max_length = 30)
	Answer = models.CharField(max_length = 30)