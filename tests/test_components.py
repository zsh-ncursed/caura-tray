"""
Basic unit tests for the Tray Launcher application components.
"""

import unittest
import tempfile
import os
from pathlib import Path
import json
from unittest.mock import patch, MagicMock

from storage.config_manager import ConfigManager
from parser.desktop_parser import DesktopParser
from launcher_logic import ApplicationLauncher


class TestConfigManager(unittest.TestCase):
    """
    Tests for ConfigManager class.
    """
    
    def setUp(self):
        """
        Set up test environment with a temporary config file.
        """
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_config.json"
        
    def tearDown(self):
        """
        Clean up test environment.
        """
        # Remove the temporary config file
        if self.config_path.exists():
            os.remove(self.config_path)
        
        # Remove the temporary directory
        os.rmdir(self.temp_dir)
    
    def test_load_default_config(self):
        """
        Test loading default configuration when file doesn't exist.
        """
        config_manager = ConfigManager(self.config_path)
        
        expected_default = {"categories": {}}
        self.assertEqual(config_manager.config, expected_default)
        self.assertTrue(self.config_path.exists())
    
    def test_save_and_load_config(self):
        """
        Test saving and loading configuration.
        """
        config_manager = ConfigManager(self.config_path)
        
        # Modify config
        test_config = {
            "categories": {
                "Test Category": [
                    {"name": "Test App", "cmd": "test_command"}
                ]
            }
        }
        config_manager.config = test_config
        config_manager.save_config()
        
        # Load config again to verify it was saved correctly
        config_manager2 = ConfigManager(self.config_path)
        self.assertEqual(config_manager2.config, test_config)
    
    def test_add_application_to_category(self):
        """
        Test adding an application to a category.
        """
        config_manager = ConfigManager(self.config_path)
        
        # Add an application
        app_info = {"name": "Test App", "cmd": "test_command"}
        config_manager.add_application_to_category("Test Category", app_info)
        
        expected = {
            "categories": {
                "Test Category": [app_info]
            }
        }
        self.assertEqual(config_manager.config, expected)
    
    def test_add_duplicate_application(self):
        """
        Test that adding a duplicate application doesn't create duplicates.
        """
        config_manager = ConfigManager(self.config_path)
        
        # Add the same application twice
        app_info = {"name": "Test App", "cmd": "test_command"}
        config_manager.add_application_to_category("Test Category", app_info)
        config_manager.add_application_to_category("Test Category", app_info)
        
        # Should only have one instance
        category_apps = config_manager.config["categories"]["Test Category"]
        self.assertEqual(len(category_apps), 1)
        self.assertEqual(category_apps[0], app_info)
    
    def test_remove_application_from_category(self):
        """
        Test removing an application from a category.
        """
        config_manager = ConfigManager(self.config_path)
        
        # Add applications
        app1 = {"name": "App 1", "cmd": "cmd1"}
        app2 = {"name": "App 2", "cmd": "cmd2"}
        config_manager.add_application_to_category("Test Category", app1)
        config_manager.add_application_to_category("Test Category", app2)
        
        # Remove one application
        config_manager.remove_application_from_category("Test Category", "App 1")
        
        remaining_apps = config_manager.config["categories"]["Test Category"]
        self.assertEqual(len(remaining_apps), 1)
        self.assertEqual(remaining_apps[0]["name"], "App 2")


class TestDesktopParser(unittest.TestCase):
    """
    Tests for DesktopParser class.
    """
    
    def setUp(self):
        """
        Set up test environment.
        """
        self.parser = DesktopParser()
        
        # Create a temporary .desktop file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.desktop', delete=False)
        self.temp_file.write("""[Desktop Entry]
Name=Test Application
Exec=/usr/bin/test-app %U
Icon=test-icon
Type=Application
Categories=Utility;
NoDisplay=false
""")
        self.temp_file.close()
    
    def tearDown(self):
        """
        Clean up test environment.
        """
        os.unlink(self.temp_file.name)
    
    def test_clean_exec_command(self):
        """
        Test cleaning exec command by removing placeholders.
        """
        original_cmd = "/usr/bin/test-app %U %f %F"
        expected = "/usr/bin/test-app"
        
        result = self.parser.clean_exec_command(original_cmd)
        self.assertEqual(result, expected)
    
    def test_parse_desktop_file(self):
        """
        Test parsing a .desktop file.
        """
        result = self.parser.parse_desktop_file(self.temp_file.name)
        
        expected = {
            "name": "Test Application",
            "cmd": "/usr/bin/test-app",
            "icon": "test-icon",
            "nodisplay": False
        }
        
        self.assertEqual(result, expected)
    
    def test_parse_desktop_file_nodisplay_true(self):
        """
        Test parsing a .desktop file with NoDisplay=true.
        """
        # Create a temporary file with NoDisplay=true
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.desktop', delete=False)
        temp_file.write("""[Desktop Entry]
Name=Hidden Application
Exec=/usr/bin/hidden-app
NoDisplay=true
""")
        temp_file.close()
        
        try:
            result = self.parser.parse_desktop_file(temp_file.name)
            # Should return None because NoDisplay=true
            self.assertIsNone(result)
        finally:
            os.unlink(temp_file.name)


class TestApplicationLauncher(unittest.TestCase):
    """
    Tests for ApplicationLauncher class.
    """
    
    def setUp(self):
        """
        Set up test environment.
        """
        self.launcher = ApplicationLauncher()
    
    def test_validate_command_safe(self):
        """
        Test validating a safe command.
        """
        safe_command = "ls -la"
        result = self.launcher.validate_command(safe_command)
        self.assertTrue(result)
    
    def test_validate_command_empty(self):
        """
        Test validating an empty command.
        """
        empty_command = ""
        result = self.launcher.validate_command(empty_command)
        self.assertFalse(result)
    
    def test_validate_command_dangerous(self):
        """
        Test validating a potentially dangerous command.
        """
        dangerous_command = "rm -rf /"
        result = self.launcher.validate_command(dangerous_command)
        self.assertFalse(result)
    
    @patch('subprocess.Popen')
    def test_launch_application_success(self, mock_popen):
        """
        Test launching an application successfully (mocked).
        """
        # Mock the subprocess.Popen to avoid actually launching anything
        mock_process = MagicMock()
        mock_popen.return_value = mock_process
        
        result = self.launcher.launch_application("echo test")
        self.assertTrue(result)
    
    def test_launch_with_validation(self):
        """
        Test launching with validation.
        """
        with patch.object(self.launcher, 'validate_command', return_value=True):
            with patch.object(self.launcher, 'launch_application', return_value=True):
                result = self.launcher.launch_with_validation("echo test")
                self.assertTrue(result)


if __name__ == '__main__':
    # Run the tests
    unittest.main()