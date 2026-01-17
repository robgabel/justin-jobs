from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.utils.claude_client import ClaudeClient


class BaseAgent(ABC):
    """Base class for all AI agents."""

    def __init__(self):
        self.claude = ClaudeClient()
        self.conversation_history = []

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's task.

        Args:
            input_data: Input parameters for the agent

        Returns:
            Dict containing the agent's output
        """
        pass

    def reset_conversation(self):
        """Reset the conversation history."""
        self.conversation_history = []

    def add_to_conversation(self, role: str, content: str):
        """Add a message to the conversation history."""
        self.conversation_history.append({"role": role, "content": content})

    async def generate_response(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 4096,
    ) -> str:
        """Generate a text response using Claude."""
        return await self.claude.generate_text(
            prompt=prompt, system=system, max_tokens=max_tokens
        )

    async def continue_conversation(
        self,
        user_message: str,
        system: Optional[str] = None,
        max_tokens: int = 4096,
    ) -> str:
        """Continue a multi-turn conversation."""
        self.add_to_conversation("user", user_message)

        response = await self.claude.continue_conversation(
            messages=self.conversation_history,
            system=system,
            max_tokens=max_tokens,
        )

        # Extract text from response
        text_content = ""
        for content_block in response["content"]:
            if hasattr(content_block, "text"):
                text_content += content_block.text

        self.add_to_conversation("assistant", text_content)
        return text_content
