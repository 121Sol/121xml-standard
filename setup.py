#!/usr/bin/env python
# © 2026 121 Solutions USA. All rights reserved.
#
# The trademarks 121XQ, 121XML, and 121MetaVerse are the exclusive
# property of 121 Solutions USA.
#
# Unauthorized use, reproduction, or distribution of this material,
# including any proprietary designs, software, or documentation, is
# strictly prohibited without prior written permission from 121 Solutions USA.
"""
121AI Setup Script
Universal AI Orchestration Platform
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read version
version_file = this_directory / "121ai" / "__version__.py"
version = "1.0.0"
if version_file.exists():
    with open(version_file) as f:
        for line in f:
            if line.startswith("__version__"):
                version = line.split('"')[1]
                break

setup(
    name="121ai",
    version=version,
    description="121AI - Universal AI Orchestration Platform with Zero Vendor Lock-in",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Rashad Khan",
    author_email="rashad@121.us",
    url="https://github.com/rashadkhan/121ai",
    license="MIT",

    # Classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Enterprise",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
    ],

    python_requires=">=3.9",

    # Packages
    packages=find_packages(exclude=["tests", "tests.*", "deployment", "docs"]),
    include_package_data=True,

    # Core dependencies
    install_requires=[
        # Web Framework
        "fastapi>=0.95.0",
        "uvicorn[standard]>=0.21.0",
        "pydantic>=2.0",
        "pydantic-settings>=2.0",

        # Database
        "sqlalchemy>=2.0",
        "psycopg2-binary>=2.9",  # PostgreSQL
        "pymongo>=4.0",           # MongoDB
        "boto3>=1.26",            # DynamoDB/AWS
        "redis>=4.0",             # Redis

        # Async
        "aiohttp>=3.8",
        "httpx>=0.23",

        # AI/ML
        "openai>=1.0",
        "anthropic>=0.7",
        "google-generativeai>=0.3",
        "requests>=2.28",

        # Cryptography & Security
        "cryptography>=38.0",
        "python-jose[cryptography]>=3.3",
        "passlib[bcrypt]>=1.7",
        "pyjwt>=2.6",
        "hvac>=1.0",  # HashiCorp Vault

        # Data Processing
        "numpy>=1.21",
        "pandas>=1.3",
        "pyyaml>=6.0",
        "toml>=0.10",
        "json5>=0.9",

        # Monitoring & Logging
        "prometheus-client>=0.15",
        "python-json-logger>=2.0",
        "opentelemetry-api>=1.0",
        "opentelemetry-sdk>=1.0",
        "opentelemetry-instrumentation>=0.35",

        # Utilities
        "click>=8.0",  # CLI
        "rich>=13.0",  # Terminal formatting
        "python-dotenv>=0.19",
        "tzlocal>=4.0",
        "python-dateutil>=2.8",
    ],

    # Optional dependencies by extras
    extras_require={
        "web": [
            "uvicorn[standard]>=0.21.0",
            "python-multipart>=0.0.5",
            "starlette-cors>=0.0.6",
            "gunicorn>=20.1",
            "whitenoise>=6.2",
        ],

        "mobile": [
            "kivy>=2.1",
            "kivy-garden>=0.1",
            "pyobjc>=9.0;platform_system=='Darwin'",  # iOS on macOS
        ],

        "desktop": [
            "pyinstaller>=5.0",
            "pyinstaller-hooks-contrib>=2022.0",
            "tkinter;platform_system=='Windows'",
        ],

        "database": [
            "psycopg2-binary>=2.9",
            "pymongo>=4.0",
            "boto3>=1.26",
            "pymysql>=1.0",
            "cx-Oracle>=8.0;platform_system!='Windows'",
        ],

        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "pytest-asyncio>=0.20",
            "pytest-mock>=3.10",
            "hypothesis>=6.0",
            "black>=23.0",
            "flake8>=5.0",
            "mypy>=1.0",
            "isort>=5.11",
            "pre-commit>=3.0",
            "sphinx>=5.0",
            "sphinx-rtd-theme>=1.0",
        ],

        "docker": [
            "docker>=5.0",
        ],

        "kubernetes": [
            "kubernetes>=24.0",
        ],
    },

    # Scripts
    entry_points={
        "console_scripts": [
            "121ai=121ai.cli:main",
            "121ai-config=121ai.cli.config:main",
            "121ai-deploy=121ai.cli.deploy:main",
        ],
    },

    # URLs
    project_urls={
        "Documentation": "https://121ai.readthedocs.io",
        "Source Code": "https://github.com/rashadkhan/121ai",
        "Issue Tracker": "https://github.com/rashadkhan/121ai/issues",
        "Changelog": "https://github.com/rashadkhan/121ai/releases",
    },

    # Package data
    package_data={
        "121ai": [
            "ui/**/*",
            "mobile/**/*",
            "config/**/*",
        ],
    },
)
