"""
Custom exceptions for the YouTube report workflow.
"""
from typing import Optional


class YouTubeWorkflowError(Exception):
    """Base exception for YouTube workflow errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, cause: Optional[Exception] = None):
        self.message = message
        self.error_code = error_code
        self.cause = cause
        super().__init__(self.message)


class YouTubeAPIError(YouTubeWorkflowError):
    """Exception raised when YouTube API operations fail."""
    pass


class AudioProcessingError(YouTubeWorkflowError):
    """Exception raised when audio processing fails."""
    pass


class OpenAIAPIError(YouTubeWorkflowError):
    """Exception raised when OpenAI API operations fail."""
    pass


class DatabaseError(YouTubeWorkflowError):
    """Exception raised when database operations fail."""
    pass


class VideoNotFoundError(YouTubeWorkflowError):
    """Exception raised when no video is found for the given criteria."""
    pass


class ContentExtractionError(YouTubeWorkflowError):
    """Exception raised when content extraction (subtitle/audio) fails."""
    pass