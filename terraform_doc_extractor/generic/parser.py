"""HTML parser for Terraform documentation sections."""

from typing import List, Dict, Optional
from bs4 import BeautifulSoup, Tag
from loguru import logger


class DocumentationParser:
    """Parses Terraform documentation HTML and extracts sections."""
    
    def __init__(self, html: str):
        """
        Initialize parser with HTML content.
        
        Args:
            html: Raw HTML string
        """
        self.soup = BeautifulSoup(html, 'lxml')
        self._sections = None
    
    @property
    def sections(self) -> Dict[str, Tag]:
        """
        Get all available sections as a dictionary.
        
        Returns:
            Dict mapping section names to their content elements
        """
        if self._sections is None:
            self._sections = self._parse_sections()
        return self._sections
    
    def _parse_sections(self) -> Dict[str, Tag]:
        """
        Parse all sections from the documentation.
        
        Sections are identified by h2 headers and include all content
        until the next h2 header.
        
        Returns:
            Dict mapping section names to their content
        """
        sections = {}
        
        markdown_div = self.soup.find('div', {'id': 'provider-doc'})
        if not markdown_div:
            # Check if this is a "Page Not Found" error
            not_found = self.soup.find('h1', string=lambda t: t and 'Page Not Found' in t if t else False)
            if not_found:
                    logger.warning("Page Not Found: The requested documentation page does not exist")
            else:
                logger.error("Could not find main documentation div")
            return sections
        
        h2_headers = markdown_div.find_all('h2')
        logger.bind(section_count=len(h2_headers)).debug("Found sections")
        
        for i, header in enumerate(h2_headers):
            section_name = header.get_text().strip()
            
            content_elements = []
            current = header.find_next_sibling()
            
            next_h2 = h2_headers[i + 1] if i + 1 < len(h2_headers) else None
            
            while current:
                if current.name == 'h2':
                    break
                if next_h2 and current == next_h2:
                    break
                    
                content_elements.append(current)
                current = current.find_next_sibling()
            
            section_wrapper = self.soup.new_tag('div')
            section_wrapper.append(header)
            for elem in content_elements:
                if elem.name:
                    section_wrapper.append(elem)
            
            sections[section_name] = section_wrapper
            logger.bind(section=section_name).debug("Parsed section")
        
        return sections
    
    def get_section(self, section_name: str) -> Optional[str]:
        """
        Get a specific section by name.
        
        Args:
            section_name: Name of the section (case-insensitive)
            
        Returns:
            Section HTML as string, or None if not found
        """
        section_name_lower = section_name.lower()
        
        for name, content in self.sections.items():
            if name.lower() == section_name_lower:
                return str(content)
        
        logger.bind(section_name=section_name).warning("Section not found")
        return None
    
    def get_sections(self, section_names: List[str]) -> Dict[str, Optional[str]]:
        """
        Get multiple sections by name.
        
        Args:
            section_names: List of section names
            
        Returns:
            Dict mapping section names to their HTML content
        """
        result = {}
        for name in section_names:
            result[name] = self.get_section(name)
        return result
    
    def get_all_sections(self) -> Dict[str, str]:
        """
        Get all sections as HTML strings.
        
        Returns:
            Dict mapping section names to their HTML content
        """
        return {name: str(content) for name, content in self.sections.items()}
    
    def list_sections(self) -> List[str]:
        """
        List all available section names.
        
        Returns:
            List of section names
        """
        return list(self.sections.keys())
    
    def get_sections_by_prefix(self, prefix: str) -> Dict[str, str]:
        """
        Get all sections whose names start with the given prefix.
        
        Args:
            prefix: The prefix to match (case-insensitive)
            
        Returns:
            Dict mapping matching section names to their HTML content
        """
        prefix_lower = prefix.lower()
        matching_sections = {}
        
        for name, content in self.sections.items():
            if name.lower().startswith(prefix_lower):
                matching_sections[name] = str(content)
        
        return matching_sections
    
    def get_sections_text_by_prefix(self, prefix: str) -> Dict[str, str]:
        """
        Get all sections whose names start with the given prefix as plain text.
        
        Args:
            prefix: The prefix to match (case-insensitive)
            
        Returns:
            Dict mapping matching section names to their plain text content
        """
        prefix_lower = prefix.lower()
        matching_sections = {}
        
        for name, content in self.sections.items():
            if name.lower().startswith(prefix_lower):
                text = self._extract_readable_text(content)
                matching_sections[name] = text
        
        return matching_sections
    
    def get_section_text(self, section_name: str) -> Optional[str]:
        """
        Get a specific section as plain text (no HTML).
        
        Args:
            section_name: Name of the section
            
        Returns:
            Section text content, or None if not found
        """
        section_name_lower = section_name.lower()
        
        for name, content in self.sections.items():
            if name.lower() == section_name_lower:
                return self._extract_readable_text(content)
        
        return None
    
    def _extract_readable_text(self, element: Tag) -> str:
        """
        Extract readable text from an element, preserving code blocks and structure.
        
        Args:
            element: BeautifulSoup Tag element
            
        Returns:
            Formatted text with preserved code blocks
        """
        import re
        
        output = []
        
        for elem in element.children:
            if not elem.name:
                continue
                
            if elem.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                text = elem.get_text(strip=True)
                output.append(f"\n{'='*len(text)}\n{text}\n{'='*len(text)}\n")
                
            elif elem.name == 'p':
                text = elem.get_text(strip=True)
                if text:
                    output.append(text + "\n")
                    
            elif elem.name in ['pre', 'code']:
                code = elem.get_text()
                output.append(f"\n```\n{code}\n```\n")
                
            elif elem.name == 'div':
                code_elem = elem.find('pre') or elem.find('code')
                if code_elem:
                    code = code_elem.get_text()
                    output.append(f"\n```\n{code}\n```\n")
                else:
                    text = elem.get_text(separator='\n', strip=True)
                    if text:
                        output.append(text + "\n")
                        
            elif elem.name in ['ul', 'ol']:
                for li in elem.find_all('li', recursive=False):
                    output.append(f"  • {li.get_text(strip=True)}\n")
                output.append("\n")
                
            elif elem.name == 'blockquote':
                text = elem.get_text(strip=True)
                for line in text.split('\n'):
                    output.append(f"> {line}\n")
                output.append("\n")
                
            else:
                text = elem.get_text(separator='\n', strip=True)
                if text:
                    output.append(text + "\n")
        
        result = ''.join(output)
        result = re.sub(r'\n{3,}', '\n\n', result)
        
        return result.strip()
    
    def get_full_documentation(self) -> Optional[str]:
        """
        Get the entire documentation content.
        
        Returns:
            Full documentation HTML as string
        """
        markdown_div = self.soup.find('div', {'id': 'provider-doc'})
        if markdown_div:
            return str(markdown_div)
        return None

