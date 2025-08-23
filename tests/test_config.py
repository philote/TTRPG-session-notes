"""
Tests for shared configuration system.
"""

import unittest
import tempfile
import json
import os
from pathlib import Path

# Add shared_utils to path for testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared_utils.config import SharedConfig, get_shared_config


class TestSharedConfig(unittest.TestCase):
    """Test the SharedConfig class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        os.rmdir(self.temp_dir)
    
    def test_default_initialization(self):
        """Test that default configuration loads correctly."""
        config = SharedConfig()
        
        # Test whisper defaults
        self.assertEqual(config.whisper["model"], "turbo")
        self.assertEqual(config.whisper["language"], "en")
        self.assertFalse(config.whisper["condition_on_previous_text"])
        
        # Test cleanup defaults
        self.assertEqual(config.cleanup["session_name"], "sessions")
        self.assertEqual(config.cleanup["part"], "test")
        self.assertTrue(config.cleanup["remove_silence_gibberish"])
        
        # Test name mappings
        self.assertIn("ephson", config.name_mappings)
        self.assertTrue(len(config.silence_patterns) > 0)
    
    def test_config_file_loading(self):
        """Test loading configuration from JSON file."""
        test_config = {
            "whisper": {"model": "large-v2", "language": "es"},
            "cleanup": {"session_name": "test_session", "part": "one"},
            "name_mappings": {"test_user": "Test Character"}
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(test_config, f)
        
        config = SharedConfig(config_file=self.config_file)
        
        # Verify overrides were applied
        self.assertEqual(config.whisper["model"], "large-v2")
        self.assertEqual(config.whisper["language"], "es")
        self.assertEqual(config.cleanup["session_name"], "test_session")
        self.assertEqual(config.cleanup["part"], "one")
        self.assertIn("test_user", config.name_mappings)
    
    def test_environment_variable_loading(self):
        """Test loading configuration from environment variables."""
        # Set test environment variables
        os.environ["TTRPG_WHISPER_MODEL"] = "large-v3"
        os.environ["TTRPG_WHISPER_LANGUAGE"] = "fr"
        os.environ["TTRPG_SESSION_NAME"] = "env_session"
        os.environ["TTRPG_WHISPER_FP16"] = "false"
        
        try:
            config = SharedConfig()
            
            # Verify environment variables were loaded
            self.assertEqual(config.whisper["model"], "large-v3")
            self.assertEqual(config.whisper["language"], "fr")
            self.assertEqual(config.cleanup["session_name"], "env_session")
            self.assertFalse(config.whisper["fp16"])
        
        finally:
            # Clean up environment variables
            for var in ["TTRPG_WHISPER_MODEL", "TTRPG_WHISPER_LANGUAGE", 
                       "TTRPG_SESSION_NAME", "TTRPG_WHISPER_FP16"]:
                if var in os.environ:
                    del os.environ[var]
    
    def test_computed_defaults(self):
        """Test that computed default values are set correctly."""
        config = SharedConfig()
        
        # Test base_path computation
        expected_path = os.path.join(
            config.project_root,
            config.cleanup["session_name"],
            config.cleanup["part"]
        )
        self.assertEqual(config.cleanup["base_path"], expected_path)
        
        # Test filename methods
        self.assertTrue(config.get_combined_csv_filename().endswith("_processed.csv"))
        self.assertTrue(config.get_merged_csv_filename().endswith("_merged.csv"))
        self.assertTrue(config.get_final_txt_filename().endswith("_final.txt"))
    
    def test_save_and_load_config(self):
        """Test saving and loading configuration."""
        config = SharedConfig()
        
        # Modify some values
        config.whisper["model"] = "test-model"
        config.cleanup["session_name"] = "saved_session"
        
        # Save configuration
        config.save_to_file(self.config_file)
        self.assertTrue(os.path.exists(self.config_file))
        
        # Load saved configuration
        new_config = SharedConfig(config_file=self.config_file)
        
        # Verify saved values were loaded
        self.assertEqual(new_config.whisper["model"], "test-model")
        self.assertEqual(new_config.cleanup["session_name"], "saved_session")
    
    def test_get_shared_config_function(self):
        """Test the convenience function for getting config."""
        config = get_shared_config()
        self.assertIsInstance(config, SharedConfig)
        
        # Test with config file
        test_config = {"whisper": {"model": "convenience-test"}}
        with open(self.config_file, 'w') as f:
            json.dump(test_config, f)
        
        config = get_shared_config(config_file=self.config_file)
        self.assertEqual(config.whisper["model"], "convenience-test")


if __name__ == '__main__':
    unittest.main()