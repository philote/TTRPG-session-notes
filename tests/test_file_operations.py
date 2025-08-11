"""
Tests for file operations utilities.
"""

import unittest
import tempfile
import os
import pandas as pd
import zipfile
from pathlib import Path

# Add shared_utils to path for testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared_utils.file_operations import (
    ensure_directory_exists,
    find_files_by_pattern,
    extract_zip_file,
    cleanup_temp_directory,
    load_tsv_file,
    save_dataframe,
    merge_csv_files,
    get_file_stats
)


class TestFileOperations(unittest.TestCase):
    """Test file operations utilities."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_files_dir = os.path.join(self.temp_dir, "test_files")
        os.makedirs(self.test_files_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_ensure_directory_exists(self):
        """Test directory creation."""
        new_dir = os.path.join(self.temp_dir, "new", "nested", "directory")
        result_path = ensure_directory_exists(new_dir)
        
        self.assertTrue(os.path.exists(new_dir))
        self.assertEqual(str(result_path), new_dir)
    
    def test_find_files_by_pattern(self):
        """Test finding files by pattern."""
        # Create test files
        test_files = ["test1.txt", "test2.txt", "data.csv", "audio.flac"]
        for filename in test_files:
            with open(os.path.join(self.test_files_dir, filename), 'w') as f:
                f.write("test content")
        
        # Find txt files
        txt_files = find_files_by_pattern(self.test_files_dir, "*.txt")
        self.assertEqual(len(txt_files), 2)
        
        # Find all files
        all_files = find_files_by_pattern(self.test_files_dir, "*")
        self.assertEqual(len(all_files), 4)
        
        # Find non-existent pattern
        no_files = find_files_by_pattern(self.test_files_dir, "*.xyz")
        self.assertEqual(len(no_files), 0)
    
    def test_extract_zip_file(self):
        """Test zip file extraction."""
        # Create a test zip file
        zip_path = os.path.join(self.temp_dir, "test.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.writestr("file1.txt", "content1")
            zipf.writestr("file2.txt", "content2")
            zipf.writestr("subdir/file3.txt", "content3")
        
        # Test extraction
        extract_path, is_temp = extract_zip_file(zip_path, temp_dir=True)
        
        self.assertTrue(is_temp)
        self.assertTrue(extract_path.exists())
        
        # Check extracted files
        extracted_files = list(extract_path.rglob("*.txt"))
        self.assertEqual(len(extracted_files), 3)
        
        # Clean up temp directory
        cleanup_temp_directory(extract_path)
        self.assertFalse(extract_path.exists())
    
    def test_load_tsv_file(self):
        """Test loading TSV files."""
        # Create test TSV file
        tsv_path = os.path.join(self.temp_dir, "test.tsv")
        test_data = pd.DataFrame({
            'start': [1.0, 2.0, 3.0],
            'end': [2.0, 3.0, 4.0],
            'text': ['Hello', 'world', 'test']
        })
        test_data.to_csv(tsv_path, sep='\t', index=False)
        
        # Load and verify
        loaded_df = load_tsv_file(tsv_path)
        self.assertEqual(len(loaded_df), 3)
        self.assertListEqual(list(loaded_df.columns), ['start', 'end', 'text'])
        self.assertEqual(loaded_df.iloc[0]['text'], 'Hello')
    
    def test_save_dataframe(self):
        """Test saving DataFrames in different formats."""
        test_df = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['a', 'b', 'c']
        })
        
        # Test CSV
        csv_path = os.path.join(self.temp_dir, "test.csv")
        save_dataframe(test_df, csv_path, format_type='csv')
        self.assertTrue(os.path.exists(csv_path))
        
        # Verify content
        loaded_df = pd.read_csv(csv_path)
        pd.testing.assert_frame_equal(test_df, loaded_df)
        
        # Test TSV
        tsv_path = os.path.join(self.temp_dir, "test.tsv")
        save_dataframe(test_df, tsv_path, format_type='tsv')
        self.assertTrue(os.path.exists(tsv_path))
        
        # Test JSON
        json_path = os.path.join(self.temp_dir, "test.json")
        save_dataframe(test_df, json_path, format_type='json')
        self.assertTrue(os.path.exists(json_path))
    
    def test_merge_csv_files(self):
        """Test merging CSV files."""
        # Create test CSV files
        df1 = pd.DataFrame({'start': [1, 2], 'text': ['hello', 'world']})
        df2 = pd.DataFrame({'start': [3, 4], 'text': ['foo', 'bar']})
        
        csv1_path = os.path.join(self.temp_dir, "file1.csv")
        csv2_path = os.path.join(self.temp_dir, "file2.csv")
        output_path = os.path.join(self.temp_dir, "merged.csv")
        
        df1.to_csv(csv1_path, index=False)
        df2.to_csv(csv2_path, index=False)
        
        # Merge files
        merged_df = merge_csv_files([csv1_path, csv2_path], output_path, sort_column='start')
        
        self.assertEqual(len(merged_df), 4)
        self.assertTrue(os.path.exists(output_path))
        self.assertIn('source_file', merged_df.columns)
        
        # Verify sorting
        start_values = merged_df['start'].tolist()
        self.assertEqual(start_values, sorted(start_values))
    
    def test_get_file_stats(self):
        """Test getting file statistics."""
        # Test with existing file
        test_file = os.path.join(self.temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        stats = get_file_stats(test_file)
        
        self.assertTrue(stats["exists"])
        self.assertTrue(stats["is_file"])
        self.assertFalse(stats["is_directory"])
        self.assertGreater(stats["size_bytes"], 0)
        self.assertEqual(stats["extension"], ".txt")
        self.assertEqual(stats["name"], "test.txt")
        
        # Test with non-existent file
        missing_stats = get_file_stats("nonexistent.txt")
        self.assertFalse(missing_stats["exists"])


if __name__ == '__main__':
    unittest.main()