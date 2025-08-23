"""
Simple cleanup step configuration for TTRPG transcript processing.
"""

from typing import Dict, List, Tuple, Any
import pandas as pd

from shared_utils.text_processing import (
    remove_duplicate_short_text,
    merge_adjacent_segments, 
    remove_short_text,
    remove_silence_gibberish
)
from shared_utils.logging_config import get_logger


def remove_final_duplicates(df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
    """Remove final duplicate entries by text content."""
    logger = get_logger()
    original_len = len(df)
    df_cleaned = df.drop_duplicates(subset='text', keep='first')
    removed_count = original_len - len(df_cleaned)
    
    if removed_count > 0:
        logger.info(f"Removed {removed_count} final duplicate entries")
    
    return df_cleaned, removed_count


# Define cleanup steps as simple list of tuples
# Format: (step_name, function, config_key_prefix, description)
CLEANUP_STEPS = [
    (
        'remove_duplicates', 
        remove_duplicate_short_text,
        'short_duplicate_text',
        'Remove duplicate short text entries'
    ),
    (
        'merge_segments', 
        merge_adjacent_segments,
        'merge',
        'Merge adjacent segments based on timing'
    ),
    (
        'remove_short', 
        remove_short_text,
        'short_text',
        'Remove entries with very short text'
    ),
    (
        'remove_final_duplicates',
        remove_final_duplicates,
        'final_duplicates', 
        'Remove final duplicate entries'
    ),
    (
        'remove_gibberish',
        remove_silence_gibberish,
        'silence_gibberish',
        'Remove silence/gibberish patterns'
    ),
]


def get_step_parameters(config_dict: Dict[str, Any], step_name: str) -> Dict[str, Any]:
    """Extract parameters for a specific cleanup step from config."""
    params = {}
    
    if step_name == 'remove_duplicates':
        if config_dict.get('short_duplicate_text_length', 0) > 0:
            params['max_length'] = config_dict['short_duplicate_text_length']
    
    elif step_name == 'merge_segments':
        if config_dict.get('merge_threshold', 0) > 0:
            params['threshold'] = config_dict['merge_threshold']
    
    elif step_name == 'remove_short':
        if config_dict.get('short_text_length', 0) > 0:
            params['min_length'] = config_dict['short_text_length']
    
    elif step_name == 'remove_gibberish':
        if (config_dict.get('remove_silence_gibberish', False) and 
            config_dict.get('silence_gibberish_patterns')):
            params['patterns'] = config_dict['silence_gibberish_patterns']
    
    return params


def should_run_step(config_dict: Dict[str, Any], step_name: str) -> bool:
    """Determine if a cleanup step should run based on configuration."""
    
    # Check if step is explicitly disabled
    if config_dict.get(f'enable_{step_name}', True) is False:
        return False
    
    # Check step-specific conditions
    if step_name == 'remove_duplicates':
        return config_dict.get('short_duplicate_text_length', 0) > 0
    
    elif step_name == 'merge_segments':
        return config_dict.get('merge_threshold', 0) > 0
        
    elif step_name == 'remove_short':
        return config_dict.get('short_text_length', 0) > 0
        
    elif step_name == 'remove_final_duplicates':
        return True  # Always run this step
        
    elif step_name == 'remove_gibberish':
        return (config_dict.get('remove_silence_gibberish', False) and 
                config_dict.get('silence_gibberish_patterns'))
    
    return True


def run_cleanup_pipeline(df: pd.DataFrame, config_dict: Dict[str, Any]) -> pd.DataFrame:
    """Run the configurable cleanup pipeline."""
    logger = get_logger()
    logger.info(f"Starting configurable cleanup pipeline with {len(df)} rows")
    
    for step_name, step_func, step_prefix, description in CLEANUP_STEPS:
        
        if not should_run_step(config_dict, step_name):
            logger.debug(f"Skipping step '{step_name}': {description}")
            continue
            
        logger.debug(f"Running step '{step_name}': {description}")
        
        # Get step parameters
        params = get_step_parameters(config_dict, step_name)
        
        if not params and step_name != 'remove_final_duplicates':
            logger.debug(f"Skipping step '{step_name}': no valid parameters")
            continue
        
        # Run the step
        try:
            df, _ = step_func(df, **params)
        except Exception as e:
            logger.error(f"Error in cleanup step '{step_name}': {e}")
            continue
    
    logger.info(f"Cleanup pipeline complete: {len(df)} rows remaining")
    return df


def get_step_info() -> List[Dict[str, str]]:
    """Get information about all available cleanup steps."""
    return [
        {
            'name': step_name,
            'prefix': step_prefix, 
            'description': description,
            'config_key': f'enable_{step_name}'
        }
        for step_name, _, step_prefix, description in CLEANUP_STEPS
    ]