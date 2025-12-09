#!/usr/bin/env python3
"""
Setup script for Mistral CLI
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="mistral-cli",
    version="1.0.0",
    author="Daniel Thun",
    author_email="",  # Optional: Ihre E-Mail hier einfügen
    description="Leistungsstarke CLI für Mistral AI mit erweiterten Tool-Funktionen",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/IHR-USERNAME/mistral-cli",  # Ersetzen Sie IHR-USERNAME
    py_modules=["mistral-cli"],
    scripts=["mistral"],
    install_requires=read_requirements(),
    extras_require={
        "full": [
            "Pillow>=10.0.0",  # Für Bildverarbeitung
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: POSIX :: Linux",
        "Environment :: Console",
    ],
    python_requires=">=3.8",
    keywords="mistral ai cli chatbot automation tools",
    project_urls={
        "Bug Reports": "https://github.com/IHR-USERNAME/mistral-cli/issues",
        "Source": "https://github.com/IHR-USERNAME/mistral-cli",
        "Documentation": "https://github.com/IHR-USERNAME/mistral-cli#readme",
    },
)
