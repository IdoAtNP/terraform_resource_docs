"""
Terraform Resource Documentation Extractor

A Python package to extract sections from Terraform provider documentation.

Package Structure:
- generic: Core extraction components (fetcher, parser, generic extractor)
- specialized: Domain-specific extractors and facade
"""

# Generic components
from .generic import (
    TerraformDocExtractor,
    TerraformURL,
    PageFetcher,
    DocumentationParser
)

# Specialized components
from .specialized import (
    ExampleUsageExtractor,
    ArgumentReferenceExtractor,
    TerraformResourceDocs
)

__version__ = "0.1.0"
__all__ = [
    # Generic
    "TerraformDocExtractor",
    "TerraformURL",
    "PageFetcher",
    "DocumentationParser",
    # Specialized
    "ExampleUsageExtractor",
    "ArgumentReferenceExtractor",
    "TerraformResourceDocs"
]

