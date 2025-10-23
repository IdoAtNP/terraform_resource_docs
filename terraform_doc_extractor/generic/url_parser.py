"""URL parser for Terraform Registry resource documentation."""

import re
from typing import Optional
from dataclasses import dataclass
from loguru import logger


@dataclass
class TerraformURL:
    """Parsed Terraform Registry URL components."""
    
    namespace: str
    provider: str
    version: str
    resource: str
    
    @property
    def url(self) -> str:
        """Construct full URL from components."""
        return (
            f"https://registry.terraform.io/providers/"
            f"{self.namespace}/{self.provider}/{self.version}/"
            f"docs/resources/{self.resource}"
        )
    
    @classmethod
    def parse(cls, url: str) -> Optional["TerraformURL"]:
        """
        Parse a Terraform Registry resource documentation URL.
        
        Args:
            url: Full URL or just the path components
            
        Returns:
            TerraformURL object if valid, None otherwise
            
        Example:
            >>> url = "https://registry.terraform.io/providers/hashicorp/aws/5.100.0/docs/resources/lb"
            >>> tf_url = TerraformURL.parse(url)
            >>> tf_url.namespace
            'hashicorp'
        """
        pattern = (
            r"(?:https?://registry\.terraform\.io/providers/)?"
            r"(?P<namespace>[\w-]+)/"
            r"(?P<provider>[\w-]+)/"
            r"(?P<version>[\w.-]+)/"
            r"docs/resources/"
            r"(?P<resource>[\w_]+)"
        )
        
        match = re.search(pattern, url)
        if not match:
            logger.bind(url=url).error("Invalid Terraform Registry URL format")
            return None
        
        components = match.groupdict()
        logger.bind(
            namespace=components["namespace"],
            provider=components["provider"],
            version=components["version"],
            resource=components["resource"]
        ).debug("Parsed URL successfully")
        
        return cls(
            namespace=components["namespace"],
            provider=components["provider"],
            version=components["version"],
            resource=components["resource"]
        )
    
    @classmethod
    def from_components(
        cls,
        namespace: str,
        provider: str,
        version: str,
        resource: str
    ) -> "TerraformURL":
        """
        Create TerraformURL from individual components.
        
        Args:
            namespace: Provider namespace (e.g., 'hashicorp')
            provider: Provider name (e.g., 'aws')
            version: Version string (e.g., '5.100.0' or 'latest')
            resource: Resource name (e.g., 'lb')
            
        Returns:
            TerraformURL object
        """
        return cls(
            namespace=namespace,
            provider=provider,
            version=version,
            resource=resource
        )

