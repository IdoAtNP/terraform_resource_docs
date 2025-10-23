"""Generic Terraform documentation extractor components."""

from .extractor import TerraformDocExtractor
from .url_parser import TerraformURL
from .fetcher import PageFetcher
from .parser import DocumentationParser

__all__ = [
    "TerraformDocExtractor",
    "TerraformURL",
    "PageFetcher",
    "DocumentationParser"
]

