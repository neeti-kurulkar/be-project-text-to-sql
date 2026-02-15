"""
Base agent class with common functionality for all agents.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import time
from app.config import settings
from app.retrieval import VectorStore
from app.langgraph.state import QueryState


def _create_llm():
    """Create the LLM client based on LLM_PROVIDER (gemini, groq, openai)."""
    provider = (settings.LLM_PROVIDER or "gemini").strip().lower()

    if provider == "gemini":
        api_key = (settings.GEMINI_API_KEY or "").strip()
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is required when LLM_PROVIDER=gemini. "
                "Set GEMINI_API_KEY in .env (get a key at https://aistudio.google.com/apikey)."
            )
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            google_api_key=api_key,
        )

    if provider == "groq":
        api_key = (settings.GROQ_API_KEY or "").strip()
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is required when LLM_PROVIDER=groq. "
                "Set GROQ_API_KEY in .env (get a key at https://console.groq.com)."
            )
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            api_key=api_key,
            base_url=settings.OPENAI_BASE_URL or "https://api.groq.com/openai/v1",
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
        )

    # openai or fallback
    api_key = (settings.OPENAI_API_KEY or "").strip()
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is required when LLM_PROVIDER=openai. "
            "Set OPENAI_API_KEY in .env or use Gemini (LLM_PROVIDER=gemini) with GEMINI_API_KEY."
        )
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        api_key=api_key,
        base_url=settings.OPENAI_BASE_URL or None,
        model=settings.LLM_MODEL,
        temperature=settings.LLM_TEMPERATURE,
    )


class BaseAgent(ABC):
    """Abstract base class for all agents in the NL2SQL pipeline."""

    def __init__(self):
        """Initialize the agent with LLM and vector store."""
        self.llm = _create_llm()
        self.vector_store = VectorStore()
        self.agent_name = self.__class__.__name__

    @abstractmethod
    def execute(self, state: QueryState) -> QueryState:
        """
        Execute the agent's task.

        Args:
            state: Current pipeline state

        Returns:
            Updated pipeline state
        """
        pass

    def retrieve_examples(
        self,
        query: str,
        collection_name: str,
        k: int
    ) -> List[Dict[str, Any]]:
        """
        Retrieve similar examples from ChromaDB.

        Args:
            query: Query text for semantic search
            collection_name: Name of the collection to search
            k: Number of examples to retrieve

        Returns:
            List of examples with question, metadata, and distance
        """
        return self.vector_store.query(
            collection_name=collection_name,
            query_text=query,
            n_results=k
        )

    def log_trace(
        self,
        state: QueryState,
        duration: float,
        status: str,
        details: Dict[str, Any] = None
    ) -> None:
        """
        Log agent execution to the state trace.

        Args:
            state: Current pipeline state
            duration: Execution time in seconds
            status: Status string (success, error, skipped)
            details: Optional additional details
        """
        if "agent_trace" not in state:
            state["agent_trace"] = []

        state["agent_trace"].append({
            "agent": self.agent_name,
            "duration": round(duration, 3),
            "status": status,
            "details": details
        })

    def call_llm(self, prompt: str, max_retries: int = 2) -> str:
        """
        Call the LLM with a prompt, with retry logic for rate limits.

        Args:
            prompt: The prompt to send to the LLM
            max_retries: Maximum number of retries on rate limit

        Returns:
            The LLM's response as a string
        """
        import time as time_module

        last_error = None
        for attempt in range(max_retries + 1):
            try:
                response = self.llm.invoke(prompt)
                content = getattr(response, "content", response)
                # Gemini/LangChain can return content as a list of blocks (e.g. [{"type": "text", "text": "..."}])
                if isinstance(content, list):
                    parts = []
                    for block in content:
                        text = None
                        if isinstance(block, dict):
                            text = block.get("text") or block.get("content")
                            if text is None and block.get("parts"):
                                p0 = block["parts"][0]
                                text = p0.get("text") or p0.get("content") if isinstance(p0, dict) else None
                        elif hasattr(block, "text"):
                            text = getattr(block, "text", None)
                        elif hasattr(block, "content"):
                            text = getattr(block, "content", None)
                        else:
                            text = str(block) if block else None
                        if text:
                            parts.append(str(text))
                    return "\n".join(parts) if parts else ""
                if content is None:
                    return ""
                return content if isinstance(content, str) else str(content)
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "rate_limit" in error_str.lower():
                    last_error = e
                    if attempt < max_retries:
                        # Wait before retry (exponential backoff)
                        wait_time = (attempt + 1) * 2  # 2s, 4s
                        print(f"[{self.agent_name}] Rate limited, waiting {wait_time}s before retry...")
                        time_module.sleep(wait_time)
                        continue
                raise e

        raise last_error

    def format_examples_for_prompt(
        self,
        examples: List[Dict[str, Any]],
        include_sql: bool = False,
        include_intent: bool = False,
        include_schema: bool = False
    ) -> str:
        """
        Format retrieved examples for inclusion in prompts.

        Args:
            examples: List of examples from retrieval
            include_sql: Include SQL in output
            include_intent: Include intent in output
            include_schema: Include schema in output

        Returns:
            Formatted string with examples
        """
        if not examples:
            return ""

        lines = []
        for i, ex in enumerate(examples, 1):
            lines.append(f"Example {i}:")
            lines.append(f"  Question: {ex['question']}")

            metadata = ex.get("metadata", {})

            if include_intent and "intent" in metadata:
                intent = metadata["intent"]
                if isinstance(intent, dict):
                    lines.append(f"  Intent: {intent}")

            if include_schema and "schema" in metadata:
                schema = metadata["schema"]
                if isinstance(schema, dict):
                    lines.append(f"  Schema: {schema}")

            if include_sql and "sql" in metadata:
                lines.append(f"  SQL: {metadata['sql']}")

            if "explanation" in metadata:
                lines.append(f"  Explanation: {metadata['explanation']}")

            lines.append("")

        return "\n".join(lines)
