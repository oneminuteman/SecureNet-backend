from django.core.management.base import BaseCommand
from myapp.apps import MyappConfig

class Command(BaseCommand):
    help = 'Test that the ML model file exists and loads correctly.'

    def handle(self, *args, **options):
        if MyappConfig.model is not None:
            self.stdout.write(self.style.SUCCESS('ML model loaded successfully.'))
        else:
            self.stdout.write(self.style.ERROR('ML model is not loaded. Please retrain the model.')) 