from functools import wraps
import logging

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s — %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logging.getLogger('azure').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

def log_function_use(logger):
    """Decorator that logs method entry, arguments, return value."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"Calling {func.__qualname__}...")
            result = func(*args, **kwargs)
            logger.info(f"{func.__qualname__} executed successfully \n")
            return result
        return wrapper
    return decorator
