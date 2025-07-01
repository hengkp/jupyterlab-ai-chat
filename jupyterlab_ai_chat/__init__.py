"""
JupyterLab AI Chat Extension

A JupyterLab extension that adds AI Chat functionality with local LLM support.
"""

__version__ = "0.1.0"

def _jupyter_labextension_paths():
    """Called by Jupyter Lab to find the extension assets"""
    return [{
        'src': 'labextension',
        'dest': 'jupyterlab-ai-chat'
    }]

def _jupyter_server_extension_points():
    """Called by Jupyter Server to find the extension entry point"""
    return [{
        'module': 'jupyterlab_ai_chat'
    }]

def _load_jupyter_server_extension(server_app):
    """Load the server extension"""
    from .handlers import setup_handlers
    setup_handlers(server_app)

# For compatibility with older Jupyter versions
load_jupyter_server_extension = _load_jupyter_server_extension 