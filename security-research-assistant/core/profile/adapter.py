"""Adaptive prompt modification based on learned user preferences."""

from core.logging import get_logger
from core.models.profile import UserProfile
from core.models.query import QueryResponse
from core.profile.tracker import PreferenceTracker

log = get_logger(__name__)


class PromptAdapter:
    """Modify system prompts and suggest queries based on user profile.

    Args:
        tracker: Preference tracker for loading the profile.
    """

    def __init__(self, tracker: PreferenceTracker) -> None:
        self._tracker = tracker

    def adapt_system_prompt(self, base_prompt: str, profile: UserProfile | None = None) -> str:
        """Adapt the system prompt based on learned preferences.

        Adds gentle instructions without dramatically changing the base prompt.

        Args:
            base_prompt: The standard system prompt.
            profile: User profile (loaded if not provided).

        Returns:
            Modified system prompt.
        """
        if profile is None:
            profile = self._tracker.get_profile()

        additions: list[str] = []

        # Detail preference
        if profile.detail_preference > 0.7:
            additions.append(
                "The user prefers detailed, comprehensive responses. Include technical "
                "specifics, relevant context, and thorough explanations."
            )
        elif profile.detail_preference < 0.3:
            additions.append(
                "The user prefers concise, focused responses. Be direct and avoid "
                "unnecessary elaboration. Lead with the key answer."
            )

        # Format preference
        if profile.format_preference == "structured":
            additions.append(
                "The user prefers structured responses with tables, lists, and clear "
                "headings where appropriate."
            )
        elif profile.format_preference == "prose":
            additions.append(
                "The user prefers flowing prose explanations rather than bullet points "
                "and tables."
            )

        # Frequent topics
        if profile.frequent_topics:
            top = ", ".join(profile.frequent_topics[:5])
            additions.append(
                f"The user is currently focused on the following topics: {top}. "
                "When relevant, connect answers to these areas of interest."
            )

        if not additions:
            return base_prompt

        adapted = base_prompt + "\n\nUser preferences:\n" + "\n".join(f"- {a}" for a in additions)
        log.debug("prompt_adapted", additions=len(additions))
        return adapted

    def suggest_related_queries(
        self, profile: UserProfile | None = None, last_response: QueryResponse | None = None,
    ) -> list[str]:
        """Suggest follow-up questions based on profile and last response.

        Args:
            profile: User profile.
            last_response: The most recent query response.

        Returns:
            List of 2-3 suggested query strings.
        """
        if profile is None:
            profile = self._tracker.get_profile()

        suggestions: list[str] = []

        # Combine frequent topics with response content
        topics = profile.frequent_topics[:5]
        response_terms: list[str] = []

        if last_response and last_response.citations:
            response_terms = [c.document_name.split(".")[0] for c in last_response.citations[:3]]

        # Generate suggestions from topic × response term combinations
        if topics and response_terms:
            for topic in topics[:2]:
                for term in response_terms[:1]:
                    suggestions.append(f"What {topic} capabilities does the {term} have?")
            if len(suggestions) < 3 and topics:
                suggestions.append(f"Are there any known vulnerabilities related to {topics[0]}?")
        elif topics:
            suggestions.append(f"What components use {topics[0]}?")
            if len(topics) > 1:
                suggestions.append(f"How do {topics[0]} and {topics[1]} interact in this system?")
            suggestions.append("What are the main security concerns for this product?")
        else:
            # Default suggestions for new users
            suggestions = [
                "What is the main processor in this system?",
                "What communication interfaces are used?",
                "What are the known security concerns?",
            ]

        return suggestions[:3]
