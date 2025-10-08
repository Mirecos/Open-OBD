import logging
from datetime import datetime
from typing import Optional


class Logger:
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.log_level = logging.DEBUG
    
    def _format_message(self, level: str, content: str) -> str:
        """Format message with timestamp and service name"""
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        return f"[{timestamp}][{self.service_name}][{level}] : {content}"
    
    def debug(self, content: str):
        """Log debug message"""
        print(self._format_message("DEBUG", content))
    
    def info(self, content: str):
        """Log info message"""
        print(self._format_message("INFO", content))
    
    def warning(self, content: str):
        """Log warning message"""
        print(self._format_message("WARNING", content))
    
    def error(self, content: str):
        """Log error message"""
        print(self._format_message("ERROR", content))
    
    def critical(self, content: str):
        """Log critical message"""
        print(self._format_message("CRITICAL", content))

