# Hebrew AI Tutor CLI Tool

A no-bullshit command-line interface for managing the Hebrew AI Tutor pipeline services. Built with Linus Torvalds' philosophy: it either works or it doesn't.

## Quick Start

```bash
# Make the script executable
chmod +x scripts/tutor.py

# Start everything in development mode
./scripts/tutor.py start --dev

# Check what's running
./scripts/tutor.py status

# Stop everything
./scripts/tutor.py stop
```

## Installation

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm
- Virtual environment (recommended)

### Setup

```bash
# Install dependencies in virtual environment
source venv/bin/activate
pip install psutil pyyaml requests

# Or use the requirements.txt
pip install -r requirements.txt
```

## Commands

### Service Management

```bash
# Start services (automatically configured for network access!)
./scripts/tutor.py start                    # Start both frontend and backend
./scripts/tutor.py start --dev              # Development mode (hot reload)
./scripts/tutor.py start --prod             # Production mode
./scripts/tutor.py start --frontend-only    # Only start Next.js frontend
./scripts/tutor.py start --backend-only     # Only start FastAPI backend

# Custom ports and workers
./scripts/tutor.py start --port-frontend 3002 --port-backend 8001 --workers 4

# Stop services
./scripts/tutor.py stop                     # Stop all services
./scripts/tutor.py stop --service frontend  # Stop specific service

# Restart services
./scripts/tutor.py restart                  # Restart all
./scripts/tutor.py restart --service backend # Restart specific service
```

### 🌐 Network Access

The CLI tool automatically configures the frontend for external network access:

```bash
# When you start the frontend, you'll see:
./scripts/tutor.py start --dev

# Output shows:
# Frontend started successfully:
#   - Local access: http://localhost:3001
#   - Network access: http://192.168.1.100:3001
#   - External access: Access from any device on your network!

# Check network URLs anytime:
./scripts/tutor.py status                   # Shows local and network URLs

# Perfect for classrooms - students can access from tablets/phones!
```

### Monitoring

```bash
# Service status
./scripts/tutor.py status                   # Human-readable status
./scripts/tutor.py status --json            # JSON output
./scripts/tutor.py status --watch           # Continuous monitoring

# Health checks
./scripts/tutor.py health                   # Overall health check
./scripts/tutor.py health --json            # JSON output
```

### Development Tools

```bash
# Run tests
./scripts/tutor.py test                     # Run all tests
./scripts/tutor.py test --type backend      # Backend tests only
./scripts/tutor.py test --type frontend     # Frontend tests only
./scripts/tutor.py test --type e2e          # End-to-end tests
./scripts/tutor.py test --watch             # Watch mode

# Configuration
./scripts/tutor.py config                   # Show current config
./scripts/tutor.py config --validate        # Validate environment
```

### Maintenance

```bash
# Clean up
./scripts/tutor.py clean --sessions         # Clean old sessions
./scripts/tutor.py clean --sessions --older 48  # Clean sessions > 48 hours

# Database backup
./scripts/tutor.py backup                   # Auto-named backup
./scripts/tutor.py backup --file my-backup.db   # Custom filename
```

### Global Options

```bash
# Available for all commands
--config FILE                               # Use custom config file
--log-level DEBUG|INFO|WARNING|ERROR       # Set log verbosity
--verbose                                   # Enable verbose output

# Example
./scripts/tutor.py --verbose --log-level DEBUG status
```

## Configuration

The tool uses the following configuration sources (in order of precedence):

1. Command-line arguments
2. Custom config file (via `--config`)
3. Default `config.yaml`
4. Built-in defaults

### Default Configuration

```yaml
frontend_port: 3001
backend_port: 8000
workers: 1
session_timeout: 20
max_sessions: 10
log_level: INFO
config_file: config.yaml
env_file: .env
```

## Examples

### Development Workflow

```bash
# Start development environment
./scripts/tutor.py start --dev

# In another terminal, run tests in watch mode
./scripts/tutor.py test --watch

# Check status
./scripts/tutor.py status --json | jq '.frontend.status'

# Stop when done
./scripts/tutor.py stop
```

