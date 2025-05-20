from pyats.topology import loader
from mcp.server.fastmcp import FastMCP
import yaml
import asyncio
from dotenv import load_dotenv, find_dotenv
import os
import logging
import sys



# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("PyatsMCPServer")

# Load environment variables from .env file
load_dotenv(find_dotenv(), override=True)
testbed_file  = os.getenv("PYATS_TESTBED_PATH")

if not testbed_file or not os.path.exists(testbed_file):
    logger.error("❌ CRITICAL: Testbed file not found. Please set the PYATS_TESTBED_PATH in .env file.")
    sys.exit(1)

#Define the MCP server
mcp = FastMCP(name="healthcheck-server")


# Get device from testbed file
def _setup_connect_device(device_name: str):
    """
    Connect to th device using the testbed file.
    """
    try:
        testbed = loader.load(testbed_file)
        device = testbed.devices[device_name]
        if not device:
            raise KeyError(f"Device '{device_name}' not found in testbed.")
        device.connect()
        return device
    except Exception as e:
        logger.error(f"Error connecting to device '{device_name}': {e}")
        raise RuntimeError(f"Error connecting to device '{device_name}': {e}")

def _disconnect_device(device):
    """Helper to safely disconnect."""
    if device and device.is_connected():
        logger.info(f"Disconnecting from {device.name}...")
        try:
            device.disconnect()
            logger.info(f"Disconnected from {device.name}")
        except Exception as e:
            logger.warning(f"Error disconnecting from {device.name}: {e}")


@mcp.prompt(name="healthcheck agent")
def get_prompt() -> str:
    """
    Get the prompt for the agent.
    A prompt that provides a simple string with the prompt for the agent.
    """
    return """
    You are an expert CCIE in health check network devices.
    You should following the instructions below:
    1. You must use tool get_name_devices to get the name of the devices in the testbed file.
    2. If user ask for specific checking, please use the appropriate tool.
    3. Custom tool can be used if for any specific command.
    """

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
def cpu_checking(device_name: str) -> str:
    """
    Args:
        device_name (str): Name of the device in the testbed (e.g., 'R1').
    Returns:
        dict: CPU usage information (e.g., {'cpu_usage': '5%'}) or None if failed.
    Raises:
        FileNotFoundError: If testbed file is not found.
        KeyError: If device_name is not in testbed.
        RuntimeError: For connection or command execution errors.
    """        
    try:
        device = _setup_connect_device(device_name)
        cpu_output = device.execute("show processes cpu | i CPU utilization")
        return cpu_output
        _disconnect_device(device)
    except Exception as e:
        raise RuntimeError(f"Error checking CPU tool: {e}")
    
        
#Interface tool checking
@mcp.tool()
def interface_checking(device_name: str):
    """
    Args:
        device_name (str): Name of the device in the testbed (e.g., 'R1').
    Raises:
        FileNotFoundError: If testbed file is not found.
        KeyError: If device_name is not in testbed.
        RuntimeError: For connection or command execution errors.
    """        
    try:
        device = _setup_connect_device(device_name)
        interface_output = device.execute("show interface")
        _disconnect_device(device)
        return interface_output
    except Exception as e:
        raise RuntimeError(f"Error checking Interface tool: {e}")


#CRC tool checking
@mcp.tool()
def crc_checking(device_name: str):
    """
    Args:
        device_name (str): Name of the device in the testbed (e.g., 'R1').
    Raises:
        FileNotFoundError: If testbed file is not found.
        KeyError: If device_name is not in testbed.
        RuntimeError: For connection or command execution errors.
    """        
    try:
        device = _setup_connect_device(device_name)
        crc_output = device.execute("show interfaces | i CRC")
        _disconnect_device(device)
        return crc_output
    except Exception as e:
        raise RuntimeError(f"Error checking CRC tool: {e}")


#Custom show command tool checking
@mcp.tool()
def custom_show_command(device_name: str, command: list[str]) -> str:
    """
    This tool using for custom show command health checking
    """
    try:
        device = _setup_connect_device(device_name)
        command_output = device.execute(command)
        _disconnect_device(device)
        return command_output
    except Exception as e:
        raise RuntimeError(f"Error checking custom show command tool: {e}")


if __name__ == "__main__":
    #Test the tool
    name_device = get_name_devices_tool(testbed_file)
    print(name_device)

    # cpu_checking(name_device[0])
    cpu_checking(name_device[0])

    # interface_checking(name_device[0])
    interface_checking(name_device[0])

    # crc_checking(name_device[0])
    crc_checking(name_device[0])

    # custom_show_command(name_device[0], "show ip interface brief")
    custom_show_command(name_device[0], "show ip interface brief")

    #mcp.run(transport='stdio')
