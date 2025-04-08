import threading
import logging
from django.core.exceptions import MiddlewareNotUsed
from .bot import start_bot

logger = logging.getLogger(__name__)

class TelegramBotMiddleware:
    """Middleware to start the Telegram bot when Django starts."""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Start the bot in a separate thread
        bot_thread = threading.Thread(target=start_bot)
        bot_thread.daemon = True  # This ensures the thread will exit when the main program exits
        bot_thread.start()
        
        # Raise MiddlewareNotUsed to ensure this middleware runs only once
        raise MiddlewareNotUsed('TelegramBotMiddleware is no longer needed')