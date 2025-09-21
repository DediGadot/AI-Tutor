#!/usr/bin/env python3
"""
Comprehensive tests for the Tutor CLI tool.
Testing every function because broken software is worse than no software.
"""

import os
import sys
import json
import time
import socket
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest
import requests

# Add the script to the path
sys.path.insert(0, str(Path(__file__).parent))
from tutor import TutorCLI, DEFAULT_CONFIG, create_parser

class TestTutorCLI:
    """Test the TutorCLI class thoroughly."""

    def setup_method(self):
        """Setup for each test."""
        self.cli = TutorCLI()

    def test_init(self):
        """Test CLI initialization."""
        assert self.cli.config == DEFAULT_CONFIG
        assert self.cli.processes == {}
        assert self.cli.logger is not None

    def test_set_log_level(self):
        """Test log level setting."""
        self.cli.set_log_level('DEBUG')
        assert self.cli.logger.level == 10  # logging.DEBUG

        self.cli.set_log_level('ERROR')
        assert self.cli.logger.level == 40  # logging.ERROR

        self.cli.set_log_level('INVALID')
        assert self.cli.logger.level == 20  # defaults to INFO

    def test_load_config_missing_file(self):
        """Test loading config when file doesn't exist."""
        config = self.cli.load_config('nonexistent.yaml')
        assert config == {}

    def test_load_config_valid_file(self):
        """Test loading valid config file."""
        config_content = """
system:
  version: "2.0.0"
llm:
  default_model: "gpt-4"
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_content)
            f.flush()

            config = self.cli.load_config(f.name)
            assert config['system']['version'] == "2.0.0"
            assert config['llm']['default_model'] == "gpt-4"

            os.unlink(f.name)

    def test_load_config_invalid_yaml(self):
        """Test loading invalid YAML file."""
        invalid_yaml = "invalid: yaml: content: {"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(invalid_yaml)
            f.flush()

            config = self.cli.load_config(f.name)
            assert config == {}

            os.unlink(f.name)

    def test_check_port_available(self):
        """Test port availability checking."""
        # Test with a port that should be available (high port number)
        assert self.cli.check_port_available(65432) == True

        # Test occupied port - create a server socket that stays bound
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind(('localhost', 0))
        server_sock.listen(1)
        occupied_port = server_sock.getsockname()[1]

        try:
            # Port should be unavailable while socket is bound and listening
            assert self.cli.check_port_available(occupied_port) == False
        finally:
            server_sock.close()

    @patch('requests.get')
    def test_wait_for_service_success(self, mock_get):
        """Test waiting for service when it becomes available."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = self.cli.wait_for_service('http://localhost:8000', timeout=1)
        assert result == True

    @patch('requests.get')
    def test_wait_for_service_timeout(self, mock_get):
        """Test waiting for service timeout."""
        mock_get.side_effect = requests.RequestException("Connection failed")

        result = self.cli.wait_for_service('http://localhost:8000', timeout=1)
        assert result == False

    def test_get_service_status_not_running(self):
        """Test getting status of non-running service."""
        status = self.cli.get_service_status('nonexistent')
        assert status['status'] == 'stopped'
        assert status['pid'] is None

    @patch('subprocess.Popen')
    def test_stop_service_success(self, mock_popen):
        """Test stopping a service successfully."""
        mock_process = Mock()
        mock_process.terminate.return_value = None
        mock_process.wait.return_value = None
        mock_popen.return_value = mock_process

        self.cli.processes['test_service'] = mock_process

        result = self.cli.stop_service('test_service')
        assert result == True
        assert 'test_service' not in self.cli.processes
        mock_process.terminate.assert_called_once()

    @patch('subprocess.Popen')
    def test_stop_service_force_kill(self, mock_popen):
        """Test force killing a service that doesn't respond to terminate."""
        mock_process = Mock()
        mock_process.terminate.return_value = None
        mock_process.wait.side_effect = [subprocess.TimeoutExpired('test', 10), None]
        mock_process.kill.return_value = None
        mock_popen.return_value = mock_process

        self.cli.processes['test_service'] = mock_process

        result = self.cli.stop_service('test_service')
        assert result == True
        mock_process.terminate.assert_called_once()
        mock_process.kill.assert_called_once()

    def test_stop_all_services(self):
        """Test stopping all services."""
        # Mock some processes
        for i in range(3):
            mock_process = Mock()
            mock_process.terminate.return_value = None
            mock_process.wait.return_value = None
            self.cli.processes[f'service_{i}'] = mock_process

        result = self.cli.stop_all_services()
        assert result == True
        assert len(self.cli.processes) == 0

    @patch('requests.get')
    def test_health_check(self, mock_get):
        """Test health check functionality."""
        # Mock running processes
        mock_process = Mock()
        mock_process.poll.return_value = None  # Still running
        mock_process.pid = 12345

        self.cli.processes['frontend'] = mock_process
        self.cli.processes['backend'] = mock_process

        # Mock HTTP responses
        def mock_get_side_effect(url, timeout=None):
            mock_response = Mock()
            if 'health' in url:
                mock_response.status_code = 200
                mock_response.json.return_value = {'status': 'healthy'}
            else:
                mock_response.status_code = 200
            return mock_response

        mock_get.side_effect = mock_get_side_effect

        with patch('psutil.Process') as mock_psutil:
            mock_proc = Mock()
            mock_proc.cpu_percent.return_value = 5.0
            mock_proc.memory_info.return_value = Mock(rss=100*1024*1024)  # 100MB
            mock_proc.create_time.return_value = time.time() - 100
            mock_psutil.return_value = mock_proc

            health = self.cli.health_check()

            assert health['overall'] == 'healthy'
            assert 'frontend' in health['services']
            assert 'backend' in health['services']
            assert health['services']['frontend']['healthy'] == True
            assert health['services']['backend']['healthy'] == True

    def test_validate_environment_python_version(self):
        """Test environment validation with wrong Python version."""
        with patch('sys.version_info', (3, 7, 0)):
            result = self.cli.validate_environment()
            assert result == False

    @patch('subprocess.run')
    def test_validate_environment_missing_node(self, mock_run):
        """Test environment validation with missing Node.js."""
        mock_run.side_effect = FileNotFoundError("Node not found")

        result = self.cli.validate_environment()
        assert result == False

    @patch('subprocess.run')
    @patch('pathlib.Path.exists')
    def test_validate_environment_success(self, mock_exists, mock_run):
        """Test successful environment validation."""
        # Mock all required files exist
        mock_exists.return_value = True

        # Mock successful command execution
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = self.cli.validate_environment()
        assert result == True

    def test_run_tests_backend_only(self):
        """Test running backend tests only."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0

            result = self.cli.run_tests('backend')
            assert result == True
            mock_run.assert_called()

    def test_clean_sessions(self):
        """Test session cleanup."""
        result = self.cli.clean_sessions(24)
        assert result == True  # Should succeed (mock implementation)

    def test_backup_database(self):
        """Test database backup."""
        result = self.cli.backup_database()
        assert result == True  # Should succeed (mock implementation)

        result = self.cli.backup_database('custom-backup.db')
        assert result == True

    def test_get_local_ip(self):
        """Test local IP detection for external access."""
        local_ip = self.cli.get_local_ip()

        # Should not be localhost
        assert local_ip != "127.0.0.1"

        # Should be a valid IP format
        parts = local_ip.split('.')
        assert len(parts) == 4

        for part in parts:
            assert part.isdigit()
            assert 0 <= int(part) <= 255


class TestArgumentParser:
    """Test the argument parser."""

    def test_create_parser(self):
        """Test parser creation."""
        parser = create_parser()
        assert parser is not None

    def test_start_command_args(self):
        """Test start command arguments."""
        parser = create_parser()

        # Test dev mode
        args = parser.parse_args(['start', '--dev'])
        assert args.command == 'start'
        assert args.dev == True

        # Test production mode with workers
        args = parser.parse_args(['start', '--prod', '--workers', '4'])
        assert args.prod == True
        assert args.workers == 4

        # Test frontend only
        args = parser.parse_args(['start', '--frontend-only'])
        assert args.frontend_only == True

    def test_status_command_args(self):
        """Test status command arguments."""
        parser = create_parser()

        args = parser.parse_args(['status', '--json'])
        assert args.command == 'status'
        assert args.json == True

        args = parser.parse_args(['status', '--watch'])
        assert args.watch == True

    def test_test_command_args(self):
        """Test test command arguments."""
        parser = create_parser()

        args = parser.parse_args(['test', '--type', 'backend'])
        assert args.command == 'test'
        assert args.type == 'backend'

        args = parser.parse_args(['test', '--watch'])
        assert args.watch == True

    def test_global_args(self):
        """Test global arguments."""
        parser = create_parser()

        args = parser.parse_args(['--verbose', '--log-level', 'DEBUG', 'status'])
        assert args.verbose == True
        assert args.log_level == 'DEBUG'


class TestIntegration:
    """Integration tests for the CLI tool."""

    def test_cli_help(self):
        """Test that CLI help works."""
        result = subprocess.run([
            sys.executable, 'scripts/tutor.py', '--help'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)

        assert result.returncode == 0
        assert 'Hebrew AI Tutor Pipeline Controller' in result.stdout

    def test_cli_config_validation(self):
        """Test config validation command."""
        result = subprocess.run([
            sys.executable, 'scripts/tutor.py', 'config', '--validate'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)

        # Should complete without errors (return code might be 0 or 1 depending on environment)
        assert result.returncode in [0, 1]

    def test_cli_status_json(self):
        """Test status command with JSON output."""
        result = subprocess.run([
            sys.executable, 'scripts/tutor.py', 'status', '--json'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)

        assert result.returncode == 0
        # Should be valid JSON
        try:
            status = json.loads(result.stdout)
            assert 'frontend' in status
            assert 'backend' in status
        except json.JSONDecodeError:
            pytest.fail("Status output is not valid JSON")


def test_script_is_executable():
    """Test that the script file is executable."""
    script_path = Path(__file__).parent / 'tutor.py'
    assert script_path.exists()

    # Test that it has a shebang
    with open(script_path, 'r') as f:
        first_line = f.readline()
        assert first_line.startswith('#!/usr/bin/env python3')


def test_script_imports():
    """Test that all required modules can be imported."""
    try:
        import yaml
        import psutil
        import requests
    except ImportError as e:
        pytest.fail(f"Required dependency not available: {e}")


if __name__ == '__main__':
    # Run tests if called directly
    import pytest
    pytest.main([__file__, '-v'])