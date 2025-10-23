"""Facade class for easy access to specialized extractors."""

from typing import Optional, Dict
from pathlib import Path
from loguru import logger

from ..generic.url_parser import TerraformURL
from ..generic.fetcher import PageFetcher
from .example_usage_extractor import ExampleUsageExtractor
from .argument_reference_extractor import ArgumentReferenceExtractor


class TerraformResourceDocs:
    """
    Facade class that provides a unified interface to extract both
    Example Usage and Argument Reference sections.
    
    This class optimizes extraction by caching fetched HTML. Multiple operations
    on the same URL will reuse the cached HTML instead of re-fetching.
    
    Example:
        >>> from terraform_doc_extractor import TerraformResourceDocs
        >>> 
        >>> docs_extractor = TerraformResourceDocs()
        >>> 
        >>> # First call fetches HTML and caches it
        >>> docs = docs_extractor.extract_all("hashicorp/aws/5.100.0/docs/resources/lb")
        >>> 
        >>> # Subsequent calls reuse cached HTML (no re-fetch!)
        >>> docs_extractor.save_to_files("hashicorp/aws/5.100.0/docs/resources/lb", "output_dir")
        >>> examples = docs_extractor.extract_examples("hashicorp/aws/5.100.0/docs/resources/lb")
    """
    
    def __init__(
        self,
        headless: bool = True,
        timeout: int = 10,
        wait_time: int = 2
    ):
        """
        Initialize the facade with shared configuration.
        
        Args:
            headless: Run browser in headless mode
            timeout: Maximum time to wait for page elements
            wait_time: Extra wait time after page load
        """
        # Single fetcher for all operations
        self.fetcher = PageFetcher(
            headless=headless,
            timeout=timeout,
            wait_time=wait_time
        )
        
        # Specialized parsers (don't need fetchers anymore)
        self.example_extractor = ExampleUsageExtractor()
        self.argument_extractor = ArgumentReferenceExtractor()
        
        # Cache for fetched HTML: {url: html_content}
        self._html_cache: Dict[str, str] = {}
        
        logger.debug("Initialized TerraformResourceDocs with HTML caching")
    
    def _get_html(self, tf_url: TerraformURL) -> Optional[str]:
        """
        Get HTML from cache or fetch it if not cached.
        
        Args:
            tf_url: TerraformURL object
            
        Returns:
            HTML content or None if fetch failed
        """
        # Check cache first
        if tf_url.url in self._html_cache:
            logger.bind(url=tf_url.url).debug("Using cached HTML")
            return self._html_cache[tf_url.url]
        
        # Not in cache, fetch it
        logger.bind(url=tf_url.url).info("Fetching HTML (not in cache)")
        html = self.fetcher.fetch(tf_url.url)
        
        if html:
            # Cache it for future use
            self._html_cache[tf_url.url] = html
            logger.bind(url=tf_url.url, cache_size=len(self._html_cache)).debug("Cached HTML")
        
        return html
    
    def clear_cache(self):
        """
        Clear the HTML cache.
        
        Useful if you want to force re-fetching of pages.
        
        Example:
            >>> facade = TerraformDocumentationFacade()
            >>> docs = facade.extract_all("...")
            >>> facade.clear_cache()  # Force next call to re-fetch
        """
        cache_size = len(self._html_cache)
        self._html_cache.clear()
        logger.bind(cleared_entries=cache_size).info("Cleared HTML cache")
    
    def extract_all(self, url: str, heading_level: int = 1) -> Dict[str, Optional[str]]:
        """
        Extract both Example Usage and Argument Reference sections.
        
        Optimized: Uses cached HTML if available, otherwise fetches once.
        
        Args:
            url: Terraform Registry URL or path
            heading_level: Starting heading level (1 for #, 2 for ##, etc.)
            
        Returns:
            Dictionary with keys 'examples' and 'arguments' containing
            the formatted markdown content, or None if not found
            
        Example:
            >>> facade = TerraformDocumentationFacade()
            >>> docs = facade.extract_all("hashicorp/aws/5.100.0/docs/resources/lb")
            >>> print(docs['examples'])
            >>> print(docs['arguments'])
        """
        tf_url = TerraformURL.parse(url)
        
        if not tf_url:
            logger.bind(url=url).error("Failed to parse URL")
            return {'examples': None, 'arguments': None}
        
        # Get HTML from cache or fetch it
        html = self._get_html(tf_url)
        
        if not html:
            logger.bind(url=tf_url.url).error("Failed to fetch page")
            return {'examples': None, 'arguments': None}
        
        # Parse the HTML with both parsers
        logger.debug("Parsing both sections from HTML")
        examples = self.example_extractor.extract(tf_url, html=html, heading_level=heading_level)
        arguments = self.argument_extractor.extract(tf_url, html=html, heading_level=heading_level)
        
        return {
            'examples': examples,
            'arguments': arguments
        }
    
    def extract_examples(self, url: str, heading_level: int = 1) -> Optional[str]:
        """
        Extract only Example Usage section.
        
        Uses cached HTML if available.
        
        Args:
            url: Terraform Registry URL or path
            heading_level: Starting heading level (1 for #, 2 for ##, etc.)
            
        Returns:
            Formatted markdown string or None if not found
            
        Example:
            >>> facade = TerraformDocumentationFacade()
            >>> examples = facade.extract_examples("hashicorp/aws/5.100.0/docs/resources/lb")
        """
        tf_url = TerraformURL.parse(url)
        
        if not tf_url:
            logger.bind(url=url).error("Failed to parse URL")
            return None
        
        # Get HTML from cache or fetch it
        html = self._get_html(tf_url)
        
        if not html:
            return None
        
        return self.example_extractor.extract(tf_url, html=html, heading_level=heading_level)
    
    def extract_arguments(self, url: str, heading_level: int = 1) -> Optional[str]:
        """
        Extract only Argument Reference section.
        
        Uses cached HTML if available.
        
        Args:
            url: Terraform Registry URL or path
            heading_level: Starting heading level (1 for #, 2 for ##, etc.)
            
        Returns:
            Formatted markdown string or None if not found
            
        Example:
            >>> facade = TerraformDocumentationFacade()
            >>> arguments = facade.extract_arguments("hashicorp/aws/5.100.0/docs/resources/lb")
        """
        tf_url = TerraformURL.parse(url)
        
        if not tf_url:
            logger.bind(url=url).error("Failed to parse URL")
            return None
        
        # Get HTML from cache or fetch it
        html = self._get_html(tf_url)
        
        if not html:
            return None
        
        return self.argument_extractor.extract(tf_url, html=html, heading_level=heading_level)
    
    def save_to_files(
        self,
        url: str,
        output_dir: str = ".",
        examples_filename: Optional[str] = None,
        arguments_filename: Optional[str] = None,
        heading_level: int = 1
    ) -> Dict[str, bool]:
        """
        Extract and save both sections to separate files.
        
        Optimized: Fetches HTML only once and parses it twice.
        
        Args:
            url: Terraform Registry URL or path
            output_dir: Directory to save files in (default: current directory)
            examples_filename: Custom filename for examples (default: {resource}_examples.md)
            arguments_filename: Custom filename for arguments (default: {resource}_arguments.md)
            heading_level: Starting heading level (1 for #, 2 for ##, etc.)
            
        Returns:
            Dictionary with keys 'examples' and 'arguments' indicating success (True/False)
            
        Example:
            >>> facade = TerraformDocumentationFacade()
            >>> result = facade.save_to_files(
            ...     "hashicorp/aws/5.100.0/docs/resources/lb",
            ...     output_dir="docs"
            ... )
            >>> print(f"Examples saved: {result['examples']}")
            >>> print(f"Arguments saved: {result['arguments']}")
        """
        tf_url = TerraformURL.parse(url)
        
        if not tf_url:
            logger.bind(url=url).error("Failed to parse URL")
            return {'examples': False, 'arguments': False}
        
        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate filenames
        if not examples_filename:
            examples_filename = f"{tf_url.resource}_examples.md"
        if not arguments_filename:
            arguments_filename = f"{tf_url.resource}_arguments.md"
        
        examples_file = output_path / examples_filename
        arguments_file = output_path / arguments_filename
        
        logger.bind(
            examples_file=str(examples_file),
            arguments_file=str(arguments_file)
        ).info("Extracting and saving both sections to files")
        
        # Get HTML from cache or fetch it
        html = self._get_html(tf_url)
        
        if not html:
            logger.bind(url=tf_url.url).error("Failed to get HTML")
            return {'examples': False, 'arguments': False}
        
        # Extract both from same HTML
        examples_md = self.example_extractor.extract(tf_url, html=html, heading_level=heading_level)
        arguments_md = self.argument_extractor.extract(tf_url, html=html, heading_level=heading_level)
        
        # Save to files
        examples_success = False
        arguments_success = False
        
        if examples_md:
            try:
                with open(examples_file, 'w', encoding='utf-8') as f:
                    f.write(examples_md)
                examples_success = True
                logger.bind(file=str(examples_file)).info("Saved Example Usage")
            except Exception as e:
                logger.bind(file=str(examples_file), error=str(e)).error("Failed to save file")
        
        if arguments_md:
            try:
                with open(arguments_file, 'w', encoding='utf-8') as f:
                    f.write(arguments_md)
                arguments_success = True
                logger.bind(file=str(arguments_file)).info("Saved Argument Reference")
            except Exception as e:
                logger.bind(file=str(arguments_file), error=str(e)).error("Failed to save file")
        
        return {
            'examples': examples_success,
            'arguments': arguments_success
        }
    
    def save_examples(
        self,
        url: str,
        output_file: str
    ) -> bool:
        """
        Extract and save only Example Usage section.
        
        Args:
            url: Terraform Registry URL or path
            output_file: Path to output file
            
        Returns:
            True if successful, False otherwise
            
        Example:
            >>> facade = TerraformDocumentationFacade()
            >>> facade.save_examples("hashicorp/aws/5.100.0/docs/resources/lb", "lb_examples.md")
        """
        tf_url = TerraformURL.parse(url)
        
        if not tf_url:
            logger.bind(url=url).error("Failed to parse URL")
            return False
        
        return self.example_extractor.extract_to_file(tf_url, output_file)
    
    def save_arguments(
        self,
        url: str,
        output_file: str
    ) -> bool:
        """
        Extract and save only Argument Reference section.
        
        Args:
            url: Terraform Registry URL or path
            output_file: Path to output file
            
        Returns:
            True if successful, False otherwise
            
        Example:
            >>> facade = TerraformDocumentationFacade()
            >>> facade.save_arguments("hashicorp/aws/5.100.0/docs/resources/lb", "lb_arguments.md")
        """
        tf_url = TerraformURL.parse(url)
        
        if not tf_url:
            logger.bind(url=url).error("Failed to parse URL")
            return False
        
        return self.argument_extractor.extract_to_file(tf_url, output_file)
    
    def batch_extract(
        self,
        urls: list,
        output_dir: str = "."
    ) -> Dict[str, Dict[str, bool]]:
        """
        Extract and save documentation for multiple resources.
        
        Args:
            urls: List of Terraform Registry URLs or paths
            output_dir: Directory to save all files
            
        Returns:
            Dictionary mapping URLs to their extraction results
            
        Example:
            >>> facade = TerraformDocumentationFacade()
            >>> urls = [
            ...     "hashicorp/aws/5.100.0/docs/resources/lb",
            ...     "hashicorp/aws/5.100.0/docs/resources/s3_bucket"
            ... ]
            >>> results = facade.batch_extract(urls, "docs/aws")
            >>> for url, result in results.items():
            ...     print(f"{url}: examples={result['examples']}, arguments={result['arguments']}")
        """
        results = {}
        
        logger.bind(count=len(urls)).info("Starting batch extraction")
        
        for url in urls:
            tf_url = TerraformURL.parse(url)
            
            if not tf_url:
                logger.bind(url=url).warning("Skipping invalid URL")
                results[url] = {'examples': False, 'arguments': False}
                continue
            
            result = self.save_to_files(url, output_dir)
            results[url] = result
            
            logger.bind(
                resource=tf_url.resource,
                examples=result['examples'],
                arguments=result['arguments']
            ).info("Processed resource")
        
        logger.info("Batch extraction complete")
        
        return results

