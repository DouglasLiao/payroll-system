from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseEmailProvider(ABC):
    """Abstract base class for email providers"""

    @abstractmethod
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str = None,
        from_email: str = None,
        from_name: str = None,
    ) -> Dict[str, Any]:
        """
        Send an email

        Returns:
            Dict with 'success', 'message_id', and optionally 'error'
        """
        pass

    @abstractmethod
    async def check_connection(self) -> bool:
        """Check if provider connection is working"""
        pass
