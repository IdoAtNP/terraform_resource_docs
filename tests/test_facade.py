#!/usr/bin/env python3
"""Tests for TerraformResourceDocs facade."""

import pytest
from loguru import logger
from terraform_doc_extractor import TerraformResourceDocs

# Disable logging for tests
logger.disable("terraform_doc_extractor")


class TestFacadeBasics:
    """Test basic facade operations."""
    
    @pytest.fixture
    def facade(self):
        """Create a TerraformResourceDocs instance."""
        return TerraformResourceDocs()
    
    def test_extract_all(self, facade):
        """Test extracting both sections at once."""
        docs = facade.extract_all("hashicorp/aws/5.100.0/docs/resources/lb")
        
        assert 'examples' in docs
        assert 'arguments' in docs
        assert docs['examples'] is not None
        assert docs['arguments'] is not None
        assert len(docs['examples']) > 0
        assert len(docs['arguments']) > 0
    
    def test_extract_examples_only(self, facade):
        """Test extracting only examples."""
        examples = facade.extract_examples("hashicorp/aws/5.100.0/docs/resources/lb")
        
        assert examples is not None
        assert "# Example Usage: lb" in examples
        assert len(examples) > 0
    
    def test_extract_arguments_only(self, facade):
        """Test extracting only arguments."""
        arguments = facade.extract_arguments("hashicorp/aws/5.100.0/docs/resources/lb")
        
        assert arguments is not None
        assert "# Argument Reference: lb" in arguments
        assert len(arguments) > 0
    
    def test_extract_with_custom_heading_level(self, facade):
        """Test extraction with custom heading level."""
        examples = facade.extract_examples(
            "hashicorp/aws/5.100.0/docs/resources/lb",
            heading_level=2
        )
        
        assert examples is not None
        assert examples.startswith("## Example Usage:")
    
    def test_extract_all_with_heading_level(self, facade):
        """Test extract_all with custom heading level."""
        docs = facade.extract_all(
            "hashicorp/aws/5.100.0/docs/resources/lb",
            heading_level=3
        )
        
        assert docs['examples'].startswith("### Example Usage:")
        assert docs['arguments'].startswith("### Argument Reference:")


class TestFacadeCaching:
    """Test HTML caching functionality."""
    
    @pytest.fixture
    def facade(self):
        """Create a TerraformResourceDocs instance."""
        return TerraformResourceDocs()
    
    def test_html_caching(self, facade):
        """Test that HTML caching works."""
        url = "hashicorp/aws/5.100.0/docs/resources/lb"
        
        # First call - should fetch HTML
        docs1 = facade.extract_all(url)
        cache_size_after_first = len(facade._html_cache)
        assert cache_size_after_first == 1
        
        # Second call - should use cache
        docs2 = facade.extract_examples(url)
        cache_size_after_second = len(facade._html_cache)
        assert cache_size_after_second == 1  # Same cache size
        
        # Verify content is consistent
        assert docs1['examples'] == docs2
    
    def test_multiple_urls_cached(self, facade):
        """Test that multiple URLs are cached separately."""
        url1 = "hashicorp/aws/5.100.0/docs/resources/lb"
        url2 = "hashicorp/aws/5.100.0/docs/resources/s3_bucket"
        
        # Fetch first URL
        facade.extract_examples(url1)
        assert len(facade._html_cache) == 1
        
        # Fetch second URL
        facade.extract_examples(url2)
        assert len(facade._html_cache) == 2
    
    def test_clear_cache(self, facade):
        """Test cache clearing."""
        url = "hashicorp/aws/5.100.0/docs/resources/lb"
        
        # Populate cache
        facade.extract_all(url)
        assert len(facade._html_cache) == 1
        
        # Clear cache
        facade.clear_cache()
        assert len(facade._html_cache) == 0
    
    def test_cache_reuse_performance(self, facade):
        """Test that cache improves performance."""
        url = "hashicorp/aws/5.100.0/docs/resources/lb"
        
        # First call - will fetch
        docs1 = facade.extract_all(url)
        
        # Multiple subsequent calls should be fast (using cache)
        examples = facade.extract_examples(url)
        arguments = facade.extract_arguments(url)
        docs2 = facade.extract_all(url)
        
        # All should return the same content
        assert docs1['examples'] == examples
        assert docs1['arguments'] == arguments
        assert docs1 == docs2
        
        # Only one cache entry
        assert len(facade._html_cache) == 1


class TestFacadeEdgeCases:
    """Test edge cases and error handling."""
    
    @pytest.fixture
    def facade(self):
        """Create a TerraformResourceDocs instance."""
        return TerraformResourceDocs()
    
    def test_invalid_url(self, facade):
        """Test handling of completely invalid URL."""
        examples = facade.extract_examples("invalid/malformed/url")
        assert examples is None
    
    def test_nonexistent_resource(self, facade):
        """Test handling of non-existent resource (e.g., aws_alb)."""
        # aws_alb exists in schema but not in documentation
        docs = facade.extract_all("hashicorp/aws/5.100.0/docs/resources/alb")
        
        # Should handle gracefully (return None or empty)
        # Don't assert specific behavior, just that it doesn't crash
        assert isinstance(docs, dict)
        assert 'examples' in docs
        assert 'arguments' in docs


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

