from langchain_core.tools import tool
from pathlib import Path
from schemas.agent_states import DeviceHealth
from typing import List, Dict, Any, Optional

@tool
def format_and_output_health_report(
    health_data_list: List[Dict[str, Any]],
    overall_status_notes: Optional[str] = None
) -> str:
    """
    Formats a list of device health data dictionaries into a string report
    and outputs it TO THE CONSOLE.
    The input 'health_data_list' should be a list of dictionaries, where each dictionary
    represents a device's health status (conforming to DeviceHealth schema).
    'overall_status_notes' can be an optional string to add any preamble, summary, or error notes to the report.
    Returns a string confirming the report output or an error message.
    """
    print(f"--- TOOL INVOKED: format_and_output_health_report ---")
    print(f"Args: health_data_list_count={len(health_data_list) if isinstance(health_data_list, list) else 'N/A (not a list)'}, overall_status_notes='{overall_status_notes}'")

    if not isinstance(health_data_list, list):
        error_msg = "Tool Error: health_data_list input must be a list of device health dictionaries."
        print(error_msg)
        return error_msg

    processed_health_data: List[DeviceHealth] = []
    for item in health_data_list:
        if isinstance(item, dict):
            processed_health_data.append(DeviceHealth(
                name=item.get("name", "N/A"),
                id=item.get("id", "N/A"),
                status=item.get("status", "Unknown"),
                uptime=item.get("uptime"),
                cpu_usage=item.get("cpu_usage"),
                memory_usage=item.get("memory_usage"),
                error_messages=item.get("error_messages")
            ))
        else:
            print(f"Warning (format_and_output_health_report): Skipping non-dictionary item in health_data_list: {item}")

    report_lines = ["Network Devices Health Check Report:", "="*35]
    if overall_status_notes:
        report_lines.insert(0, f"Overall Status/Notes: {overall_status_notes}\n")

    if not processed_health_data:
        report_lines.append("\nNo device health data was provided to generate the report details.")
    else:
        for device in processed_health_data:
            report_lines.append(f"\nDevice: {device['name']} (ID: {device['id']})")
            report_lines.append(f"  Status: {device['status']}")
            if device['status'] == "Reachable":
                report_lines.append(f"  Uptime: {device.get('uptime', 'N/A')}")
                report_lines.append(f"  CPU Usage: {device.get('cpu_usage', 'N/A')}")
                report_lines.append(f"  Memory Usage: {device.get('memory_usage', 'N/A')}")
            if device.get('error_messages'):
                errors_str = "; ".join(device['error_messages']) if device['error_messages'] else "None"
                report_lines.append(f"  Reported Errors: {errors_str}")

    report_content = "\n".join(report_lines)
    output_status_message: str = ""

    try:
        print("\n--- HEALTH CHECK REPORT (Outputting to Console) ---")
        print(report_content)
        print("--- END OF CONSOLE REPORT ---\n")
        output_status_message = "Report was successfully output to the console."
        return output_status_message
    except Exception as e:
        error_detail = f"Tool Error during console output: {type(e).__name__} - {e}. Report content was:\n{report_content[:500]}..."
        print(error_detail)
        return error_detail

if __name__ == '__main__':


    sample_health_data_list_good: List[Dict[str, Any]] = [
        {"name": "router1", "id": "10.0.1.1", "status": "Reachable", "uptime": "10d", "cpu_usage": "20%", "memory_usage": "30%"},
        {"name": "switch1", "id": "10.0.0.1", "status": "Reachable", "uptime": "5d", "cpu_usage": "10%", "memory_usage": "15%"}
    ]
    print("\nTesting report tool with good data (console):")
    format_and_output_health_report(health_data_list=sample_health_data_list_good, overall_status_notes="All systems nominal.")
