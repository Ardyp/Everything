from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
import psutil
import subprocess
import sys
import os
from datetime import datetime

router = APIRouter(
    prefix="/process",
    tags=["process management"],
    responses={404: {"description": "Not found"}},
)

def get_process_info(process: psutil.Process) -> Dict[str, Any]:
    """Get detailed information about a process."""
    try:
        with process.oneshot():
            return {
                "pid": process.pid,
                "name": process.name(),
                "status": process.status(),
                "created": datetime.fromtimestamp(process.create_time()).isoformat(),
                "cpu_percent": process.cpu_percent(),
                "memory_percent": process.memory_percent(),
                "command": process.cmdline(),
                "username": process.username(),
                "num_threads": process.num_threads(),
                "memory_info": {
                    "rss": process.memory_info().rss,  # Resident Set Size
                    "vms": process.memory_info().vms,  # Virtual Memory Size
                },
                "num_fds": process.num_fds() if sys.platform != "win32" else None,
                "nice": process.nice(),
            }
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return None

@router.get("/list")
async def list_processes(
    sort_by: str = Query("cpu", description="Sort by: cpu, memory, pid, name"),
    limit: int = Query(50, description="Number of processes to return"),
    pattern: Optional[str] = Query(None, description="Filter process names by pattern")
) -> List[Dict[str, Any]]:
    """List running processes with optional filtering and sorting."""
    try:
        processes = []
        for proc in psutil.process_iter():
            try:
                if pattern and pattern.lower() not in proc.name().lower():
                    continue
                
                info = get_process_info(proc)
                if info:
                    processes.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        # Sort processes
        sort_key = {
            "cpu": lambda x: x["cpu_percent"],
            "memory": lambda x: x["memory_percent"],
            "pid": lambda x: x["pid"],
            "name": lambda x: x["name"].lower()
        }.get(sort_by, lambda x: x["cpu_percent"])
        
        return sorted(processes, key=sort_key, reverse=sort_by in ["cpu", "memory"])[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{pid}")
async def get_process(pid: int) -> Dict[str, Any]:
    """Get detailed information about a specific process."""
    try:
        process = psutil.Process(pid)
        info = get_process_info(process)
        if not info:
            raise HTTPException(status_code=404, detail="Process not found")
        return info
    except psutil.NoSuchProcess:
        raise HTTPException(status_code=404, detail="Process not found")
    except psutil.AccessDenied:
        raise HTTPException(status_code=403, detail="Access denied")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run")
async def run_process(
    command: str = Query(..., description="Command to run"),
    shell: bool = Query(False, description="Run command in shell"),
    cwd: Optional[str] = Query(None, description="Working directory"),
    timeout: Optional[float] = Query(None, description="Timeout in seconds")
) -> Dict[str, Any]:
    """Run a new process."""
    try:
        if shell and ("|" in command or ">" in command or "<" in command):
            # For shell commands with pipes or redirections
            process = subprocess.run(
                command,
                shell=True,
                text=True,
                capture_output=True,
                cwd=cwd,
                timeout=timeout
            )
        else:
            # For regular commands
            cmd_list = command.split() if not shell else command
            process = subprocess.run(
                cmd_list,
                shell=shell,
                text=True,
                capture_output=True,
                cwd=cwd,
                timeout=timeout
            )
        
        return {
            "command": command,
            "return_code": process.returncode,
            "stdout": process.stdout,
            "stderr": process.stderr,
            "successful": process.returncode == 0
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Process timed out")
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{pid}")
async def terminate_process(
    pid: int,
    force: bool = Query(False, description="Force kill the process")
) -> Dict[str, str]:
    """Terminate or kill a process."""
    try:
        process = psutil.Process(pid)
        
        # Don't allow terminating system processes
        if process.username() in ["root", "system"]:
            raise HTTPException(status_code=403, detail="Cannot terminate system processes")
        
        if force:
            process.kill()  # SIGKILL
        else:
            process.terminate()  # SIGTERM
            
        return {"message": f"Process {pid} {'killed' if force else 'terminated'} successfully"}
    except psutil.NoSuchProcess:
        raise HTTPException(status_code=404, detail="Process not found")
    except psutil.AccessDenied:
        raise HTTPException(status_code=403, detail="Access denied")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 