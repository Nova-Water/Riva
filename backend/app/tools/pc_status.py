"""get_pc_status: read-only system status (green permission)."""
from __future__ import annotations

import platform
import socket
import time

import psutil
from pydantic import BaseModel

from app.tools.registry import ToolDefinition, registry
from app.tools.schemas import PermissionLevel, ToolContext, ToolResult


class GetPcStatusInput(BaseModel):
    pass


def _local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        try:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        finally:
            s.close()
    except Exception:
        return "unavailable"


def _has_network() -> bool:
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=1.5).close()
        return True
    except Exception:
        return False


def _top_processes(limit: int = 5) -> list[dict]:
    processes = []
    for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            info = proc.info
            processes.append(
                {
                    "name": info.get("name") or "unknown",
                    "cpu_percent": round(info.get("cpu_percent") or 0.0, 1),
                    "memory_percent": round(info.get("memory_percent") or 0.0, 1),
                }
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    processes.sort(key=lambda p: p["cpu_percent"], reverse=True)
    return processes[:limit]


async def handle_get_pc_status(_: GetPcStatusInput, __: ToolContext) -> ToolResult:
    vm = psutil.virtual_memory()
    disk = psutil.disk_usage("/" if platform.system() != "Windows" else "C:\\")
    uptime_seconds = time.time() - psutil.boot_time()

    data = {
        "computer_name": socket.gethostname(),
        "operating_system": f"{platform.system()} {platform.release()}",
        "cpu_usage_percent": psutil.cpu_percent(interval=0.3),
        "memory_usage_percent": vm.percent,
        "memory_available_gb": round(vm.available / (1024**3), 2),
        "disk_usage_percent": disk.percent,
        "disk_available_gb": round(disk.free / (1024**3), 2),
        "network_connected": _has_network(),
        "uptime_hours": round(uptime_seconds / 3600, 1),
        "local_ip_address": _local_ip(),
        "top_processes": _top_processes(),
    }
    return ToolResult(success=True, data=data, message="Retrieved current PC status.")


registry.register(
    ToolDefinition(
        name="get_pc_status",
        description=(
            "Get read-only computer status: CPU, memory, disk, network, uptime, and top "
            "resource-consuming processes. No sensitive process arguments are exposed."
        ),
        input_model=GetPcStatusInput,
        permission_level=PermissionLevel.GREEN,
        handler=handle_get_pc_status,
    )
)
