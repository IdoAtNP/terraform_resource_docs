#!/usr/bin/env python3
"""Tests for URL parsing functionality."""

import pytest
from terraform_doc_extractor import TerraformURL


class TestURLParsing:
    """Test URL parsing and validation."""
    
    def test_parse_full_url(self):
        """Test parsing a full URL."""
        url = TerraformURL.parse("https://registry.terraform.io/providers/hashicorp/aws/5.100.0/docs/resources/lb")
        assert url is not None
        assert url.namespace == "hashicorp"
        assert url.provider == "aws"
        assert url.version == "5.100.0"
        assert url.resource == "lb"
    
    def test_parse_short_path(self):
        """Test parsing a short path."""
        url = TerraformURL.parse("hashicorp/aws/5.100.0/docs/resources/lb")
        assert url is not None
        assert url.namespace == "hashicorp"
        assert url.provider == "aws"
        assert url.version == "5.100.0"
        assert url.resource == "lb"
    
    def test_parse_latest_version(self):
        """Test parsing with 'latest' version."""
        url = TerraformURL.parse("hashicorp/google/latest/docs/resources/bigquery_dataset")
        assert url is not None
        assert url.version == "latest"
        assert url.resource == "bigquery_dataset"
    
    def test_parse_databricks_provider(self):
        """Test parsing Databricks provider URL."""
        url = TerraformURL.parse("databricks/databricks/latest/docs/resources/database_database_catalog")
        assert url is not None
        assert url.namespace == "databricks"
        assert url.provider == "databricks"
        assert url.version == "latest"
    
    def test_invalid_url(self):
        """Test that invalid URLs return None."""
        url = TerraformURL.parse("invalid/url")
        assert url is None
    
    def test_empty_string(self):
        """Test that empty string returns None."""
        url = TerraformURL.parse("")
        assert url is None
    
    def test_url_reconstruction(self):
        """Test that parsed URL can be reconstructed."""
        original = "hashicorp/aws/5.100.0/docs/resources/lb"
        url = TerraformURL.parse(original)
        assert url is not None
        assert url.url == f"https://registry.terraform.io/providers/{original}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

