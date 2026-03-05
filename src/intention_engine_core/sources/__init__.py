"""Source adapter package for Intention Engine discovery."""

from .base import SourceAdapter, SourceCandidate, SourceFetchResult
from .registry import get_source_adapter, supported_source_types

__all__ = [
    "SourceAdapter",
    "SourceCandidate",
    "SourceFetchResult",
    "get_source_adapter",
    "supported_source_types",
]