### Production Deployment

```bash
# Validate environment first
./scripts/tutor.py config --validate

# Start production services
./scripts/tutor.py start --prod --workers 4

# Monitor health
./scripts/tutor.py health --json

# Set up monitoring
watch -n 5 './scripts/tutor.py status'
```

### Troubleshooting

```bash
# Check environment
./scripts/tutor.py config --validate

# Verbose output for debugging
./scripts/tutor.py --verbose --log-level DEBUG start --dev

# Check ports are available
netstat -tulpn | grep :3001
netstat -tulpn | grep :8000

# Force stop if needed
pkill -f "next"
pkill -f "uvicorn"
```

## Features

### ✅ What Works

- **Service Management**: Start/stop/restart frontend and backend services
- **Environment Validation**: Checks Python, Node.js, npm, and project structure
- **Health Monitoring**: HTTP health checks with JSON output
- **Process Management**: Graceful shutdown with SIGTERM, force kill if needed
- **Port Management**: Automatic port availability checking
- **Configuration**: YAML config loading with environment variable substitution
- **Logging**: Structured logging with configurable levels
- **Testing Integration**: Run frontend, backend, and E2E tests
- **Signal Handling**: Proper cleanup on Ctrl+C
- **Cross-platform**: Works on Linux, macOS, and Windows

### 🚧 Limitations

- Database operations are placeholder (clean/backup log but don't execute)
- LLM integration requires actual API keys and configuration
- Some advanced features need the full application stack

### 🧪 Testing

The tool includes comprehensive tests covering:

- **Unit Tests**: All CLI functions and argument parsing
- **Integration Tests**: Real CLI execution and JSON output
- **Error Handling**: Invalid configs, missing dependencies, port conflicts
- **Cross-platform**: Socket handling, process management

```bash
# Run the test suite
source venv/bin/activate
python -m pytest scripts/test_tutor_cli.py -v

# All 29 tests should pass
```

## Architecture

### Design Philosophy

This tool follows Linus Torvalds' approach to software:

1. **Simple defaults that just work** - `./tutor.py start` does what you expect
2. **No magic** - Clear error messages, predictable behavior
3. **Fast startup** - Minimal overhead, quick validation
4. **Unix philosophy** - Does one thing well, composes with other tools
5. **Debuggable** - Verbose mode shows exactly what's happening

### Code Structure

```
scripts/
├── tutor.py              # Main CLI script (681 lines)
├── test_tutor_cli.py     # Comprehensive test suite (29 tests)
└── README.md             # This documentation
```

### Key Classes

- **TutorCLI**: Main controller class with service management
- **Process Management**: Start/stop services with proper cleanup
- **Health Checking**: HTTP-based service health validation
- **Configuration**: YAML loading with environment validation

## Error Handling

The tool handles common errors gracefully:

```bash
# Missing dependencies
❌ Node.js not found in PATH

# Port conflicts
❌ Port 3001 is already in use

# Invalid configuration
❌ Configuration has errors

# Service failures
❌ Frontend failed to start within timeout
```

## Contributing

### Adding New Commands

1. Add the command to `create_parser()`
2. Implement the logic in `main()`
3. Add corresponding tests
4. Update this documentation

### Testing

Always add tests for new functionality:

```python
def test_new_feature(self):
    """Test the new feature thoroughly."""
    # Test normal case
    assert self.cli.new_feature() == expected_result

    # Test error cases
    with pytest.raises(ExpectedError):
        self.cli.new_feature(invalid_input)
```

### Code Style

- Follow existing patterns
- Use type hints where helpful
- Add docstrings for public methods
- Handle errors explicitly
- Log important actions

## License

MIT License - because we're not animals.

## Support

If it's broken, fix it. If you can't fix it, open an issue with:

1. Exact command you ran
2. Full error output
3. Your environment (OS, Python version, Node version)
4. What you expected to happen

**Built with ❤️ and a healthy dose of pragmatism.**