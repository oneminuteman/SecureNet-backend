from django.core.management.base import BaseCommand
from myapp.ml.train_model import train_header_classifier

class Command(BaseCommand):
    help = 'Train the email header classification model'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting model training...')
        )
        
        try:
            train_header_classifier()
            self.stdout.write(
                self.style.SUCCESS('Model training completed successfully!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Model training failed: {str(e)}')
            ) 