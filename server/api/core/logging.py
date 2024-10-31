# server/api/core/logging.py
import logging
import logging.handlers
import os
from datetime import datetime
from typing import Optional, Dict, Any
from flask import Flask, request
import json
import traceback

class CustomFormatter(logging.Formatter):
    """Custom formatter that outputs logs in JSON format"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data: Dict[str, Any] = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }

        # Add request information if available
        if request:
            log_data.update({
                'request_id': request.headers.get('X-Request-ID'),
                'ip': request.remote_addr,
                'method': request.method,
                'path': request.path,
                'user_agent': request.user_agent.string if request.user_agent else None
            })

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'stack_trace': traceback.format_exception(*record.exc_info)
            }

        # Add extra fields
        if hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)

        return json.dumps(log_data)

def setup_logging(app: Flask, log_level: Optional[str] = None) -> None:
    """Configure application logging
    
    Args:
        app: Flask application instance
        log_level: Optional override for log level
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # Set up formatter
    formatter = CustomFormatter()

    # File handler for all logs
    file_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(log_dir, 'app.log'),
        maxBytes=10485760,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)

    # Error file handler
    error_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(log_dir, 'error.log'),
        maxBytes=10485760,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)

    # Console handler with colored output
    class ColoredConsoleHandler(logging.StreamHandler):
        """Console handler with colored output"""
        
        colors = {
            'DEBUG': '\033[94m',    # Blue
            'INFO': '\033[92m',     # Green
            'WARNING': '\033[93m',  # Yellow
            'ERROR': '\033[91m',    # Red
            'CRITICAL': '\033[91m'  # Red
        }
        reset = '\033[0m'

        def emit(self, record):
            try:
                message = self.format(record)
                color = self.colors.get(record.levelname, '')
                stream = self.stream
                stream.write(f'{color}{message}{self.reset}\n')
                self.flush()
            except Exception:
                self.handleError(record)

    console_handler = ColoredConsoleHandler()
    console_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level or app.config.get('LOG_LEVEL', 'INFO'))

    # Remove existing handlers
    root_logger.handlers = []

    # Add our handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)

    # Set up request logging
    @app.before_request
    def log_request_info():
        app.logger.info('Request started', extra={
            'extra_fields': {
                'method': request.method,
                'path': request.path,
                'ip': request.remote_addr,
                'user_agent': request.user_agent.string if request.user_agent else None,
                'request_id': request.headers.get('X-Request-ID')
            }
        })

    @app.after_request
    def log_response_info(response):
        app.logger.info('Request finished', extra={
            'extra_fields': {
                'method': request.method,
                'path': request.path,
                'status': response.status_code,
                'size': len(response.get_data()),
                'request_id': request.headers.get('X-Request-ID'),
                'duration': request.elapsed_time if hasattr(request, 'elapsed_time') else None
            }
        })
        return response

    # Log unhandled exceptions
    @app.errorhandler(Exception)
    def log_exception(error):
        app.logger.exception('Unhandled exception', extra={
            'extra_fields': {
                'request_id': request.headers.get('X-Request-ID'),
                'error_type': type(error).__name__
            }
        })
        return 'Internal Server Error', 500

    # Test logging setup
    app.logger.info('Logging setup completed', extra={
        'extra_fields': {
            'log_level': root_logger.level,
            'handlers': [type(h).__name__ for h in root_logger.handlers]
        }
    })