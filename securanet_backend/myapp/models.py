#from django.db import models

# Create your models here.

from transformers import pipeline

classifier = pipeline("text-classification",  model = "distilbert-base-uncased-finetuned-sst-2-english" )

def clasify_message(text):
    result = classifier(text)
    return result[0]