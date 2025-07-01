"""
Setup module for jupyterlab-ai-chat extension
"""

import json
import os
from pathlib import Path

try:
    from jupyter_packaging import (
        create_cmdclass,
        install_npm,
        ensure_targets,
        combine_commands,
        skip_if_exists
    )
    HAS_JUPYTER_PACKAGING = True
except ImportError:
    HAS_JUPYTER_PACKAGING = False
    print("Warning: jupyter_packaging not found. Installing without frontend build.")

import setuptools

HERE = Path(__file__).parent.resolve()

# Get package info from package.json
pkg_json = HERE / "package.json"
with pkg_json.open() as f:
    pkg_info = json.load(f)

pkg_info["author"] = "hengkp"
pkg_info["author_email"] = ""

lab_path = HERE / pkg_info["name"] / "labextension"

# Representative files that should exist after a successful build
jstargets = [
    str(lab_path / "package.json"),
]

package_data_spec = {
    pkg_info["name"]: ["*"],
}

labext_name = "jupyterlab-ai-chat"

data_files_spec = [
    ("share/jupyter/labextensions/%s" % labext_name, lab_path, "**"),
    ("share/jupyter/labextensions/%s" % labext_name, HERE, "install.json"),
    ("etc/jupyter/jupyter_server_config.d", "jupyter-config/jupyter_server_config.d", "jupyterlab_ai_chat.json"),
]

if HAS_JUPYTER_PACKAGING:
    cmdclass = create_cmdclass("jsdeps", package_data_spec=package_data_spec, data_files_spec=data_files_spec)

    js_command = combine_commands(
        install_npm(HERE, build_cmd="build:prod", npm=["jlpm"]),
        ensure_targets(jstargets),
    )

    is_repo = (HERE / ".git").exists()
    if is_repo:
        cmdclass["jsdeps"] = js_command
    else:
        cmdclass["jsdeps"] = skip_if_exists(jstargets, js_command)
else:
    cmdclass = {}

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
    cmdclass=cmdclass,
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