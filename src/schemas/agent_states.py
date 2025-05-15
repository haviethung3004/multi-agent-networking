# src/schemas/agent_states.py

from typing import TypedDict, Optional, List, Dict

# --- Individual Data Structures ---
class DeviceInfo(TypedDict):
    """"Represents a device to be checked by the Monitoring Agent."""
    name: str
    id: str

class DeviceHealth(TypedDict):
    """Represents the health status of a device."""
    name: str
    id: str
    status: str # e.g,. "Reachable", "Unreachable", "Unknown"
    uptime: Optional[str]
    cpu_usage: Optional[str]
    memory_usage: Optional[str]
    error_messages: Optional[List[str]]
    
# --- Agent States ---
class AgentState(TypedDict):
    """Represents the state of an agent."""
    
    devices_to_check: Optional[List[DeviceInfo]]
    collected_heath_data: Optional[List[DeviceHealth]]
    report_generation_status: Optional[str]
    error_info: Optional[str]