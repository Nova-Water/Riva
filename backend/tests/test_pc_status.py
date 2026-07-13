import pytest

from app.config import get_settings
from app.security.app_allowlist import ApplicationAllowlist
from app.tools.pc_status import GetPcStatusInput, handle_get_pc_status
from app.tools.schemas import ToolContext


@pytest.mark.asyncio
async def test_get_pc_status_returns_expected_fields():
    settings = get_settings()
    ctx = ToolContext(settings=settings, conversation_id="c1", app_allowlist=ApplicationAllowlist([]))
    result = await handle_get_pc_status(GetPcStatusInput(), ctx)

    assert result.success is True
    for field in [
        "computer_name",
        "operating_system",
        "cpu_usage_percent",
        "memory_usage_percent",
        "memory_available_gb",
        "disk_usage_percent",
        "disk_available_gb",
        "network_connected",
        "uptime_hours",
        "local_ip_address",
        "top_processes",
    ]:
        assert field in result.data

    assert isinstance(result.data["top_processes"], list)
