# Terraform Resource Documentation Extractor

A Python package to extract and format documentation from Terraform Registry resources.

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)

## Features

- 🔍 **Generic Extraction**: Extract any section from Terraform documentation
- 📝 **Specialized Extractors**: Dedicated formatters for Example Usage and Argument Reference
- 🎯 **Smart Handling**: Automatically combines multiple example sections
- 🎨 **Clean Markdown**: Beautiful, readable markdown output
- 🔄 **HTML Caching**: Efficient caching to minimize network requests
- 📊 **Custom Heading Levels**: Control heading hierarchy for document embedding
- 🔇 **Silent Mode**: Perfect for automation and scripts

## Installation

```bash
# Clone the repository
git clone https://github.com/IdoAtNP/terraform_resource_docs.git
cd terraform_resource_docs

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

## Quick Start

### Using the Facade (Recommended)

```python
from terraform_doc_extractor import TerraformResourceDocs

# Initialize
docs = TerraformResourceDocs()

# Extract both sections
result = docs.extract_all("hashicorp/aws/5.100.0/docs/resources/lb")
print(result['examples'])
print(result['arguments'])

# Or extract individually
examples = docs.extract_examples("hashicorp/aws/5.100.0/docs/resources/lb")
arguments = docs.extract_arguments("hashicorp/aws/5.100.0/docs/resources/lb")
```

### Custom Heading Levels

Perfect for embedding in larger documents:

```python
# Start with ## instead of #
docs = TerraformResourceDocs()
examples = docs.extract_examples(
    "hashicorp/aws/5.100.0/docs/resources/lb",
    heading_level=2
)
```

### Silent Mode

For scripts and automation:

```python
from loguru import logger
logger.disable("terraform_doc_extractor")

docs = TerraformResourceDocs()
examples = docs.extract_examples("hashicorp/aws/5.100.0/docs/resources/lb")
print(examples)  # Clean output, no logs
```

## Package Structure

```
terraform_doc_extractor/
├── generic/
│   ├── TerraformDocExtractor  - Generic extraction for any section
│   ├── TerraformURL           - URL parsing and validation
│   ├── PageFetcher            - Headless browser HTML fetching
│   └── DocumentationParser    - HTML parsing with prefix matching
└── specialized/
    ├── ExampleUsageExtractor      - Extracts example usage (handles multiple)
    ├── ArgumentReferenceExtractor - Extracts argument reference
    └── TerraformResourceDocs      - Facade with caching
```

## Key Features

### Multiple Example Sections

Automatically detects and combines multiple example sections:

```python
# Google BigQuery Dataset has 6 example sections
docs = TerraformResourceDocs()
examples = docs.extract_examples(
    "hashicorp/google/latest/docs/resources/bigquery_dataset"
)
# All 6 sections combined with proper subsection headers!
```

### HTML Caching

Efficient caching prevents redundant network requests:

```python
docs = TerraformResourceDocs()

# First call fetches HTML
all_docs = docs.extract_all(url)

# Subsequent calls use cached HTML (no fetch!)
examples = docs.extract_examples(url)
arguments = docs.extract_arguments(url)

# Clear cache when needed
docs.clear_cache()
```

### Generic Extractor

For extracting any section:

```python
from terraform_doc_extractor import TerraformDocExtractor

extractor = TerraformDocExtractor()

# List available sections
sections = extractor.list_available_sections(
    "hashicorp/aws/5.100.0/docs/resources/lb"
)

# Extract specific sections
result = extractor.extract_sections(
    "hashicorp/aws/5.100.0/docs/resources/lb",
    ["Example Usage", "Argument Reference", "Attributes Reference"],
    as_text=True
)
```

## Supported Providers

Works with any Terraform Registry provider:

- AWS (`hashicorp/aws`)
- Google Cloud (`hashicorp/google`)
- Azure (`hashicorp/azurerm`)
- Databricks (`databricks/databricks`)
- And many more!

## Examples

See the [`examples/`](examples/) directory for comprehensive examples:

- `basic_usage.py` - Generic extractor demonstration
- `final_demo.py` - Comprehensive feature showcase
- `heading_level_demo.py` - Custom heading levels
- `multiple_examples_demo.py` - Multiple example sections
- `silent_extraction.py` - Silent mode usage

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_facade.py

# Run with verbose output
pytest tests/ -v

# Run tests matching pattern
pytest tests/ -k "caching"
```

Test coverage:
- ✅ URL parsing (7 tests)
- ✅ Generic extraction (7 tests)
- ✅ Specialized extractors (9 tests)
- ✅ Facade & caching (11 tests)
- ✅ Markdown formatting (13 tests)

**Total: 47 tests**

## CLI Usage

```bash
# Extract sections from a resource
terraform-doc-extract hashicorp/aws/5.100.0/docs/resources/lb \
  --sections "Example Usage" "Argument Reference" \
  --output-dir ./output

# List available sections
terraform-doc-extract hashicorp/aws/5.100.0/docs/resources/lb --list
```

## Requirements

- Python 3.7+
- Chrome/Chromium (for Selenium)
- Internet connection (for fetching documentation)

See [`requirements.txt`](requirements.txt) for Python dependencies.

## Architecture

The package is organized into two main modules:

### Generic Module
Core functionality for extracting any section from Terraform documentation:
- URL parsing and validation
- HTML fetching with Selenium (JavaScript-rendered pages)
- BeautifulSoup parsing
- Section identification and extraction

### Specialized Module
Domain-specific extractors with enhanced formatting:
- Clean markdown output
- Code block formatting
- Argument formatting with bold backticks
- Multiple section handling
- Custom heading levels

## License

Copyright (c) 2025 NPLabs. All rights reserved.

This is proprietary software owned by NPLabs. Unauthorized copying, modification,
distribution, or use of this software is strictly prohibited. See the LICENSE
file for full terms and conditions.

## Author

NPLabs

## Repository

[https://github.com/IdoAtNP/terraform_resource_docs](https://github.com/IdoAtNP/terraform_resource_docs)

