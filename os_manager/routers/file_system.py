from fastapi import APIRouter, HTTPException, Query, Depends
from auth import require_admin_user
from typing import List, Dict, Any, Optional
import os
import shutil
from pathlib import Path
from datetime import datetime

router = APIRouter(
    prefix="/files",
    tags=["file system"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(require_admin_user)],
)

def get_file_info(path: Path) -> Dict[str, Any]:
    """Get detailed information about a file or directory."""
    stats = path.stat()
    return {
        "name": path.name,
        "path": str(path.absolute()),
        "type": "directory" if path.is_dir() else "file",
        "size": stats.st_size,
        "created": datetime.fromtimestamp(stats.st_ctime).isoformat(),
        "modified": datetime.fromtimestamp(stats.st_mtime).isoformat(),
        "accessed": datetime.fromtimestamp(stats.st_atime).isoformat(),
        "permissions": oct(stats.st_mode)[-3:],  # Last 3 digits of octal permissions
    }

@router.get("/list")
async def list_directory(
    path: str = Query("/", description="Directory path to list"),
    show_hidden: bool = Query(False, description="Show hidden files")
) -> List[Dict[str, Any]]:
    """List contents of a directory."""
    try:
        directory = Path(path).expanduser().resolve()
        if not directory.exists():
            raise HTTPException(status_code=404, detail="Directory not found")
        if not directory.is_dir():
            raise HTTPException(status_code=400, detail="Path is not a directory")
        
        contents = []
        for item in directory.iterdir():
            if not show_hidden and item.name.startswith('.'):
                continue
            contents.append(get_file_info(item))
        
        return sorted(contents, key=lambda x: (x["type"] == "file", x["name"].lower()))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/info")
async def get_path_info(
    path: str = Query(..., description="Path to get information about")
) -> Dict[str, Any]:
    """Get detailed information about a file or directory."""
    try:
        file_path = Path(path).expanduser().resolve()
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Path not found")
        return get_file_info(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mkdir")
async def create_directory(
    path: str = Query(..., description="Directory path to create"),
    parents: bool = Query(False, description="Create parent directories if needed")
) -> Dict[str, Any]:
    """Create a new directory."""
    try:
        directory = Path(path).expanduser().resolve()
        directory.mkdir(parents=parents, exist_ok=False)
        return get_file_info(directory)
    except FileExistsError:
        raise HTTPException(status_code=400, detail="Directory already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/remove")
async def remove_path(
    path: str = Query(..., description="Path to remove"),
    recursive: bool = Query(False, description="Recursively remove directories")
) -> Dict[str, str]:
    """Remove a file or directory."""
    try:
        file_path = Path(path).expanduser().resolve()
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Path not found")
        
        if file_path.is_file():
            file_path.unlink()
        elif file_path.is_dir():
            if recursive:
                shutil.rmtree(file_path)
            else:
                file_path.rmdir()  # Will only work if directory is empty
        
        return {"message": f"Successfully removed {path}"}
    except OSError as e:
        if not recursive and file_path.is_dir():
            raise HTTPException(status_code=400, detail="Directory not empty. Use recursive=true to remove")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/copy")
async def copy_path(
    source: str = Query(..., description="Source path"),
    destination: str = Query(..., description="Destination path"),
    overwrite: bool = Query(False, description="Overwrite existing files")
) -> Dict[str, Any]:
    """Copy a file or directory."""
    try:
        src_path = Path(source).expanduser().resolve()
        dst_path = Path(destination).expanduser().resolve()
        
        if not src_path.exists():
            raise HTTPException(status_code=404, detail="Source path not found")
        
        if dst_path.exists() and not overwrite:
            raise HTTPException(status_code=400, detail="Destination already exists")
        
        if src_path.is_file():
            shutil.copy2(src_path, dst_path)
        else:
            shutil.copytree(src_path, dst_path, dirs_exist_ok=overwrite)
        
        return get_file_info(dst_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 