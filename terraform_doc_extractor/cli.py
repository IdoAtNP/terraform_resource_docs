"""Command-line interface for Terraform documentation extractor."""

import sys
import json
from typing import Optional
import click
from loguru import logger

from .generic.extractor import TerraformDocExtractor


def setup_logging(verbose: bool):
    """Configure logging based on verbosity."""
    logger.remove()
    
    if verbose:
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
            level="DEBUG"
        )
    else:
        logger.add(
            sys.stderr,
            format="<level>{level: <8}</level> | <level>{message}</level>",
            level="INFO"
        )


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.pass_context
def cli(ctx, verbose):
    """Extract sections from Terraform provider documentation."""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    setup_logging(verbose)


@cli.command()
@click.argument('url')
@click.option('--sections', '-s', multiple=True, help='Section names to extract (can be used multiple times)')
@click.option('--all', 'extract_all', is_flag=True, help='Extract all sections')
@click.option('--text', is_flag=True, help='Output as plain text instead of HTML')
@click.option('--output', '-o', type=click.Path(), help='Output file (default: stdout)')
@click.option('--format', 'output_format', type=click.Choice(['json', 'html', 'text']), default='json', help='Output format')
@click.pass_context
def extract(ctx, url, sections, extract_all, text, output, output_format):
    """
    Extract sections from a Terraform resource documentation page.
    
    Examples:
    
        Extract specific sections:
        
        $ terraform-doc-extract extract "hashicorp/aws/5.100.0/docs/resources/lb" -s "Example Usage" -s "Argument Reference"
        
        Extract all sections:
        
        $ terraform-doc-extract extract "hashicorp/aws/latest/docs/resources/lb" --all
        
        Extract as plain text:
        
        $ terraform-doc-extract extract "hashicorp/aws/5.100.0/docs/resources/lb" -s "Example Usage" --text
    """
    extractor = TerraformDocExtractor()
    
    if not extract_all and not sections:
        click.echo("Error: Must specify either --sections or --all", err=True)
        sys.exit(1)
    
    sections_list = list(sections) if sections else None
    
    if output_format == 'text':
        text = True
    
    try:
        result = extractor.extract_sections(url, sections_list, as_text=text)
        
        if output_format == 'json':
            output_data = json.dumps(result, indent=2)
        elif output_format == 'html':
            output_data = '\n\n'.join(
                f'<!-- Section: {name} -->\n{content}' 
                for name, content in result.items() 
                if content
            )
        else:
            output_data = '\n\n'.join(
                f'=== {name} ===\n{content}' 
                for name, content in result.items() 
                if content
            )
        
        if output:
            with open(output, 'w') as f:
                f.write(output_data)
            logger.bind(output_file=output).info("Saved output to file")
        else:
            click.echo(output_data)
            
    except Exception as e:
        logger.bind(error=str(e)).error("Failed to extract sections")
        sys.exit(1)


@cli.command()
@click.argument('url')
@click.pass_context
def list_sections(ctx, url):
    """
    List all available sections in a documentation page.
    
    Example:
    
        $ terraform-doc-extract list-sections "hashicorp/aws/5.100.0/docs/resources/lb"
    """
    extractor = TerraformDocExtractor()
    
    try:
        sections = extractor.list_available_sections(url)
        
        if not sections:
            click.echo("No sections found", err=True)
            sys.exit(1)
        
        click.echo("Available sections:")
        for i, section in enumerate(sections, 1):
            click.echo(f"  {i}. {section}")
            
    except Exception as e:
        logger.bind(error=str(e)).error("Failed to list sections")
        sys.exit(1)


@cli.command()
@click.argument('url')
@click.option('--text', is_flag=True, help='Output as plain text instead of HTML')
@click.option('--output', '-o', type=click.Path(), help='Output file (default: stdout)')
@click.pass_context
def extract_all(ctx, url, text, output):
    """
    Extract the complete documentation from a page.
    
    Example:
    
        $ terraform-doc-extract extract-all "hashicorp/aws/5.100.0/docs/resources/lb"
    """
    extractor = TerraformDocExtractor()
    
    try:
        result = extractor.extract_full_documentation(url, as_text=text)
        
        if not result:
            click.echo("Failed to extract documentation", err=True)
            sys.exit(1)
        
        if output:
            with open(output, 'w') as f:
                f.write(result)
            logger.bind(output_file=output).info("Saved output to file")
        else:
            click.echo(result)
            
    except Exception as e:
        logger.bind(error=str(e)).error("Failed to extract documentation")
        sys.exit(1)


def main():
    """Entry point for the CLI."""
    cli(obj={})


if __name__ == '__main__':
    main()

