# src/tools/report_tools.py
from langchain_core.tools import tool
from utils.config_loader import load_devices


@tool
def generate_report(data: str) -> str:
    """
    Generates a report based on the provided data.
    Args:
        data (str): The data to include in the report.
    """
    return f"Report generated with the following data: {data}"

def get_device_info() -> str:
    """
    Retrieves all information about device.
    Returns:
        str: Information about the device.
    """
    device_info = load_devices()
    return device_info

if __name__ == "__main__":
    device_info = get_device_info()
    print(device_info)


