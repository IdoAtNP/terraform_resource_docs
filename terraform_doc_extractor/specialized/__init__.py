"""Specialized extractors for Terraform documentation."""

from .example_usage_extractor import ExampleUsageExtractor
from .argument_reference_extractor import ArgumentReferenceExtractor
from .terraform_resource_docs import TerraformResourceDocs

__all__ = [
    "ExampleUsageExtractor",
    "ArgumentReferenceExtractor",
    "TerraformResourceDocs"
]

