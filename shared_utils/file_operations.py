"""
Common file operations utilities for TTRPG Session Notes automation.
Contains functions for handling files, directories, and data I/O.
"""

import os
import shutil
import zipfile
import tempfile
import pandas as pd
from pathlib import Path
from typing import List, Optional, Union, Tuple, Dict, Any
import logging

from .logging_config import get_logger

def ensure_directory_exists(directory_path: Union[str, Path], 
                           create_parents: bool = True) -> Path:
    """Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
        create_parents: Whether to create parent directories
    
    Returns:
        Path object for the directory
    """
    path = Path(directory_path)
    path.mkdir(parents=create_parents, exist_ok=True)
    return path

def find_files_by_pattern(directory: Union[str, Path],
                         pattern: str,
                         recursive: bool = False) -> List[Path]:
    """Find files matching a pattern in a directory.
    
    Args:
        directory: Directory to search in
        pattern: File pattern (e.g., "*.tsv", "*.flac")
        recursive: Whether to search subdirectories
    
    Returns:
        List of matching file paths
    """
    logger = get_logger()
    path = Path(directory)
    
    if not path.exists():
        logger.warning(f"Directory not found: {path}")
        return []
    
    if recursive:
        files = list(path.rglob(pattern))
    else:
        files = list(path.glob(pattern))
    
    logger.debug(f"Found {len(files)} files matching '{pattern}' in {path}")
    return files

def extract_zip_file(zip_path: Union[str, Path],
                    extract_to: Optional[Union[str, Path]] = None,
                    temp_dir: bool = False) -> Tuple[Path, bool]:
    """Extract a zip file to a directory.
    
    Args:
        zip_path: Path to the zip file
        extract_to: Directory to extract to (if None, uses zip file directory)
        temp_dir: Whether to create a temporary directory for extraction
    
    Returns:
        Tuple of (extraction_path, is_temp_dir)
    """
    logger = get_logger()
    zip_path = Path(zip_path)
    
    if not zip_path.exists():
        raise FileNotFoundError(f"Zip file not found: {zip_path}")
    
    if temp_dir:
        extract_path = Path(tempfile.mkdtemp(prefix="ttrpg_extract_"))
        is_temp = True
    elif extract_to:
        extract_path = Path(extract_to)
        is_temp = False
    else:
        extract_path = zip_path.parent / zip_path.stem
        is_temp = False
    
    ensure_directory_exists(extract_path)
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        
        extracted_files = list(extract_path.rglob("*"))
        logger.info(f"Extracted {len(extracted_files)} files from {zip_path.name} to {extract_path}")
        
    except Exception as e:
        if is_temp:
            cleanup_temp_directory(extract_path)
        raise RuntimeError(f"Failed to extract {zip_path}: {e}")
    
    return extract_path, is_temp

def cleanup_temp_directory(temp_path: Union[str, Path]):
    """Clean up a temporary directory.
    
    Args:
        temp_path: Path to the temporary directory
    """
    logger = get_logger()
    temp_path = Path(temp_path)
    
    if temp_path.exists() and temp_path.is_dir():
        try:
            shutil.rmtree(temp_path)
            logger.debug(f"Cleaned up temporary directory: {temp_path}")
        except Exception as e:
            logger.warning(f"Failed to clean up temporary directory {temp_path}: {e}")

def copy_default_config_if_missing(default_file: Union[str, Path],
                                  target_file: Union[str, Path],
                                  overwrite: bool = False) -> bool:
    """Copy a default configuration file if the target doesn't exist.
    
    Args:
        default_file: Path to the default configuration file
        target_file: Path to the target configuration file
        overwrite: Whether to overwrite existing target file
    
    Returns:
        True if file was copied, False otherwise
    """
    logger = get_logger()
    default_path = Path(default_file)
    target_path = Path(target_file)
    
    if not default_path.exists():
        logger.error(f"Default config file not found: {default_path}")
        return False
    
    if target_path.exists() and not overwrite:
        logger.debug(f"Target config file already exists: {target_path}")
        return False
    
    try:
        shutil.copy2(default_path, target_path)
        logger.info(f"Copied default config: {default_path} -> {target_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to copy config file: {e}")
        return False

def load_tsv_file(file_path: Union[str, Path], 
                 encoding: str = 'utf-8') -> pd.DataFrame:
    """Load a TSV file into a pandas DataFrame.
    
    Args:
        file_path: Path to the TSV file
        encoding: File encoding
    
    Returns:
        DataFrame with the TSV data
    """
    logger = get_logger()
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"TSV file not found: {file_path}")
    
    try:
        df = pd.read_csv(file_path, delimiter='\t', encoding=encoding)
        logger.debug(f"Loaded TSV file: {file_path} ({len(df)} rows)")
        return df
    except Exception as e:
        logger.error(f"Failed to load TSV file {file_path}: {e}")
        raise

