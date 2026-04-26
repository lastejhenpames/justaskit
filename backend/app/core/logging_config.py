import logging
import sys
from pythonjsonlogger import jsonlogger
from contextvars import ContextVar
from app.core.config import settings

# Context variable for request ID
request_id_var: ContextVar[str] = ContextVar('request_id', default='')

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter that includes request_id from context
    """
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        
        # Add request_id if available
        request_id = request_id_var.get('')
        if request_id:
            log_record['request_id'] = request_id
        
        # Add standard fields
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        log_record['timestamp'] = self.formatTime(record, self.datefmt)

def setup_logging():
    """
    Configure structured logging for the application
    """
    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    
    # Use JSON formatter for production, simple format for development
    if settings.ENVIRONMENT == "production":
        formatter = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    root_logger.addHandler(handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    
    return root_logger

def get_request_id() -> str:
    """Get current request ID from context"""
    return request_id_var.get('')

def set_request_id(request_id: str):
    """Set request ID in context"""
    request_id_var.set(request_id)
