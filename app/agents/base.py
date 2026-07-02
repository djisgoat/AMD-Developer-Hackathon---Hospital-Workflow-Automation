"""Base agent class for all hospital workflow agents.

Every specialised agent inherits from ``BaseAgent`` and only needs to
implement the ``run`` method.  The base class provides:

* A unified way to load the agent-specific prompt.
* Access to the shared LLM via ``get_chat_model()``.
* Utility helpers for structured-output invocation and tool binding.
"""

from abc import ABC, abstractmethod
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import BaseTool

from app.llm.provider import get_chat_model
from app.state.hospital_state import HospitalState
from app.utils.prompt_loader import load_prompt


class BaseAgent(ABC):
    """Abstract base class for every hospital workflow agent.

    Subclasses must set ``name`` and implement ``run(state)``.
    """

    name: str = ""
    """Unique identifier used for routing (must match the LangGraph node name)."""

    tools: list[BaseTool] = []
    """LangChain tools available to this agent (can be overridden per-subclass)."""

    def __init__(self) -> None:
        if not self.name:
            raise ValueError(f"{self.__class__.__name__} must define a non-empty 'name'.")

    # ------------------------------------------------------------------
    # Prompt helpers
    # ------------------------------------------------------------------

    def get_system_prompt(self) -> str:
        """Load the dedicated system prompt for this agent."""
        return load_prompt(self.name)

    # ------------------------------------------------------------------
    # LLM helpers
    # ------------------------------------------------------------------

    def get_llm(self, temperature: float = 0):
        """Return the shared chat model (never instantiate ChatOpenAI directly)."""
        return get_chat_model(temperature=temperature)

    def invoke_llm_structured(self, user_message: str, output_schema, temperature: float = 0):
        """Invoke the LLM and return a validated Pydantic object.

        Args:
            user_message: The context / data to send as the human message.
            output_schema: A Pydantic ``BaseModel`` subclass for structured output.
            temperature: LLM temperature override.

        Returns:
            An instance of ``output_schema`` populated by the LLM.
        """
        llm = self.get_llm(temperature=temperature)
        structured_llm = llm.with_structured_output(output_schema)

        messages = [
            SystemMessage(content=self.get_system_prompt()),
            HumanMessage(content=user_message),
        ]

        return structured_llm.invoke(messages)

    def invoke_llm_with_tools(self, user_message: str, temperature: float = 0):
        """Invoke the LLM with tools bound, returning raw AIMessage.

        The caller is responsible for parsing tool calls from the response
        and executing them.

        Args:
            user_message: The context / data to send as the human message.
            temperature: LLM temperature override.

        Returns:
            An ``AIMessage`` that may contain tool-call requests.
        """
        llm = self.get_llm(temperature=temperature)
        if self.tools:
            llm = llm.bind_tools(self.tools)

        messages = [
            SystemMessage(content=self.get_system_prompt()),
            HumanMessage(content=user_message),
        ]

        return llm.invoke(messages)

    # ------------------------------------------------------------------
    # Main entry point (LangGraph node function)
    # ------------------------------------------------------------------

    @abstractmethod
    def run(self, state: HospitalState) -> dict[str, Any]:
        """Execute the agent's logic and return a state-update dict.

        Each agent should:
        1. Read only the portions of ``state`` it is allowed to access.
        2. Perform reasoning (optionally calling LLM / tools).
        3. Return a dict containing **only** the state keys it owns.

        This method is wrapped and registered as a LangGraph node.
        """
        ...