def save_dataframe(df: pd.DataFrame,
                  file_path: Union[str, Path],
                  format_type: str = 'csv',
                  encoding: str = 'utf-8',
                  **kwargs) -> None:
    """Save a DataFrame to various file formats.
    
    Args:
        df: DataFrame to save
        file_path: Output file path
        format_type: File format ('csv', 'tsv', 'json', 'excel')
        encoding: File encoding
        **kwargs: Additional arguments for pandas save methods
    """
    logger = get_logger()
    file_path = Path(file_path)
    
    # Ensure parent directory exists
    ensure_directory_exists(file_path.parent)
    
    try:
        if format_type.lower() == 'csv':
            df.to_csv(file_path, encoding=encoding, index=False, **kwargs)
        elif format_type.lower() == 'tsv':
            df.to_csv(file_path, sep='\t', encoding=encoding, index=False, **kwargs)
        elif format_type.lower() == 'json':
            df.to_json(file_path, orient='records', indent=2, **kwargs)
        elif format_type.lower() == 'excel':
            df.to_excel(file_path, index=False, **kwargs)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
        
        logger.info(f"Saved DataFrame to {file_path} ({len(df)} rows)")
        
    except Exception as e:
        logger.error(f"Failed to save DataFrame to {file_path}: {e}")
        raise

def merge_csv_files(file_paths: List[Union[str, Path]],
                   output_path: Union[str, Path],
                   sort_column: Optional[str] = None,
                   encoding: str = 'utf-8') -> pd.DataFrame:
    """Merge multiple CSV files into one.
    
    Args:
        file_paths: List of CSV file paths to merge
        output_path: Path for the merged output file
        sort_column: Column name to sort by after merging
        encoding: File encoding
    
    Returns:
        Merged DataFrame
    """
    logger = get_logger()
    
    if not file_paths:
        raise ValueError("No files provided for merging")
    
    dataframes = []
    for file_path in file_paths:
        file_path = Path(file_path)
        if file_path.exists():
            df = pd.read_csv(file_path, encoding=encoding)
            # Add source file column for tracking
            df['source_file'] = file_path.name
            dataframes.append(df)
            logger.debug(f"Loaded {len(df)} rows from {file_path.name}")
        else:
            logger.warning(f"File not found, skipping: {file_path}")
    
    if not dataframes:
        raise RuntimeError("No valid files found to merge")
    
    # Merge all DataFrames
    merged_df = pd.concat(dataframes, ignore_index=True)
    
    # Sort if requested
    if sort_column and sort_column in merged_df.columns:
        merged_df = merged_df.sort_values(sort_column).reset_index(drop=True)
        logger.info(f"Sorted merged data by '{sort_column}'")
    
    # Save merged file
    save_dataframe(merged_df, output_path, encoding=encoding)
    
    logger.info(f"Merged {len(file_paths)} files into {output_path} ({len(merged_df)} total rows)")
    return merged_df

def get_file_stats(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Get statistics about a file.
    
    Args:
        file_path: Path to the file
    
    Returns:
        Dictionary with file statistics
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        return {"exists": False}
    
    stat = file_path.stat()
    return {
        "exists": True,
        "size_bytes": stat.st_size,
        "size_mb": round(stat.st_size / (1024 * 1024), 2),
        "modified_time": stat.st_mtime,
        "is_file": file_path.is_file(),
        "is_directory": file_path.is_dir(),
        "extension": file_path.suffix,
        "name": file_path.name,
    }

def organize_output_files(source_dir: Union[str, Path],
                         output_dir: Union[str, Path],
                         file_patterns: Dict[str, str],
                         create_subdirs: bool = True) -> Dict[str, List[Path]]:
    """Organize output files into structured directories.
    
    Args:
        source_dir: Source directory containing files
        output_dir: Output directory for organization
        file_patterns: Dict mapping subdirectory names to file patterns
        create_subdirs: Whether to create subdirectories
    
    Returns:
        Dictionary mapping subdirectory names to lists of moved files
    """
    logger = get_logger()
    source_path = Path(source_dir)
    output_path = Path(output_dir)
    
    if not source_path.exists():
        raise FileNotFoundError(f"Source directory not found: {source_path}")
    
    ensure_directory_exists(output_path)
    organized_files = {}
    
    for subdir_name, pattern in file_patterns.items():
        # Find files matching pattern
        files = find_files_by_pattern(source_path, pattern, recursive=False)
        
        if files and create_subdirs:
            subdir = output_path / subdir_name
            ensure_directory_exists(subdir)
        else:
            subdir = output_path
        
        moved_files = []
        for file_path in files:
            dest_path = subdir / file_path.name
            try:
                shutil.move(str(file_path), str(dest_path))
                moved_files.append(dest_path)
                logger.debug(f"Moved {file_path.name} to {subdir_name}/")
            except Exception as e:
                logger.warning(f"Failed to move {file_path}: {e}")
        
        organized_files[subdir_name] = moved_files
        
        if moved_files:
            logger.info(f"Organized {len(moved_files)} files into {subdir_name}/")
    
    return organized_files