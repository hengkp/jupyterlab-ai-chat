"""
Simplified setup module for jupyterlab-ai-chat extension
This version works without jupyter_packaging for basic Python-only installation
"""

import json
import os
from pathlib import Path
import setuptools

HERE = Path(__file__).parent.resolve()

# Get package info from package.json
pkg_json = HERE / "package.json"
with pkg_json.open() as f:
    pkg_info = json.load(f)

pkg_info["author"] = "hengkp"
pkg_info["author_email"] = ""

long_description = (HERE / "README.md").read_text()

setup_args = dict(
    name=pkg_info["name"],
    version=pkg_info["version"],
    url=pkg_info["homepage"],
    author=pkg_info["author"],
    author_email=pkg_info["author_email"],
    description=pkg_info["description"],
    license=pkg_info["license"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=[
        "jupyter_server>=1.6,<3",
        "jupyterlab>=3.1.0,<4.0.0a0",
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "transformers>=4.20.0",
        "torch>=1.12.0",
        "requests>=2.25.0",
        "python-multipart>=0.0.5",
        "aiofiles>=0.7.0",
    ],
    extras_require={
        "dev": [
            "jupyter_packaging~=0.10",
            "jupyterlab~=3.1",
        ]
    },
    zip_safe=False,
    include_package_data=True,
    python_requires=">=3.7",
    platforms="Linux, Mac OS X, Windows",
    keywords=["Jupyter", "JupyterLab", "JupyterLab3"],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Framework :: Jupyter",
        "Framework :: Jupyter :: JupyterLab",
        "Framework :: Jupyter :: JupyterLab :: 3",
        "Framework :: Jupyter :: JupyterLab :: Extensions",
        "Framework :: Jupyter :: JupyterLab :: Extensions :: Prebuilt",
    ],
)

if __name__ == "__main__":
    setuptools.setup(**setup_args) 