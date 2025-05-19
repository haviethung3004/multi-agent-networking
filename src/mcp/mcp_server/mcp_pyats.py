from pyats.topology import loader
from pathlib import Path
from mcp.server.fastmcp import FastMCP
import yaml
import asyncio

#Define the MCP server
mcp = FastMCP(name="pyats-server")


def testbed_file():
    # Get the script's directory
    script_dir = Path(__file__).parent

    # Find the project root by walking up until 'multi-agent-networking' is found
    current_dir = script_dir
    while current_dir.name != "multi-agent-networking" and current_dir != current_dir.parent:
        current_dir = current_dir.parent
    project_root = current_dir if current_dir.name == "multi-agent-networking" else script_dir.parent

    # Define possible locations for testbed.yaml
    possible_locations = [
        project_root / "config" / "testbed.yaml",  # Primary: multi-agent-networking/config/
        project_root / "testbed.yaml",             # Project root
        project_root.parent / "testbed.yaml",      # Parent of project root
    ]

    # Check each location
    for testbed_path in possible_locations:
        print(f"Checking for testbed file at: {testbed_path}")
        if testbed_path.is_file():
            return str(testbed_path)

    # Raise error if not found
    search_dirs = ", ".join(str(p.parent) for p in possible_locations)
    raise FileNotFoundError(f"Testbed file 'testbed.yaml' not found in {search_dirs}")

@mcp.resource("testbed://folders")
def get_availables_testbed_file_path() -> str:
    """
    Get the testbed file path.
    The resource provides a simmple string with the path to the testbed file.
    """
    return testbed_file()

@mcp.resource("testbed://{file_path}")
def get_name_devices(file_path: str) -> list:
    """
    Read the content of the testbed file and get the name file.
    A resource that provides a list name of the devices in the testbed file.
    """
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            # Load the YAML content
            data = yaml.safe_load(content)
            # Extract the device names
            device_names = [device for device in data['devices']]
            # Return the list of device names
            return device_names
    except FileNotFoundError:
        raise FileNotFoundError(f"Testbed file not found at {file_path}")


#Temporary function to get the testbed file
@mcp.tool()
def get_testbed_file() -> str:
    """
    Get the testbed file path.
    A tool that provides a simple string with the path to the testbed file.
    """
    return testbed_file()


#Temporary function to get the name of the devices
@mcp.tool()
def get_name_devices_tool(testbed_file: str) -> list:
    """
    Read the content of the testbed file and get the name file.
    A tool that provides a list name of the devices in the testbed file.
    please use get_testbed_file tool to get the testbed file path
    """
    try:
        with open(testbed_file, 'r') as file:
            content = file.read()
            # Load the YAML content
            data = yaml.safe_load(content)
            # Extract the device names
            device_names = [device for device in data['devices']]
            # Return the list of device names
            return device_names
    except FileNotFoundError:
        raise FileNotFoundError(f"Testbed file not found at {testbed_file}")


#CPU tool checking
@mcp.tool()
def cpu_checking(testbed_file: str, device_name: str):
    """
    Check CPU usage on a specified device using pyATS.
    This function connects to the device, executes a command to check CPU usage
    please use get_testbed_file tool to get the testbed file path and get_name_devices_tool to get the name of the devices.

    Args:
        device_name (str): Name of the device in the testbed (e.g., 'R1').
        testbed_file (str, optional): Path to testbed.yaml. If None, uses testbed_file().

    Returns:
        dict: CPU usage information (e.g., {'cpu_usage': '5%'}) or None if failed.

    Raises:
        FileNotFoundError: If testbed file is not found.
        KeyError: If device_name is not in testbed.
        RuntimeError: For connection or command execution errors.
    """        
    try:
        testbed = loader.load(testbed_file)
        device = testbed.devices[device_name]
        if not device:
            raise KeyError(f"Device '{device_name}' not found in testbed.")
        device.connect()
        cpu_output = device.execute("show processes cpu | i CPU utilization")
        if device.is_connected():
            device.disconnect()
        return cpu_output
    except Exception as e:
        raise RuntimeError(f"Error checking CPU tool: {e}")
        


if __name__ == "__main__":
    mcp.run(transport='stdio')
