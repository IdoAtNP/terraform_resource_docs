"""Specialized extractor for Argument Reference sections."""

from typing import Optional
from loguru import logger

from ..generic.url_parser import TerraformURL
from ..generic.extractor import TerraformDocExtractor
from ..generic.parser import DocumentationParser


class ArgumentReferenceExtractor:
    """
    Extracts and formats Argument Reference sections from Terraform documentation.
    
    This class can work in two modes:
    1. Standalone: Fetches HTML and parses it
    2. Parser mode: Accepts pre-fetched HTML
    
    Example:
        >>> from terraform_doc_extractor import TerraformURL
        >>> from terraform_doc_extractor.argument_reference_extractor import ArgumentReferenceExtractor
        >>> 
        >>> # Standalone mode
        >>> url = TerraformURL.parse("hashicorp/aws/5.100.0/docs/resources/lb")
        >>> extractor = ArgumentReferenceExtractor()
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
        Initialize the Argument Reference extractor.
        
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
        Extract Argument Reference section as formatted markdown.
        
        Args:
            tf_url: TerraformURL object containing provider and resource info
            html: Optional pre-fetched HTML. If provided, skips fetching (more efficient).
            heading_level: Starting heading level (1 for #, 2 for ##, etc.)
            
        Returns:
            Formatted markdown string with argument reference, or None if not found
            
        Example:
            >>> url = TerraformURL.parse("hashicorp/aws/5.100.0/docs/resources/lb")
            >>> extractor = ArgumentReferenceExtractor()
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
        ).info("Extracting Argument Reference")
        
        # If HTML is provided, parse it directly
        if html:
            logger.debug("Using pre-fetched HTML")
            parser = DocumentationParser(html)
            content = parser.get_section_text("Argument Reference")
        else:
            # Otherwise, fetch the HTML first
            logger.debug("Fetching HTML")
            result = self.doc_extractor.extract_sections(
                tf_url.url,
                ["Argument Reference"],
                as_text=True
            )
            content = result.get("Argument Reference")
        
        if not content:
            logger.bind(url=tf_url.url).warning("Argument Reference section not found")
            return None
        
        markdown = self._format_as_markdown(tf_url, content, heading_level)
        
        logger.bind(
            provider=tf_url.provider,
            resource=tf_url.resource,
            content_length=len(markdown)
        ).debug("Successfully extracted Argument Reference")
        
        return markdown
    
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
        lines.append(f"{main_heading} Argument Reference: {tf_url.resource}")
        lines.append("")
        
        content_lines = content.split('\n')
        in_code_block = False
        skip_next_code_block = False
        
        # Subsection heading (one level deeper than main)
        subsection_heading = "#" * (heading_level + 2)
        
        for i, line in enumerate(content_lines):
            if line.strip() == '```':
                if not in_code_block:
                    next_line = content_lines[i + 1].strip() if i + 1 < len(content_lines) else ""
                    if len(next_line.split()) <= 2 and not next_line.startswith(('resource', 'data', 'module', 'variable', 'output')):
                        skip_next_code_block = True
                        in_code_block = True
                        continue
                    
                    lines.append("```hcl")
                    in_code_block = True
                else:
                    if skip_next_code_block:
                        skip_next_code_block = False
                        in_code_block = False
                        continue
                    
                    lines.append("```")
                    in_code_block = False
            else:
                if skip_next_code_block and in_code_block:
                    continue
                
                if line.startswith('=') and len(set(line.strip())) == 1:
                    continue
                
                stripped = line.lstrip()
                if stripped.startswith('• '):
                    indent_level = len(line) - len(stripped)
                    arg_text = stripped[2:].strip()
                    
                    if '-' in arg_text:
                        parts = arg_text.split('-', 1)
                        arg_name = parts[0].strip()
                        description = parts[1].strip() if len(parts) > 1 else ""
                        
                        indent = ' ' * indent_level
                        if indent_level == 0:
                            lines.append(f"{indent}- **`{arg_name}`** - {description}")
                        else:
                            lines.append(f"{indent}- **`{arg_name}`** - {description}")
                    else:
                        lines.append(f"- {arg_text}")
                elif stripped and not in_code_block:
                    if stripped.endswith(':') and not any(word in stripped.lower() for word in ['note', 'warning', 'important']):
                        lines.append(f"\n{subsection_heading} {stripped[:-1]}\n")
                    else:
                        lines.append(line)
                elif in_code_block:
                    lines.append(line)
        
        lines.append("")
        
        return '\n'.join(lines)
    
    def extract_to_file(
        self,
        tf_url: TerraformURL,
        output_file: str
    ) -> bool:
        """
        Extract Argument Reference and save to a markdown file.
        
        Args:
            tf_url: TerraformURL object
            output_file: Path to output file
            
        Returns:
            True if successful, False otherwise
            
        Example:
            >>> url = TerraformURL.parse("hashicorp/aws/5.100.0/docs/resources/lb")
            >>> extractor = ArgumentReferenceExtractor()
            >>> extractor.extract_to_file(url, "lb_arguments.md")
        """
        markdown = self.extract(tf_url)
        
        if not markdown:
            return False
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown)
            
            logger.bind(output_file=output_file).info("Saved Argument Reference to file")
            return True
            
        except Exception as e:
            logger.bind(output_file=output_file, error=str(e)).error("Failed to save file")
            return False

