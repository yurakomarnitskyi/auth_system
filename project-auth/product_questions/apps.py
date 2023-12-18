from django.apps import AppConfig


class ProductQuestionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'product_questions'

    def ready(self):
        import product_questions.signals
