"""
Google Antigravity Schema Extraction and Validation Suite.
"""

from .registry import registry, SchemaRegistry, SchemaDescriptor
from .doc_inspector import DocSyncInspector, DocSection, SchemaSyncResult

__version__ = "0.2.0"

__all__ = [
    "registry",
    "SchemaRegistry",
    "SchemaDescriptor",
    "DocSyncInspector",
    "DocSection",
    "SchemaSyncResult",
    "__version__",
]


