import pytest
import os
import sys
from unittest.mock import patch, MagicMock

# Ensure we can import the dashboard pages
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.mark.asyncio
async def test_dashboard_imports():
    """Verify that all dashboard pages import successfully without tracebacks."""
    # We mock streamlit to prevent it from actually launching the UI or caching in tests
    with patch("streamlit.set_page_config"):
        with patch("streamlit.sidebar"):
            with patch("streamlit.cache_data", lambda *args, **kwargs: lambda f: f):
                import dashboard.app
                import dashboard.pages.1_Overview
                import dashboard.pages.2_Research
                import dashboard.pages.3_Startups
                import dashboard.pages.4_Products
                import dashboard.pages.5_Fresh_Signals
                import dashboard.pages.6_Entity_Resolution
                import dashboard.pages.7_Pipeline_Monitor
                import dashboard.pages.8_Architecture

    # If it reached here without ImportError or SyntaxError, we are good.
    assert True
