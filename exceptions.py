class ChatAppException(Exception):
  """Base exception class for the chat application"""
  pass

class UserNotFoundException(ChatAppException):
  """Raised when a user is not found"""
  pass

class UnauthorizedAccessException(ChatAppException):
  """Raised when a user attempts unauthorized access"""
  pass

class MessageNotFoundException(ChatAppException):
  """Raised when a message is not found"""
  pass

class ValidationError(ChatAppException):
  """Raised when input validation fails"""
  pass