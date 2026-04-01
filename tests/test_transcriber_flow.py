
import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

import t2
from main import SimpleVoiceTranscriber

class TestTranscriberFlow(unittest.TestCase):
    
    @patch('main.load_audio_config')
    @patch('main.VisualNotification')
    @patch('main.get_active_device_name')
    @patch('main.preload_model')
    @patch('main.WaylandGlobalHotkeys')
    def setUp(self, mock_hotkeys, mock_preload, mock_device_name, mock_notification, mock_load_config):
        self.transcriber = SimpleVoiceTranscriber()
        # Mocking for speed/isolation
        self.transcriber.visual_notification = MagicMock()
        self.transcriber.hotkey_system = MagicMock()

    def test_stop_recording_keyword_argument(self):
        """Test that stop_recording accepts copy_to_clipboard keyword argument"""
        self.transcriber.recording = True
        
        # Reset the event
        t2.stop_recording.clear()
        
        # This should NOT raise TypeError now
        try:
            self.transcriber.stop_recording(copy_to_clipboard=True)
        except TypeError as e:
            self.fail(f"stop_recording raised TypeError: {e}")
            
        self.assertFalse(self.transcriber.recording)
        self.assertTrue(self.transcriber.copy_to_clipboard)
        self.assertTrue(t2.stop_recording.is_set())

    def test_stop_recording_positional_argument(self):
        """Test that stop_recording accepts positional argument"""
        self.transcriber.recording = True
        t2.stop_recording.clear()
        
        self.transcriber.stop_recording(True)
        
        self.assertFalse(self.transcriber.recording)
        self.assertTrue(self.transcriber.copy_to_clipboard)
        self.assertTrue(t2.stop_recording.is_set())

    @patch('main.process_audio_stream')
    def test_process_recording_numpy_handling(self, mock_process):
        """Test that process_recording handles numpy arrays without ValueError"""
        import numpy as np
        
        mock_process.return_value = ("test transcription", 0.5)
        
        # Test empty array
        self.transcriber.audio_frames = np.array([])
        try:
            self.transcriber.process_recording()
        except ValueError as e:
            self.fail(f"process_recording raised ValueError with empty numpy array: {e}")
            
        # Test non-empty array
        self.transcriber.audio_frames = np.array([0.1, 0.2, 0.3])
        # Mocking pyperclip.copy to avoid actual clipboard access
        with patch('pyperclip.copy'):
            try:
                self.transcriber.process_recording()
            except ValueError as e:
                self.fail(f"process_recording raised ValueError with non-empty numpy array: {e}")

if __name__ == "__main__":
    unittest.main()
