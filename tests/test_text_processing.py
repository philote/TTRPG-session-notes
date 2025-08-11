"""
Tests for text processing utilities.
"""

import unittest
import tempfile
import json
import os
import pandas as pd
from pathlib import Path

# Add shared_utils to path for testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared_utils.text_processing import (
    load_replacements_file,
    apply_text_replacements,
    remove_duplicate_short_text,
    merge_adjacent_segments,
    remove_short_text,
    split_text_with_overlap,
    clean_transcript_dataframe
)


class TestTextProcessing(unittest.TestCase):
    """Test text processing utilities."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.replacements_file = os.path.join(self.temp_dir, "test_replacements.json")
        
        # Create test replacements file
        test_replacements = {
            "Gandalf": ["gandolf", "gandulf", "gandif"],
            "Frodo": ["froto", "frodo baggins", "mr frodo"]
        }
        with open(self.replacements_file, 'w') as f:
            json.dump(test_replacements, f)
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.replacements_file):
            os.remove(self.replacements_file)
        os.rmdir(self.temp_dir)
    
    def test_load_replacements_file(self):
        """Test loading replacements from JSON file."""
        replacements = load_replacements_file(self.replacements_file)
        
        self.assertIn("Gandalf", replacements)
        self.assertIn("Frodo", replacements)
        self.assertEqual(len(replacements["Gandalf"]), 3)
        self.assertIn("gandolf", replacements["Gandalf"])
    
    def test_load_replacements_file_missing(self):
        """Test loading non-existent replacements file."""
        replacements = load_replacements_file("nonexistent.json")
        self.assertEqual(replacements, {})
    
    def test_apply_text_replacements(self):
        """Test applying text replacements."""
        text = "gandolf spoke to froto about the ring"
        replacements = {
            "Gandalf": ["gandolf"],
            "Frodo": ["froto"]
        }
        
        result_text, counts = apply_text_replacements(text, replacements)
        
        self.assertEqual(result_text, "Gandalf spoke to Frodo about the ring")
        self.assertEqual(counts["Gandalf"]["gandolf"], 1)
        self.assertEqual(counts["Frodo"]["froto"], 1)
    
    def test_apply_text_replacements_case_insensitive(self):
        """Test case-insensitive text replacements."""
        text = "GANDOLF and gandolf and Gandolf"
        replacements = {"Gandalf": ["gandolf"]}
        
        result_text, counts = apply_text_replacements(text, replacements, case_insensitive=True)
        
        self.assertEqual(result_text, "Gandalf and Gandalf and Gandalf")
        self.assertEqual(counts["Gandalf"]["gandolf"], 3)
    
    def test_remove_duplicate_short_text(self):
        """Test removing duplicate short text entries."""
        df = pd.DataFrame({
            'text': ['hi', 'hi', 'hello there', 'ok', 'ok', 'longer text here'],
            'start': [1, 2, 3, 4, 5, 6],
            'end': [2, 3, 4, 5, 6, 7]
        })
        
        result_df, removed_count = remove_duplicate_short_text(df, max_length=3)
        
        # Should remove duplicate 'hi' and 'ok' entries
        self.assertEqual(removed_count, 2)
        self.assertEqual(len(result_df), 4)
        
        # Check that we kept first occurrence of each
        text_values = result_df['text'].tolist()
        self.assertEqual(text_values.count('hi'), 1)
        self.assertEqual(text_values.count('ok'), 1)
    
    def test_merge_adjacent_segments(self):
        """Test merging adjacent segments."""
        df = pd.DataFrame({
            'text': ['Hello', 'world', 'How', 'are', 'you'],
            'start': [1.0, 2.0, 3.5, 4.0, 5.5],
            'end': [2.0, 3.0, 4.0, 5.0, 6.0]
        })
        
        result_df, merge_count = merge_adjacent_segments(df, threshold=0.1)
        
        # Should merge segments where end time is close to next start time
        self.assertGreater(merge_count, 0)
        self.assertLess(len(result_df), len(df))
        
        # Check that text was combined
        merged_texts = result_df['text'].tolist()
        self.assertTrue(any(' ' in text for text in merged_texts))
    
    def test_remove_short_text(self):
        """Test removing short text entries."""
        df = pd.DataFrame({
            'text': ['a', 'hello', 'hi', 'this is longer text', ''],
            'start': [1, 2, 3, 4, 5],
            'end': [2, 3, 4, 5, 6]
        })
        
        result_df, removed_count = remove_short_text(df, min_length=2)
        
        # Should remove 'a', '', and potentially 'hi' depending on length
        self.assertGreater(removed_count, 0)
        self.assertLess(len(result_df), len(df))
        
        # Check that remaining text is longer than minimum
        for text in result_df['text']:
            self.assertGreater(len(text), 2)
    
    def test_split_text_with_overlap(self):
        """Test splitting text with overlap."""
        # Create a long text
        text = "This is a sentence. " * 100  # About 2000 characters
        
        chunks = split_text_with_overlap(text, max_length=500, overlap=50)
        
        # Should split into multiple chunks
        self.assertGreater(len(chunks), 1)
        
        # Each chunk should be roughly the right length
        for chunk in chunks[:-1]:  # All but last chunk
            self.assertLessEqual(len(chunk), 500)
        
        # Check that there's overlap between chunks
        if len(chunks) > 1:
            # Look for common text between adjacent chunks
            chunk1_end = chunks[0][-50:]
            chunk2_start = chunks[1][:50]
            # There should be some overlap (not exact due to word boundaries)
            common_words = set(chunk1_end.split()) & set(chunk2_start.split())
            self.assertGreater(len(common_words), 0)
    
    def test_split_text_short(self):
        """Test splitting text that doesn't need splitting."""
        short_text = "This is a short text."
        chunks = split_text_with_overlap(short_text, max_length=1000, overlap=100)
        
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], short_text)
    
    def test_clean_transcript_dataframe(self):
        """Test the full cleaning pipeline."""
        df = pd.DataFrame({
            'text': ['hi', 'hi', 'hello there', 'a', 'longer text here', 'um', 'good content'],
            'start': [1.0, 1.1, 2.0, 3.0, 4.0, 5.0, 6.0],
            'end': [1.5, 1.6, 2.5, 3.5, 4.5, 5.5, 6.5]
        })
        
        config_dict = {
            'short_duplicate_text_length': 3,
            'merge_threshold': 0.2,
            'short_text_length': 2,
            'remove_silence_gibberish': True,
            'silence_gibberish_patterns': ['um', 'uh']
        }
        
        result_df = clean_transcript_dataframe(df, config_dict)
        
        # Should be fewer rows after cleaning
        self.assertLess(len(result_df), len(df))
        
        # Check that gibberish was removed
        remaining_text = result_df['text'].tolist()
        self.assertNotIn('um', remaining_text)
        
        # Check that very short text was removed
        for text in remaining_text:
            self.assertGreater(len(text), 2)


if __name__ == '__main__':
    unittest.main()