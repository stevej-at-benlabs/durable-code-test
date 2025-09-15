"""
Example file demonstrating Interface Segregation Principle violation.
This file is for testing the ISP checker and will be removed.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


# BAD: Fat interface violating ISP
class DataOperations(ABC):
    """Interface that forces implementations to handle too many unrelated operations."""

    @abstractmethod
    def read_from_database(self, query: str) -> List[Dict]:
        """Read data from database."""
        pass

    @abstractmethod
    def write_to_database(self, data: Dict) -> bool:
        """Write data to database."""
        pass

    @abstractmethod
    def read_from_file(self, filepath: str) -> str:
        """Read data from file."""
        pass

    @abstractmethod
    def write_to_file(self, filepath: str, data: str) -> bool:
        """Write data to file."""
        pass

    @abstractmethod
    def send_email(self, to: str, subject: str, body: str) -> bool:
        """Send email notification."""
        pass

    @abstractmethod
    def log_error(self, error: str) -> None:
        """Log error message."""
        pass

    @abstractmethod
    def validate_data(self, data: Any) -> bool:
        """Validate data."""
        pass

    @abstractmethod
    def transform_data(self, data: Any) -> Any:
        """Transform data."""
        pass


# VIOLATION: Class forced to implement methods it doesn't use
class FileHandler(DataOperations):
    """Only needs file operations but forced to implement all methods."""

    def read_from_file(self, filepath: str) -> str:
        with open(filepath, 'r') as f:
            return f.read()

    def write_to_file(self, filepath: str, data: str) -> bool:
        with open(filepath, 'w') as f:
            f.write(data)
        return True

    # Forced to implement unused methods
    def read_from_database(self, query: str) -> List[Dict]:
        raise NotImplementedError("FileHandler doesn't support database operations")

    def write_to_database(self, data: Dict) -> bool:
        raise NotImplementedError("FileHandler doesn't support database operations")

    def send_email(self, to: str, subject: str, body: str) -> bool:
        raise NotImplementedError("FileHandler doesn't send emails")

    def log_error(self, error: str) -> None:
        # Forced to implement but doesn't really need this
        pass

    def validate_data(self, data: Any) -> bool:
        # Forced to implement
        return True

    def transform_data(self, data: Any) -> Any:
        # Forced to implement
        return data


# GOOD: Following ISP with segregated interfaces
class FileOperations(ABC):
    """Focused interface for file operations only."""

    @abstractmethod
    def read(self, filepath: str) -> str:
        pass

    @abstractmethod
    def write(self, filepath: str, data: str) -> bool:
        pass


class DatabaseOperations(ABC):
    """Focused interface for database operations only."""

    @abstractmethod
    def query(self, query: str) -> List[Dict]:
        pass

    @abstractmethod
    def insert(self, data: Dict) -> bool:
        pass


class NotificationService(ABC):
    """Focused interface for notifications."""

    @abstractmethod
    def send_email(self, to: str, subject: str, body: str) -> bool:
        pass


# Good implementation following ISP
class SimpleFileHandler(FileOperations):
    """Only implements what it needs."""

    def read(self, filepath: str) -> str:
        with open(filepath, 'r') as f:
            return f.read()

    def write(self, filepath: str, data: str) -> bool:
        with open(filepath, 'w') as f:
            f.write(data)
        return True
