#!/usr/bin/env python3
"""Tests for specialized extractors."""

import pytest
from loguru import logger
from terraform_doc_extractor import (
    TerraformURL,
    ExampleUsageExtractor,
    ArgumentReferenceExtractor
)

# Disable logging for tests
logger.disable("terraform_doc_extractor")


class TestExampleUsageExtractor:
    """Test ExampleUsageExtractor."""
    
    @pytest.fixture
    def extractor(self):
        """Create an ExampleUsageExtractor instance."""
        return ExampleUsageExtractor()
    
    def test_single_example_section(self, extractor):
        """Test extraction of single example usage section."""
        url = TerraformURL.parse("hashicorp/aws/5.100.0/docs/resources/lb")
        markdown = extractor.extract(url)
        
        assert markdown is not None
        assert "# Example Usage: lb" in markdown
        assert "```hcl" in markdown
    
    def test_multiple_example_sections(self, extractor):
        """Test handling of multiple example usage sections."""
        # Note: This test uses the facade instead of direct extractor
        # because direct extractor without pre-fetched HTML may not work
        # in standalone mode. Use TerraformResourceDocs for better reliability.
        from terraform_doc_extractor import TerraformResourceDocs
        
        facade = TerraformResourceDocs()
        markdown = facade.extract_examples("hashicorp/google/latest/docs/resources/bigquery_dataset")
        
        if markdown is None:
            pytest.skip("Could not fetch documentation (network issue or page not found)")
        
        assert "# Example Usage: bigquery_dataset" in markdown
        # Check for subsections (should be ##)
        assert "\n## " in markdown
        # Should have multiple subsections
        assert markdown.count("\n## ") >= 2
    
    def test_custom_heading_level(self, extractor):
        """Test custom heading level."""
        url = TerraformURL.parse("hashicorp/aws/5.100.0/docs/resources/lb")
        markdown = extractor.extract(url, heading_level=2)
        
        assert markdown is not None
        assert markdown.startswith("## Example Usage:")
    
    def test_code_blocks_formatted(self, extractor):
        """Test that code blocks are properly formatted."""
        url = TerraformURL.parse("hashicorp/aws/5.100.0/docs/resources/lb")
        markdown = extractor.extract(url)
        
        # Check for HCL code blocks
        assert "```hcl" in markdown
        # Ensure code blocks are closed
        assert markdown.count("```hcl") <= markdown.count("```") // 2
    
    def test_no_metadata(self, extractor):
        """Test that Provider/Version/Resource metadata is not included."""
        url = TerraformURL.parse("hashicorp/aws/5.100.0/docs/resources/lb")
        markdown = extractor.extract(url)
        
        assert "**Provider:**" not in markdown
        assert "**Version:**" not in markdown


class TestArgumentReferenceExtractor:
    """Test ArgumentReferenceExtractor."""
    
    @pytest.fixture
    def extractor(self):
        """Create an ArgumentReferenceExtractor instance."""
        return ArgumentReferenceExtractor()
    
    def test_argument_extraction(self, extractor):
        """Test basic argument reference extraction."""
        url = TerraformURL.parse("hashicorp/aws/5.100.0/docs/resources/lb")
        markdown = extractor.extract(url)
        
        assert markdown is not None
        assert "# Argument Reference: lb" in markdown
        # Check for formatted arguments
        assert "**`" in markdown
        assert "`**" in markdown
    
    def test_custom_heading_level(self, extractor):
        """Test custom heading level."""
        url = TerraformURL.parse("hashicorp/aws/5.100.0/docs/resources/lb")
        markdown = extractor.extract(url, heading_level=3)
        
        assert markdown is not None
        assert markdown.startswith("### Argument Reference:")
    
    def test_nested_arguments(self, extractor):
        """Test that nested arguments are properly formatted."""
        url = TerraformURL.parse("hashicorp/aws/5.100.0/docs/resources/lb")
        markdown = extractor.extract(url)
        
        # Should have indented arguments (nested blocks)
        lines = markdown.split('\n')
        indented_args = [line for line in lines if line.startswith('  - **`')]
        assert len(indented_args) > 0
    
    def test_no_metadata(self, extractor):
        """Test that Provider/Version/Resource metadata is not included."""
        url = TerraformURL.parse("hashicorp/aws/5.100.0/docs/resources/lb")
        markdown = extractor.extract(url)
        
        assert "**Provider:**" not in markdown
        assert "**Version:**" not in markdown


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

