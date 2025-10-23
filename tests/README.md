# Tests

Comprehensive test suite for terraform-doc-extractor.

## Test Files

### `test_url_parser.py`
Tests URL parsing and validation functionality:
- Full URL parsing
- Short path parsing
- Latest version handling
- Invalid URL handling
- URL reconstruction

### `test_generic_extractor.py`
Tests the generic `TerraformDocExtractor`:
- Listing available sections
- Extracting single sections
- Extracting multiple sections
- HTML vs text extraction
- Nonexistent section handling

### `test_specialized_extractors.py`
Tests specialized extractors (`ExampleUsageExtractor`, `ArgumentReferenceExtractor`):
- Single example section extraction
- Multiple example sections handling
- Custom heading levels
- Code block formatting
- Argument formatting

### `test_facade.py`
Tests the `TerraformResourceDocs` facade:
- Basic extraction operations
- HTML caching mechanism
- Cache clearing
- Multiple URL caching
- Edge cases and error handling

### `test_markdown_formatting.py`
Tests markdown output quality:
- Code block formatting
- Argument formatting
- Heading hierarchy
- List formatting
- Multiple example sections structure
- No HTML tags in output
- No metadata in output

## Running Tests

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test File
```bash
pytest tests/test_facade.py
pytest tests/test_url_parser.py
```

### Run Specific Test Class
```bash
pytest tests/test_facade.py::TestFacadeCaching
```

### Run Specific Test
```bash
pytest tests/test_facade.py::TestFacadeCaching::test_html_caching
```

### Run with Verbose Output
```bash
pytest tests/ -v
```

### Run with Coverage
```bash
pytest tests/ --cov=terraform_doc_extractor --cov-report=html
```

### Run Tests Matching Pattern
```bash
pytest tests/ -k "caching"
pytest tests/ -k "heading"
```

## Test Organization

Tests are organized by component:
- **URL Parser**: Core URL parsing logic
- **Generic Extractor**: Base extraction functionality
- **Specialized Extractors**: Domain-specific extractors
- **Facade**: High-level interface and caching
- **Markdown Formatting**: Output quality and structure

## Test Coverage

The test suite covers:
- ✅ URL parsing and validation
- ✅ Section extraction (single and multiple)
- ✅ HTML vs text output
- ✅ Specialized markdown formatting
- ✅ Multiple example sections
- ✅ Custom heading levels
- ✅ HTML caching
- ✅ Error handling
- ✅ Edge cases

## Requirements

Tests require:
- pytest >= 7.4.0
- All package dependencies (see requirements.txt)

Install with:
```bash
pip install -r requirements.txt
```

## CI/CD Integration

These tests are designed to run in CI/CD pipelines. Example:

```yaml
# GitHub Actions example
- name: Run tests
  run: pytest tests/ -v --cov=terraform_doc_extractor
```

## Note on Network Tests

These tests make real network requests to the Terraform Registry. Consider:
- Tests may be slow due to network latency
- Tests require internet connectivity
- Consider mocking for faster unit tests in the future

