"""
Easix - A Modern Django Admin Framework
Setup configuration for pip installation.
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = ""
if readme_path.exists():
    long_description = readme_path.read_text(encoding="utf-8")

setup(
    name="easix-admin",
    version="1.0.0",
    author="Easix Team",
    author_email="hello@easix.dev",
    description="A modern, user-friendly Django admin framework for non-technical users",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/easix-admin/easix",
    project_urls={
        "Documentation": "https://easix.dev/docs",
        "Bug Tracker": "https://github.com/easix-admin/easix/issues",
        "Source Code": "https://github.com/easix-admin/easix",
    },
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.0",
        "Framework :: Django :: 5.1",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: User Interfaces",
    ],
    keywords="django admin framework easix dashboard crud htmx alpine tailwind",
    python_requires=">=3.9",
    install_requires=[
        "Django>=4.2",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-django",
            "black",
            "ruff",
            "pre-commit",
        ],
    },
    entry_points={
        "console_scripts": [
            "easix=easix.management.commands.easix:main",
        ],
    },
    zip_safe=False,
    license="MIT",
    license_files=["LICENSE"],
)
