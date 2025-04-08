from django.apps import AppConfig


class TelegramBotConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "telegram_bot"

    def ready(self):
        """
        This method is called when Django starts.
        We import the middleware here to avoid circular imports.
        """
        # Import the middleware to ensure it's loaded
        import telegram_bot.middleware