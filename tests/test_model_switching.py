#!/usr/bin/env python3
"""
Test file to verify model switching between Cohere and Whisper backends.
"""

import sys
import os
import unittest
import json
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

import transcribe2
import t2

class TestModelSwitching(unittest.TestCase):
    
    def setUp(self):
        # Reset backend state
        transcribe2._backend = None
        transcribe2._current_backend_name = "cohere"

    @patch('importlib.import_module')
    def test_get_backend_cohere(self, mock_import):
        """Test getting Cohere backend"""
        mock_cohere = MagicMock()
        mock_import.return_value = mock_cohere
        
        backend = transcribe2.get_backend()
        
        mock_import.assert_called_with("transcribe_cohere")
        self.assertEqual(backend, mock_cohere)
        self.assertEqual(transcribe2._current_backend_name, "cohere")

    @patch('importlib.import_module')
    def test_set_backend_whisper(self, mock_import):
        """Test switching to Whisper backend"""
        mock_cohere = MagicMock()
        mock_whisper = MagicMock()
        
        # Initial state (cohere)
        mock_import.return_value = mock_cohere
        transcribe2.get_backend()
        
        # Switch to whisper
        mock_import.return_value = mock_whisper
        transcribe2.set_backend("whisper")
        
        # Check if old backend was unloaded
        mock_cohere.unload_model.assert_called_once()
        
        # Check new backend
        backend = transcribe2.get_backend()
        mock_import.assert_called_with("transcribe_whisper")
        self.assertEqual(backend, mock_whisper)
        self.assertEqual(transcribe2._current_backend_name, "whisper")

    @patch('transcribe2.set_backend')
    @patch('t2.save_audio_config')
    def test_t2_config_loading(self, mock_save, mock_set_backend):
        """Test if t2 loads model_backend from config"""
        config_data = {
            'model_backend': 'whisper',
            'input_device_index': 0
        }
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', unittest.mock.mock_open(read_data=json.dumps(config_data))):
                t2.load_audio_config()
                
        self.assertEqual(t2.MODEL_BACKEND, 'whisper')
        mock_set_backend.assert_called_with('whisper')

if __name__ == "__main__":
    unittest.main()
