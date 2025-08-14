from django.apps import AppConfig
import os
import logging

logger = logging.getLogger(__name__)

class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'phishing_email'
    model = None

    def ready(self):
        """Load the ML model when Django starts up."""
        try:
            from joblib import load
            model_path = os.path.join(os.path.dirname(__file__), 'ml', 'header_classifier.pkl')
            
            if os.path.exists(model_path):
                MyappConfig.model = load(model_path)
                logger.info("ML model loaded successfully")
            else:
                logger.warning(f"Model file not found at {model_path}")
                logger.info("You can train the model by running: python manage.py shell -c 'from myapp.ml.train_model import train_header_classifier; train_header_classifier()'")
                
        except Exception as e:
            logger.error(f"Failed to load ML model: {str(e)}")
            MyappConfig.model = None
