#!/usr/bin/env python3
"""Tests for the generic TerraformDocExtractor."""

import pytest
from loguru import logger
from terraform_doc_extractor import TerraformDocExtractor

# Disable logging for tests
logger.disable("terraform_doc_extractor")


class TestGenericExtractor:
    """Test the generic TerraformDocExtractor."""
    
    @pytest.fixture
    def extractor(self):
        """Create a generic extractor instance."""
        return TerraformDocExtractor()
    
    def test_list_available_sections(self, extractor):
        """Test listing available sections."""
        sections = extractor.list_available_sections("hashicorp/aws/5.100.0/docs/resources/lb")
        assert isinstance(sections, list)
        assert len(sections) > 0
        assert "Example Usage" in sections
        assert "Argument Reference" in sections
    
    def test_extract_single_section(self, extractor):
        """Test extracting a single section."""
        result = extractor.extract_sections(
            "hashicorp/aws/5.100.0/docs/resources/lb",
            ["Example Usage"],
            as_text=True
        )
        assert "Example Usage" in result
        assert result["Example Usage"] is not None
        assert len(result["Example Usage"]) > 0
    
    def test_extract_multiple_sections(self, extractor):
        """Test extracting multiple sections."""
        result = extractor.extract_sections(
            "hashicorp/aws/5.100.0/docs/resources/lb",
            ["Example Usage", "Argument Reference"],
            as_text=True
        )
        assert len(result) == 2
        assert "Example Usage" in result
        assert "Argument Reference" in result
        assert result["Example Usage"] is not None
        assert result["Argument Reference"] is not None
    
    def test_extract_as_html(self, extractor):
        """Test extracting sections as HTML."""
        result = extractor.extract_sections(
            "hashicorp/aws/5.100.0/docs/resources/lb",
            ["Example Usage"],
            as_text=False
        )
        assert "Example Usage" in result
        assert result["Example Usage"] is not None
        # HTML should contain tags
        assert "<" in result["Example Usage"]
        assert ">" in result["Example Usage"]
    
    def test_extract_all_sections(self, extractor):
        """Test extracting all available sections."""
        result = extractor.extract_sections(
            "hashicorp/aws/5.100.0/docs/resources/lb",
            as_text=True
        )
        assert len(result) > 0
        assert "Example Usage" in result
        assert "Argument Reference" in result
    
    def test_extract_nonexistent_section(self, extractor):
        """Test extracting a section that doesn't exist."""
        result = extractor.extract_sections(
            "hashicorp/aws/5.100.0/docs/resources/lb",
            ["Nonexistent Section"],
            as_text=True
        )
        assert "Nonexistent Section" in result
        assert result["Nonexistent Section"] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

