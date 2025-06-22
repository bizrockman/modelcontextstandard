from __future__ import annotations

"""MCS core driver interface.

A driver encapsulates two mandatory responsibilities:
1. **get_function_description** – fetch a machine‑readable function spec
2. **process_llm_response** – execute a structured call emitted by the LLM

Implementations can use any transport (HTTP, CAN‑Bus, AS2, …) and any
specification format (OpenAPI, JSON‑Schema, proprietary JSON). The interface
keeps the integration surface minimal and self‑contained.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class MCSDriver(ABC):
    """Minimal contract every driver must fulfil."""

    @abstractmethod
    def get_function_description(self) -> str:  # noqa: D401
        """Return the spec for *source* as raw string."""

    @abstractmethod
    def get_driver_system_message(self) -> str:  # noqa: D401
        """Return the prompt for tool use as raw string."""

    @abstractmethod
    def process_llm_response(self, llm_response: str) -> Any:  # noqa: D401
        """Execute the structured call and return the raw result."""
