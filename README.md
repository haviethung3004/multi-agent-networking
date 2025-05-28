# Multi-Agent Networking System

A sophisticated multi-agent system designed for network automation and management, leveraging LangGraph and Model Context Protocol (MCP) servers to coordinate specialized agents for Cisco ACI, IOS device configuration, and Slack notifications.

## 🚀 Features

- **Multi-Agent Architecture**: Coordinated system with specialized agents for different network tasks
- **Supervisor Agent**: CCIE-level expertise for task delegation and coordination
- **Network Device Support**: 
  - Cisco ACI (Application Centric Infrastructure) configuration
  - Cisco IOS device management
- **Real-time Notifications**: Slack integration for status updates and alerts
- **FastAPI REST API**: HTTP endpoints for easy integration
- **Model Context Protocol**: MCP servers for agent communication
- **Google Gemini Integration**: AI-powered network decision making

## 🏗️ Architecture

The system consists of several key components:

### Core Agents
1. **Supervisor Agent**: Main coordinator with CCIE expertise
2. **ACI Agent**: Handles Cisco ACI datacenter configurations
3. **IOS Agent**: Manages Cisco IOS device configurations
4. **Notify Agent**: Sends updates via Slack

### API Layer
- FastAPI application providing REST endpoints
- Async request handling
- Structured request/response models

### MCP Integration
- Multi-server MCP client for agent communication
- Distributed agent execution
- Tool sharing between agents

## 📋 Prerequisites

- Python 3.11 or higher
- Node.js (for Slack MCP server)
- UV package manager
- Access to:
  - Google Gemini API
  - Slack workspace and bot token
  - Cisco network devices (optional for testing)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd multi-agent-networking
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   GOOGLE_API_KEY=your_google_gemini_api_key
   SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
   SLACK_TEAM_ID=your_slack_team_id
   ```

4. **Install Node.js dependencies** (for Slack MCP server)
   ```bash
   npm install -g @modelcontextprotocol/server-slack
   ```

5. **Configure MCP Server Paths**
   Update the paths in `graph.py` to match your MCP server installations:
   ```python
   # In graph.py, update these paths to your actual MCP server locations:
   client = MultiServerMCPClient({
       "aci-agent": {
           "command": "/path/to/uv",
           "args": ["--directory", "/path/to/your/ACI_MCP/aci_mcp", "run", "/path/to/your/ACI_MCP/aci_mcp/main.py"],
           "transport": "stdio"
       },
       "ios-agent": {
           "command": "/path/to/uv", 
           "args": ["--directory", "/path/to/your/MCP_Network_automator", "run", "/path/to/your/MCP_Network_automator/mcp_cisco_server.py"],
           "transport": "stdio"
       },
       # ... notify-agent configuration
   })
   ```

## 🚦 Usage

### Starting the FastAPI Server

```bash
# Using uvicorn directly
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Or using uv
uv run uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### API Endpoints

#### POST /agent
Send a request to the multi-agent system:

```bash
curl -X POST "http://localhost:8000/agent" \
     -H "Content-Type: application/json" \
     -d '{"input_text": "Configure VLAN 100 on all switches"}'
```

**Request Body:**
```json
{
  "input_text": "Your network configuration request or question"
}
```

**Response:**
```json
{
  "output_text": "Agent response with configuration details",
  "error": null
}
```

#### GET /
Health check endpoint:
```bash
curl http://localhost:8000/
```

### Example Requests

1. **Check device status:**
   ```json
   {"input_text": "Check the status of all routers"}
   ```

2. **Configure ACI policy:**
   ```json
   {"input_text": "Create a new EPG for web servers in ACI"}
   ```

3. **IOS configuration:**
   ```json
   {"input_text": "Configure OSPF area 0 on router R1"}
   ```

## 🔧 Configuration

### Network Devices
The system is pre-configured for the following test devices:

| Device | Type      | IP Address    | Credentials |
|--------|-----------|---------------|-------------|
| R1     | IOL XE    | 10.10.20.171  | cisco/cisco |
| R2     | IOL XE    | 10.10.20.172  | cisco/cisco |
| SW1    | IOL L2 XE | 10.10.20.173  | cisco/cisco |
| SW2    | IOL L2 XE | 10.10.20.174  | cisco/cisco |

### Agent Prompts
Each agent has specialized prompts:
- **Supervisor**: CCIE-level task coordination
- **ACI Agent**: Datacenter infrastructure expertise
- **IOS Agent**: Network device configuration
- **Notify Agent**: Slack communication

### MCP Servers
The system connects to three MCP servers. Configure the paths based on your MCP server locations:
- **aci-agent**: Path depends on where your ACI MCP server is installed (e.g., `/path/to/your/ACI_MCP/aci_mcp`)
- **ios-agent**: Path depends on where your Network Automator MCP server is installed (e.g., `/path/to/your/MCP_Network_automator`)
- **notify-agent**: Uses npm package `@modelcontextprotocol/server-slack`

**Note**: Update the paths in `graph.py` to match your MCP server installation locations.

## 📁 Project Structure

```
multi-agent-networking/
├── app.py              # FastAPI application
├── graph.py            # LangGraph workflow and agent definitions
├── langgraph.json      # LangGraph configuration
├── pyproject.toml      # Project dependencies
├── README.md           # This file
├── uv.lock            # Lock file for dependencies
└── __pycache__/       # Python cache files
```

## 🔍 Key Components

### `app.py`
- FastAPI application with REST endpoints
- Request/response models using Pydantic
- Async agent execution wrapper

### `graph.py`
- Multi-agent workflow definition
- MCP client configuration
- Agent prompts and LLM setup
- Supervisor pattern implementation

## 🐛 Troubleshooting

### Common Issues

1. **MCP Server Connection Failed**
   - Ensure all MCP server paths are correct
   - Check if UV is installed and accessible
   - Verify Node.js and npm packages are installed

2. **Google API Key Error**
   - Verify your Google Gemini API key is valid
   - Check the `.env` file configuration

3. **Slack Integration Issues**
   - Confirm Slack bot token has correct permissions
   - Verify the team ID is correct
   - Check channel ID in the notify prompt

### Debug Mode
Run with debug logging:
```bash
uv run uvicorn app:app --log-level debug
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

[Add your license information here]

## 📞 Support

For issues and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the MCP server logs

## 🔮 Future Enhancements

- [ ] Web UI for easier interaction
- [ ] Database integration for configuration history
- [ ] Additional network vendor support
- [ ] Real-time monitoring dashboard
- [ ] Configuration rollback capabilities
- [ ] Enhanced error handling and recovery

---

**Note**: This system requires access to actual network devices for full functionality. Ensure proper network access and credentials are configured before running network configuration commands.