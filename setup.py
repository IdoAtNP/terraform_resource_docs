"""Setup configuration for terraform-resource-documentation package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="terraform-resource-documentation",
    version="0.1.0",
    author="NPLabs",
    description="Extract and format documentation from Terraform provider resources",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/IdoAtNP/terraform_resource_docs",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "terraform-resource-docs=terraform_doc_extractor.cli:main",
        ],
    },
)

