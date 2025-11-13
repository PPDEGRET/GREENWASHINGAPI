import pytest
from unittest.mock import patch, MagicMock
import sys
import importlib


class TestMainStartup:
    """Test cases for main.py startup behavior."""
    
    @patch('dotenv.load_dotenv')
    def test_main_loads_dotenv_at_startup(self, mock_load_dotenv):
        """Test case 5: Verify that main.py successfully loads environment variables using load_dotenv() at startup."""
        # Remove the module from sys.modules if it's already loaded to force reimport
        if 'src.app.main' in sys.modules:
            del sys.modules['src.app.main']
        
        # Mock the router import to avoid side effects
        with patch.dict(sys.modules, {'src.app.routers.analysis': MagicMock()}):
            # Import the main module (this triggers load_dotenv() at module level)
            import src.app.main
            
            # Verify that load_dotenv was called during module import
            mock_load_dotenv.assert_called()
            
            # Verify it was called at least once (could be called from both gpt_service and main)
            assert mock_load_dotenv.call_count >= 1
    
    def test_main_module_imports_successfully(self):
        """Verify that the main module can be imported without errors."""
        # This test ensures the module structure is correct
        try:
            if 'src.app.main' in sys.modules:
                importlib.reload(sys.modules['src.app.main'])
            else:
                import src.app.main
            success = True
        except Exception as e:
            success = False
            pytest.fail(f"Failed to import main module: {e}")
        
        assert success
