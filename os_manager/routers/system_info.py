from fastapi import APIRouter, HTTPException, Depends
from auth import require_admin_user
from typing import List, Dict, Any
import psutil
import platform
import os
from datetime import datetime

router = APIRouter(
    prefix="/system",
    tags=["system"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(require_admin_user)],
)

@router.get("/info")
async def get_system_info() -> Dict[str, Any]:
    """Get basic system information."""
    try:
        return {
            "os": {
                "name": platform.system(),
                "version": platform.version(),
                "architecture": platform.machine(),
                "processor": platform.processor(),
            },
            "python_version": platform.python_version(),
            "hostname": platform.node(),
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
            "cpu_count": psutil.cpu_count(),
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent_used": psutil.virtual_memory().percent,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/processes")
async def get_processes(limit: int = 10) -> List[Dict[str, Any]]:
    """Get list of running processes."""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                pinfo = proc.info
                processes.append({
                    "pid": pinfo['pid'],
                    "name": pinfo['name'],
                    "cpu_percent": pinfo['cpu_percent'],
                    "memory_percent": pinfo['memory_percent'],
                    "status": pinfo['status']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by CPU usage and return top N processes
        return sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/disk")
async def get_disk_usage() -> List[Dict[str, Any]]:
    """Get disk usage information."""
    try:
        disks = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "filesystem": partition.fstype,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent_used": usage.percent
                })
            except (PermissionError, OSError):
                continue
        return disks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/network")
async def get_network_info() -> Dict[str, Any]:
    """Get network interfaces and statistics."""
    try:
        interfaces = psutil.net_if_stats()
        io_counters = psutil.net_io_counters(pernic=True)
        
        network_info = {}
        for interface, stats in interfaces.items():
            network_info[interface] = {
                "status": "up" if stats.isup else "down",
                "speed": stats.speed,
                "mtu": stats.mtu,
                "bytes_sent": io_counters[interface].bytes_sent if interface in io_counters else 0,
                "bytes_recv": io_counters[interface].bytes_recv if interface in io_counters else 0,
                "packets_sent": io_counters[interface].packets_sent if interface in io_counters else 0,
                "packets_recv": io_counters[interface].packets_recv if interface in io_counters else 0,
            }
        return network_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 