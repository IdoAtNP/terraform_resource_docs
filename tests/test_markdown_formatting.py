#!/usr/bin/env python3
"""Tests for markdown formatting quality."""

import pytest
from loguru import logger
from terraform_doc_extractor import TerraformResourceDocs

# Disable logging for tests
logger.disable("terraform_doc_extractor")


class TestMarkdownFormatting:
    """Test markdown formatting quality."""
    
    @pytest.fixture
    def facade(self):
        """Create a TerraformResourceDocs instance."""
        return TerraformResourceDocs()
    
    def test_code_blocks_formatted(self, facade):
        """Test that code blocks are properly formatted."""
        examples = facade.extract_examples("hashicorp/aws/5.100.0/docs/resources/lb")
        
        # Check for HCL code blocks
        assert "```hcl" in examples
        # Verify blocks are properly closed
        hcl_count = examples.count("```hcl")
        close_count = examples.count("```") - hcl_count  # Total ``` minus opening ```hcl
        assert hcl_count == close_count
    
    def test_arguments_formatted(self, facade):
        """Test that arguments are properly formatted."""
        arguments = facade.extract_arguments("hashicorp/aws/5.100.0/docs/resources/lb")
        
        # Check for bold code-formatted arguments
        assert "**`" in arguments
        assert "`**" in arguments
        
        # Count opening and closing
        assert arguments.count("**`") == arguments.count("`**")
    
    def test_heading_hierarchy(self, facade):
        """Test that heading hierarchy is maintained."""
        examples = facade.extract_examples(
            "hashicorp/google/latest/docs/resources/bigquery_dataset",
            heading_level=1
        )
        
        # Main heading should be #
        assert examples.startswith("# Example Usage:")
        # Subsections should be ##
        assert "\n## " in examples
        # Should not have ### at heading_level=1
        assert "\n### " not in examples
    
    def test_heading_hierarchy_level_2(self, facade):
        """Test heading hierarchy with custom level."""
        examples = facade.extract_examples(
            "hashicorp/google/latest/docs/resources/bigquery_dataset",
            heading_level=2
        )
        
        # Main heading should be ##
        assert examples.startswith("## Example Usage:")
        # Subsections should be ###
        assert "\n### " in examples
    
    def test_no_trailing_whitespace(self, facade):
        """Test that there's no excessive trailing whitespace."""
        examples = facade.extract_examples("hashicorp/aws/5.100.0/docs/resources/lb")
        
        # Should not end with multiple newlines
        assert not examples.endswith("\n\n\n")
    
    def test_no_metadata_in_output(self, facade):
        """Test that Provider/Version/Resource metadata is not included."""
        examples = facade.extract_examples("hashicorp/aws/5.100.0/docs/resources/lb")
        arguments = facade.extract_arguments("hashicorp/aws/5.100.0/docs/resources/lb")
        
        # Check examples
        assert "**Provider:**" not in examples
        assert "**Version:**" not in examples
        
        # Check arguments
        assert "**Provider:**" not in arguments
        assert "**Version:**" not in arguments
    
    def test_list_formatting(self, facade):
        """Test that lists are properly formatted."""
        arguments = facade.extract_arguments("hashicorp/aws/5.100.0/docs/resources/lb")
        
        # Should have bullet points for arguments
        assert "\n- " in arguments or "\n  - " in arguments
    
    def test_no_html_tags(self, facade):
        """Test that HTML tags are not present in text output."""
        examples = facade.extract_examples("hashicorp/aws/5.100.0/docs/resources/lb")
        
        # Should not contain common HTML tags
        assert "<div" not in examples
        assert "<span" not in examples
        assert "<p>" not in examples
        assert "</p>" not in examples


class TestMultipleExamplesFormatting:
    """Test formatting of resources with multiple example sections."""
    
    @pytest.fixture
    def facade(self):
        """Create a TerraformResourceDocs instance."""
        return TerraformResourceDocs()
    
    def test_multiple_sections_structure(self, facade):
        """Test that multiple sections are properly structured."""
        examples = facade.extract_examples(
            "hashicorp/google/latest/docs/resources/bigquery_dataset"
        )
        
        # Should have main heading
        assert "# Example Usage: bigquery_dataset" in examples
        # Should have multiple subsections
        subsection_count = examples.count("\n## ")
        assert subsection_count >= 2
    
    def test_subsection_names(self, facade):
        """Test that subsection names are properly extracted."""
        examples = facade.extract_examples(
            "hashicorp/google/latest/docs/resources/bigquery_dataset"
        )
        
        # Should have recognizable subsection names
        lines = examples.split('\n')
        subsections = [line[3:].strip() for line in lines if line.startswith("## ")]
        
        assert len(subsections) > 0
        # Subsection names should not be empty
        for subsection in subsections:
            assert len(subsection) > 0
            # Should not start with "Example Usage" (that's the main heading)
            assert not subsection.startswith("Example Usage:")
    
    def test_each_subsection_has_content(self, facade):
        """Test that each subsection has content."""
        examples = facade.extract_examples(
            "hashicorp/google/latest/docs/resources/bigquery_dataset"
        )
        
        # Split by subsections
        sections = examples.split("\n## ")
        
        # Each section should have substantial content
        for section in sections[1:]:  # Skip the header
            assert len(section) > 100  # Should have more than just a title


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

