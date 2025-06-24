#from django.db import models

# Create your models here.

from transformers import pipeline

classifier = pipeline("text classification",  model = "yiyanghkust/bert-base-uncased-finetuned-phishing" )

def clasify_message(text):
    result = classifier(text)
    return result[0]