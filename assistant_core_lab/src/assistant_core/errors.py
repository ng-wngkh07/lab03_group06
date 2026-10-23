"""Named application errors used across the service modules."""


class AssistantError(Exception):
    """Base class for all assistant errors."""


class ConfigError(AssistantError):
    """Configuration is missing or invalid."""


class DataError(AssistantError):
    """A required knowledge file is missing or malformed."""


class ValidationError(AssistantError, ValueError):
    """The user's request or a domain value is invalid."""


class InvalidRequest(ValidationError):
    """The request cannot be answered as given."""


class ProviderError(AssistantError):
    """The AI provider failed, timed out, or returned an unusable response."""
