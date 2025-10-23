"""Main extractor class combining URL parsing, fetching, and parsing."""

from typing import List, Dict, Optional
from loguru import logger

from .url_parser import TerraformURL
from .fetcher import PageFetcher
from .parser import DocumentationParser


class TerraformDocExtractor:
    """
    Main class for extracting documentation sections from Terraform Registry.
    
    Example:
        >>> extractor = TerraformDocExtractor()
        >>> sections = extractor.extract_sections(
        ...     "https://registry.terraform.io/providers/hashicorp/aws/5.100.0/docs/resources/lb",
        ...     ["Example Usage", "Argument Reference"]
        ... )
    """
    
    def __init__(
        self,
        headless: bool = True,
        timeout: int = 10,
        wait_time: int = 2
    ):
        """
        Initialize the extractor.
        
        Args:
            headless: Run browser in headless mode
            timeout: Maximum time to wait for page elements
            wait_time: Extra wait time after page load
        """
        self.fetcher = PageFetcher(
            headless=headless,
            timeout=timeout,
            wait_time=wait_time
        )
    
    def extract_sections(
        self,
        url: str,
        sections: Optional[List[str]] = None,
        as_text: bool = False
    ) -> Dict[str, Optional[str]]:
        """
        Extract specific sections from a Terraform resource documentation page.
        
        Args:
            url: Terraform Registry URL or path
            sections: List of section names to extract. If None, extracts all sections.
            as_text: If True, return plain text instead of HTML
            
        Returns:
            Dict mapping section names to their content
            
        Example:
            >>> extractor = TerraformDocExtractor()
            >>> sections = extractor.extract_sections(
            ...     "hashicorp/aws/5.100.0/docs/resources/lb",
            ...     ["Example Usage"]
            ... )
        """
        tf_url = TerraformURL.parse(url)
        if not tf_url:
            logger.bind(url=url).error("Failed to parse URL")
            return {}
        
        html = self.fetcher.fetch(tf_url.url)
        if not html:
            logger.bind(url=tf_url.url).error("Failed to fetch page")
            return {}
        
        parser = DocumentationParser(html)
        
        if sections is None:
            if as_text:
                return {
                    name: parser.get_section_text(name)
                    for name in parser.list_sections()
                }
            return parser.get_all_sections()
        
        if as_text:
            return {
                name: parser.get_section_text(name)
                for name in sections
            }
        
        return parser.get_sections(sections)
    
    def list_available_sections(self, url: str) -> List[str]:
        """
        List all available sections in a documentation page.
        
        Args:
            url: Terraform Registry URL or path
            
        Returns:
            List of section names
            
        Example:
            >>> extractor = TerraformDocExtractor()
            >>> sections = extractor.list_available_sections(
            ...     "hashicorp/aws/5.100.0/docs/resources/lb"
            ... )
            >>> print(sections)
            ['Example Usage', 'Argument Reference', 'Attribute Reference', ...]
        """
        tf_url = TerraformURL.parse(url)
        if not tf_url:
            logger.bind(url=url).error("Failed to parse URL")
            return []
        
        html = self.fetcher.fetch(tf_url.url)
        if not html:
            logger.bind(url=tf_url.url).error("Failed to fetch page")
            return []
        
        parser = DocumentationParser(html)
        return parser.list_sections()
    
    def extract_full_documentation(
        self,
        url: str,
        as_text: bool = False
    ) -> Optional[str]:
        """
        Extract the complete documentation from a page.
        
        Args:
            url: Terraform Registry URL or path
            as_text: If True, return plain text instead of HTML
            
        Returns:
            Full documentation content as string
        """
        tf_url = TerraformURL.parse(url)
        if not tf_url:
            logger.bind(url=url).error("Failed to parse URL")
            return None
        
        html = self.fetcher.fetch(tf_url.url)
        if not html:
            logger.bind(url=tf_url.url).error("Failed to fetch page")
            return None
        
        parser = DocumentationParser(html)
        
        if as_text:
            doc_html = parser.get_full_documentation()
            if doc_html:
                soup_doc = parser.soup.find('div', {'id': 'provider-doc'})
                if soup_doc:
                    return soup_doc.get_text(separator='\n', strip=True)
        
        return parser.get_full_documentation()

