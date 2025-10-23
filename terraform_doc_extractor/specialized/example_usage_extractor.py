"""Specialized extractor for Example Usage sections."""

from typing import Optional
from loguru import logger

from ..generic.url_parser import TerraformURL
from ..generic.extractor import TerraformDocExtractor
from ..generic.parser import DocumentationParser


class ExampleUsageExtractor:
    """
    Extracts and formats Example Usage sections from Terraform documentation.
    
    This class can work in two modes:
    1. Standalone: Fetches HTML and parses it
    2. Parser mode: Accepts pre-fetched HTML
    
    Example:
        >>> from terraform_doc_extractor import TerraformURL
        >>> from terraform_doc_extractor.example_usage_extractor import ExampleUsageExtractor
        >>> 
        >>> # Standalone mode
        >>> url = TerraformURL.parse("hashicorp/aws/5.100.0/docs/resources/lb")
        >>> extractor = ExampleUsageExtractor()
        >>> markdown = extractor.extract(url)
        >>> 
        >>> # Parser mode (more efficient when extracting multiple sections)
        >>> html = fetch_html(url)  # Fetch once
        >>> markdown = extractor.extract_from_html(url, html)
    """
    
    def __init__(
        self,
        headless: bool = True,
        timeout: int = 10,
        wait_time: int = 2
    ):
        """
        Initialize the Example Usage extractor.
        
        Args:
            headless: Run browser in headless mode
            timeout: Maximum time to wait for page elements
            wait_time: Extra wait time after page load
        """
        self.doc_extractor = TerraformDocExtractor(
            headless=headless,
            timeout=timeout,
            wait_time=wait_time
        )
    
    def extract(self, tf_url: TerraformURL, html: Optional[str] = None, heading_level: int = 1) -> Optional[str]:
        """
        Extract Example Usage section(s) as formatted markdown.
        
        This method automatically handles multiple example usage sections.
        If multiple sections exist (e.g., "Example Usage - Basic", "Example Usage - Advanced"),
        they will all be combined into a single markdown output.
        
        Args:
            tf_url: TerraformURL object containing provider and resource info
            html: Optional pre-fetched HTML. If provided, skips fetching (more efficient).
            heading_level: Starting heading level (1 for #, 2 for ##, etc.)
            
        Returns:
            Formatted markdown string with example usage, or None if not found
            
        Example:
            >>> url = TerraformURL.parse("hashicorp/aws/5.100.0/docs/resources/lb")
            >>> extractor = ExampleUsageExtractor()
            >>> 
            >>> # Standalone mode (fetches HTML)
            >>> markdown = extractor.extract(url)
            >>> 
            >>> # Parser mode (uses pre-fetched HTML)
            >>> html = fetch_html(url)
            >>> markdown = extractor.extract(url, html=html)
        """
        logger.bind(
            provider=tf_url.provider,
            resource=tf_url.resource
        ).info("Extracting Example Usage")
        
        # If HTML is provided, parse it directly
        if html:
            logger.debug("Using pre-fetched HTML")
            parser = DocumentationParser(html)
            
            # Try to get all "Example Usage" sections (handles multiple sections)
            example_sections = parser.get_sections_text_by_prefix("Example Usage")
            
            if not example_sections:
                logger.bind(url=tf_url.url).warning("No Example Usage sections found")
                return None
            
            # If multiple sections exist, combine them
            if len(example_sections) > 1:
                logger.bind(
                    count=len(example_sections),
                    sections=list(example_sections.keys())
                ).info("Found multiple Example Usage sections")
                markdown = self._format_multiple_sections(tf_url, example_sections, heading_level)
            else:
                # Single section
                content = list(example_sections.values())[0]
                markdown = self._format_as_markdown(tf_url, content, heading_level)
        else:
            # Otherwise, fetch the HTML first
            logger.debug("Fetching HTML")
            result = self.doc_extractor.extract_sections(
                tf_url.url,
                ["Example Usage"],
                as_text=True
            )
            content = result.get("Example Usage")
            
            if not content:
                logger.bind(url=tf_url.url).warning("Example Usage section not found")
                return None
            
            markdown = self._format_as_markdown(tf_url, content, heading_level)
        
        logger.bind(
            provider=tf_url.provider,
            resource=tf_url.resource,
            content_length=len(markdown)
        ).debug("Successfully extracted Example Usage")
        
        return markdown
    
    def _format_multiple_sections(self, tf_url: TerraformURL, sections: dict, heading_level: int = 1) -> str:
        """
        Format multiple example usage sections into a single markdown document.
        
        Args:
            tf_url: TerraformURL object for metadata
            sections: Dict mapping section names to their content
            heading_level: Starting heading level (1 for #, 2 for ##, etc.)
            
        Returns:
            Formatted markdown string with all sections
        """
        lines = []
        
        # Main heading
        main_heading = "#" * heading_level
        lines.append(f"{main_heading} Example Usage: {tf_url.resource}")
        lines.append("")
        
        # Process each section (subsections are one level deeper)
        subsection_heading = "#" * (heading_level + 1)
        for i, (section_name, content) in enumerate(sections.items()):
            # Extract the subsection name (e.g., "Basic" from "Example Usage - Basic")
            if " - " in section_name:
                subsection = section_name.split(" - ", 1)[1]
                lines.append(f"{subsection_heading} {subsection}")
            else:
                lines.append(f"{subsection_heading} Example {i + 1}")
            
            lines.append("")
            
            content_lines = content.split('\n')
            in_code_block = False
            
            for line in content_lines:
                if line.strip() == '```':
                    if not in_code_block:
                        lines.append("```hcl")
                        in_code_block = True
                    else:
                        lines.append("```")
                        in_code_block = False
                else:
                    if line.startswith('=') and len(set(line.strip())) == 1:
                        continue
                    lines.append(line)
            
            lines.append("")
            lines.append("---")
            lines.append("")
        
        lines.append(f"*Source: {tf_url.url}*")
        
        return '\n'.join(lines)
    
    def _format_as_markdown(self, tf_url: TerraformURL, content: str, heading_level: int = 1) -> str:
        """
        Format the extracted content as readable markdown.
        
        Args:
            tf_url: TerraformURL object for metadata
            content: Raw text content from extraction
            heading_level: Starting heading level (1 for #, 2 for ##, etc.)
            
        Returns:
            Formatted markdown string
        """
        lines = []
        
        main_heading = "#" * heading_level
        lines.append(f"{main_heading} Example Usage: {tf_url.resource}")
        lines.append("")
        
        content_lines = content.split('\n')
        in_code_block = False
        
        for line in content_lines:
            if line.strip() == '```':
                if not in_code_block:
                    lines.append("```hcl")
                    in_code_block = True
                else:
                    lines.append("```")
                    in_code_block = False
            else:
                if line.startswith('=') and len(set(line.strip())) == 1:
                    continue
                lines.append(line)
        
        lines.append("")
        
        return '\n'.join(lines)
    
    def extract_to_file(
        self,
        tf_url: TerraformURL,
        output_file: str
    ) -> bool:
        """
        Extract Example Usage and save to a markdown file.
        
        Args:
            tf_url: TerraformURL object
            output_file: Path to output file
            
        Returns:
            True if successful, False otherwise
            
        Example:
            >>> url = TerraformURL.parse("hashicorp/aws/5.100.0/docs/resources/lb")
            >>> extractor = ExampleUsageExtractor()
            >>> extractor.extract_to_file(url, "lb_examples.md")
        """
        markdown = self.extract(tf_url)
        
        if not markdown:
            return False
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown)
            
            logger.bind(output_file=output_file).info("Saved Example Usage to file")
            return True
            
        except Exception as e:
            logger.bind(output_file=output_file, error=str(e)).error("Failed to save file")
            return False

