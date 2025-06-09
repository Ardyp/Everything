import json
from pathlib import Path
from typing import Any, Dict

def load_json_file(file_path: str) -> Dict[str, Any]:
    """
    Load and parse a JSON file.
    
    Args:
        file_path (str): Path to the JSON file
        
    Returns:
        Dict[str, Any]: Parsed JSON data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(path, 'r') as f:
        return json.load(f)

def save_json_file(file_path: str, data: Dict[str, Any]) -> None:
    """
    Save data to a JSON file.
    
    Args:
        file_path (str): Path where to save the JSON file
        data (Dict[str, Any]): Data to save
        
    Raises:
        IOError: If the file cannot be written
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w') as f:
        json.dump(data, f, indent=4) 