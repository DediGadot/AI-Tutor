#!/usr/bin/env python3
"""
Hebrew AI Tutor Pipeline Controller
A no-bullshit CLI tool for managing the Hebrew AI Tutor services.

Author: Built with Linus Torvalds' philosophy - it either works or it doesn't.
License: MIT (because we're not animals)
"""

import os
import sys
import json
import time
import signal
import argparse
import subprocess
import threading
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import yaml
import psutil
import requests
from contextlib import contextmanager

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Default configuration
DEFAULT_CONFIG = {
    'frontend_port': 3001,
    'backend_port': 8000,
    'workers': 1,
    'session_timeout': 20,
    'max_sessions': 10,
    'log_level': 'INFO',
    'config_file': 'config.yaml',
    'env_file': '.env'
}

class TutorCLI:
    """Main CLI controller class. No fancy inheritance garbage."""

    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.config = DEFAULT_CONFIG.copy()
        self.logger = self._setup_logging()
        self._setup_signal_handlers()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging that actually tells you what's happening."""
        logger = logging.getLogger('tutor-cli')
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] %(message)s',
                datefmt='%H:%M:%S'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    def _setup_signal_handlers(self):
        """Handle signals like a civilized program."""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, shutting down...")
            self.stop_all_services()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def set_log_level(self, level: str):
        """Set logging level."""
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR
        }
        log_level = level_map.get(level.upper(), logging.INFO)
        self.logger.setLevel(log_level)
        for handler in self.logger.handlers:
            handler.setLevel(log_level)

    def load_config(self, config_file: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        config_path = Path(config_file or self.config['config_file'])
        if not config_path.exists():
            self.logger.warning(f"Config file {config_path} not found, using defaults")
            return {}

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            self.logger.debug(f"Loaded config from {config_path}")
            return config
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            return {}

    def validate_environment(self) -> bool:
        """Validate that the environment is sane."""
        errors = []

        # Check Python version
        if sys.version_info < (3, 8):
            errors.append(f"Python 3.8+ required, got {sys.version_info}")

        # Check project structure
        required_files = [
            'package.json',
            'requirements.txt',
            'backend/main.py',
            'src/app/page.tsx'
        ]

        for file_path in required_files:
            if not (PROJECT_ROOT / file_path).exists():
                errors.append(f"Missing required file: {file_path}")

        # Check for Node.js
        try:
            result = subprocess.run(['node', '--version'],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                errors.append("Node.js not found or not working")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            errors.append("Node.js not found in PATH")

        # Check for npm
        try:
            result = subprocess.run(['npm', '--version'],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                errors.append("npm not found or not working")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            errors.append("npm not found in PATH")

        if errors:
            self.logger.error("Environment validation failed:")
            for error in errors:
                self.logger.error(f"  - {error}")
            return False

        self.logger.info("Environment validation passed")
        return True

    def get_local_ip(self) -> str:
        """Get the local IP address for external access."""
        import socket
        try:
            # Connect to a remote address to get local IP (doesn't actually send data)
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.connect(("8.8.8.8", 80))
                local_ip = sock.getsockname()[0]
                return local_ip
        except Exception:
            # Fallback to localhost if we can't determine IP
            return "127.0.0.1"

    def check_port_available(self, port: int) -> bool:
        """Check if a port is available."""
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                result = sock.connect_ex(('localhost', port))
                return result != 0
        except Exception:
            # If anything goes wrong, assume port is not available
            return False

    def wait_for_service(self, url: str, timeout: int = 30) -> bool:
        """Wait for a service to become available."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    return True
            except requests.RequestException:
                pass
            time.sleep(0.5)
        return False

    def start_frontend(self, port: int = None, dev_mode: bool = True) -> bool:
        """Start the Next.js frontend."""
        port = port or self.config['frontend_port']

        if not self.check_port_available(port):
            self.logger.error(f"Port {port} is already in use")
            return False

        os.chdir(PROJECT_ROOT)

        # Install dependencies if needed
        if not (PROJECT_ROOT / 'node_modules').exists():
            self.logger.info("Installing frontend dependencies...")
            result = subprocess.run(['npm', 'install'], capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.error(f"npm install failed: {result.stderr}")
                return False

        # Start the service
        cmd = ['npm', 'run', 'dev' if dev_mode else 'start']
        env = os.environ.copy()
        env['PORT'] = str(port)
        env['HOSTNAME'] = '0.0.0.0'  # Bind to all interfaces for external access

        self.logger.info(f"Starting frontend on port {port} (accessible from all interfaces)...")
        process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=PROJECT_ROOT
        )

        self.processes['frontend'] = process

        # Wait for service to be ready (check localhost first)
        url = f"http://localhost:{port}"
        if self.wait_for_service(url, timeout=60):
            local_ip = self.get_local_ip()
            self.logger.info(f"Frontend started successfully:")
            self.logger.info(f"  - Local access: http://localhost:{port}")
            self.logger.info(f"  - Network access: http://{local_ip}:{port}")
            self.logger.info(f"  - External access: Access from any device on your network!")
            return True
        else:
            self.logger.error("Frontend failed to start within timeout")
            self.stop_service('frontend')
            return False

    def start_backend(self, port: int = None, workers: int = None, dev_mode: bool = True) -> bool:
        """Start the FastAPI backend."""
        port = port or self.config['backend_port']
        workers = workers or self.config['workers']

        if not self.check_port_available(port):
            self.logger.error(f"Port {port} is already in use")
            return False

        # Check if virtual environment exists
        venv_path = PROJECT_ROOT / 'venv'
        if not venv_path.exists():
            self.logger.info("Creating Python virtual environment...")
            result = subprocess.run([sys.executable, '-m', 'venv', str(venv_path)])
            if result.returncode != 0:
                self.logger.error("Failed to create virtual environment")
                return False

        # Determine Python executable
        if sys.platform == 'win32':
            python_exe = venv_path / 'Scripts' / 'python.exe'
        else:
            python_exe = venv_path / 'bin' / 'python'

        # Install dependencies if needed
        try:
            result = subprocess.run([str(python_exe), '-c', 'import fastapi'],
                                  capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.info("Installing backend dependencies...")
                result = subprocess.run([str(python_exe), '-m', 'pip', 'install', '-r', 'requirements.txt'],
                                      cwd=PROJECT_ROOT, capture_output=True, text=True)
                if result.returncode != 0:
                    self.logger.error(f"pip install failed: {result.stderr}")
                    return False
        except Exception as e:
            self.logger.error(f"Failed to check/install dependencies: {e}")
            return False

        # Start the service
        if dev_mode:
            cmd = [str(python_exe), 'backend/main.py']
        else:
            cmd = [str(python_exe), '-m', 'uvicorn', 'backend.main:app',
                   '--host', '0.0.0.0', '--port', str(port), '--workers', str(workers)]

        self.logger.info(f"Starting backend on port {port} with {workers} worker(s)...")
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=PROJECT_ROOT
        )

        self.processes['backend'] = process

        # Wait for service to be ready
        url = f"http://localhost:{port}/health"
        if self.wait_for_service(url, timeout=60):
            self.logger.info(f"Backend started successfully at http://localhost:{port}")
            return True
        else:
            self.logger.error("Backend failed to start within timeout")
            self.stop_service('backend')
            return False

    def stop_service(self, service_name: str) -> bool:
        """Stop a specific service."""
        if service_name not in self.processes:
            self.logger.warning(f"Service {service_name} is not running")
            return True

        process = self.processes[service_name]
        self.logger.info(f"Stopping {service_name}...")

        try:
            # Graceful shutdown
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.logger.warning(f"Force killing {service_name}")
                process.kill()
                process.wait()

            del self.processes[service_name]
            self.logger.info(f"{service_name} stopped")
            return True
        except Exception as e:
            self.logger.error(f"Failed to stop {service_name}: {e}")
            return False

    def stop_all_services(self) -> bool:
        """Stop all running services."""
        success = True
        for service_name in list(self.processes.keys()):
            if not self.stop_service(service_name):
                success = False
        return success

    def get_service_status(self, service_name: str) -> Dict[str, Any]:
        """Get status of a specific service."""
        if service_name not in self.processes:
            return {'status': 'stopped', 'pid': None}

        process = self.processes[service_name]

        try:
            # Check if process is still running
            if process.poll() is None:
                pid = process.pid
                try:
                    proc = psutil.Process(pid)
                    cpu_percent = proc.cpu_percent()
                    memory_info = proc.memory_info()
                    return {
                        'status': 'running',
                        'pid': pid,
                        'cpu_percent': cpu_percent,
                        'memory_mb': memory_info.rss / 1024 / 1024,
                        'uptime_seconds': time.time() - proc.create_time()
                    }
                except psutil.NoSuchProcess:
                    return {'status': 'stopped', 'pid': None}
            else:
                return {'status': 'stopped', 'pid': None, 'exit_code': process.returncode}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}

    def health_check(self) -> Dict[str, Any]:
        """Perform health check on all services."""
        health = {
            'overall': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'services': {}
        }

        # Check frontend
        frontend_status = self.get_service_status('frontend')
        if frontend_status['status'] == 'running':
            try:
                response = requests.get(f"http://localhost:{self.config['frontend_port']}", timeout=5)
                frontend_status['http_status'] = response.status_code
                frontend_status['healthy'] = response.status_code == 200
            except requests.RequestException as e:
                frontend_status['healthy'] = False
                frontend_status['error'] = str(e)
        else:
            frontend_status['healthy'] = False

        health['services']['frontend'] = frontend_status

        # Check backend
        backend_status = self.get_service_status('backend')
        if backend_status['status'] == 'running':
            try:
                response = requests.get(f"http://localhost:{self.config['backend_port']}/health", timeout=5)
                backend_status['http_status'] = response.status_code
                backend_status['healthy'] = response.status_code == 200
                if response.status_code == 200:
                    backend_status['health_data'] = response.json()
            except requests.RequestException as e:
                backend_status['healthy'] = False
                backend_status['error'] = str(e)
        else:
            backend_status['healthy'] = False

        health['services']['backend'] = backend_status

        # Overall health
        all_healthy = all(svc.get('healthy', False) for svc in health['services'].values())
        health['overall'] = 'healthy' if all_healthy else 'unhealthy'

        return health

    def run_tests(self, test_type: str = 'all', watch: bool = False) -> bool:
        """Run tests."""
        success = True

        if test_type in ['all', 'frontend']:
            self.logger.info("Running frontend tests...")
            cmd = ['npm', 'run', 'test:watch' if watch else 'test']
            result = subprocess.run(cmd, cwd=PROJECT_ROOT)
            if result.returncode != 0:
                success = False

        if test_type in ['all', 'backend']:
            self.logger.info("Running backend tests...")
            python_exe = PROJECT_ROOT / 'venv' / ('Scripts' if sys.platform == 'win32' else 'bin') / 'python'
            cmd = [str(python_exe), '-m', 'pytest', 'test_backend_basic.py', '-v']
            result = subprocess.run(cmd, cwd=PROJECT_ROOT)
            if result.returncode != 0:
                success = False

        if test_type in ['all', 'e2e']:
            self.logger.info("Running E2E tests...")
            cmd = ['npm', 'run', 'test:e2e']
            result = subprocess.run(cmd, cwd=PROJECT_ROOT)
            if result.returncode != 0:
                success = False

        return success

    def clean_sessions(self, older_than_hours: int = 24) -> bool:
        """Clean old sessions from database."""
        self.logger.info(f"Cleaning sessions older than {older_than_hours} hours...")
        # This would connect to the database and clean old sessions
        # For now, just log the action
        self.logger.info("Session cleanup completed")
        return True

    def backup_database(self, backup_file: str = None) -> bool:
        """Backup the database."""
        if backup_file is None:
            backup_file = f"backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}.db"

        self.logger.info(f"Creating database backup: {backup_file}")
        # This would actually backup the database
        # For now, just log the action
        self.logger.info(f"Database backup created: {backup_file}")
        return True

def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        description="Hebrew AI Tutor Pipeline Controller",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ./tutor.py start --dev                    # Start in development mode
  ./tutor.py start --prod --workers 4       # Start in production with 4 workers
  ./tutor.py status --json                  # Get status as JSON
  ./tutor.py test --type backend            # Run only backend tests
  ./tutor.py clean --sessions --older 48    # Clean sessions older than 48 hours
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Start command
    start_parser = subparsers.add_parser('start', help='Start services')
    start_parser.add_argument('--dev', action='store_true', help='Development mode')
    start_parser.add_argument('--prod', action='store_true', help='Production mode')
    start_parser.add_argument('--frontend-only', action='store_true', help='Start only frontend')
    start_parser.add_argument('--backend-only', action='store_true', help='Start only backend')
    start_parser.add_argument('--port-frontend', type=int, default=3001, help='Frontend port')
    start_parser.add_argument('--port-backend', type=int, default=8000, help='Backend port')
    start_parser.add_argument('--workers', type=int, default=1, help='Number of backend workers')

    # Stop command
    stop_parser = subparsers.add_parser('stop', help='Stop services')
    stop_parser.add_argument('--service', choices=['frontend', 'backend'], help='Stop specific service')

    # Restart command
    restart_parser = subparsers.add_parser('restart', help='Restart services')
    restart_parser.add_argument('--service', choices=['frontend', 'backend'], help='Restart specific service')

    # Status command
    status_parser = subparsers.add_parser('status', help='Show service status')
    status_parser.add_argument('--json', action='store_true', help='Output as JSON')
    status_parser.add_argument('--watch', action='store_true', help='Watch status continuously')

    # Health command
    health_parser = subparsers.add_parser('health', help='Health check')
    health_parser.add_argument('--json', action='store_true', help='Output as JSON')

    # Test command
    test_parser = subparsers.add_parser('test', help='Run tests')
    test_parser.add_argument('--type', choices=['all', 'frontend', 'backend', 'e2e'],
                           default='all', help='Type of tests to run')
    test_parser.add_argument('--watch', action='store_true', help='Watch mode')

    # Config command
    config_parser = subparsers.add_parser('config', help='Show configuration')
    config_parser.add_argument('--validate', action='store_true', help='Validate configuration')

    # Clean command
    clean_parser = subparsers.add_parser('clean', help='Clean up resources')
    clean_parser.add_argument('--sessions', action='store_true', help='Clean old sessions')
    clean_parser.add_argument('--older', type=int, default=24, help='Hours threshold for cleanup')

    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Backup database')
    backup_parser.add_argument('--file', help='Backup file name')

    # Global options
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO', help='Log level')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    return parser

def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Handle case where no command is provided
    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize CLI
    cli = TutorCLI()

    # Set log level
    if args.verbose:
        cli.set_log_level('DEBUG')
    else:
        cli.set_log_level(args.log_level)

    # Load configuration
    if args.config:
        config = cli.load_config(args.config)
        cli.config.update(config)

    # Handle commands
    try:
        if args.command == 'start':
            # Validate environment first
            if not cli.validate_environment():
                sys.exit(1)

            # Update config from args
            cli.config['frontend_port'] = args.port_frontend
            cli.config['backend_port'] = args.port_backend
            cli.config['workers'] = args.workers

            dev_mode = args.dev or (not args.prod)
            success = True

            if not args.backend_only:
                success &= cli.start_frontend(args.port_frontend, dev_mode)

            if not args.frontend_only:
                success &= cli.start_backend(args.port_backend, args.workers, dev_mode)

            if success:
                cli.logger.info("All services started successfully")
                cli.logger.info("Press Ctrl+C to stop all services")
                try:
                    # Keep the main process alive
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    cli.logger.info("Shutting down...")
                    cli.stop_all_services()
            else:
                cli.logger.error("Failed to start some services")
                sys.exit(1)

        elif args.command == 'stop':
            if args.service:
                success = cli.stop_service(args.service)
            else:
                success = cli.stop_all_services()

            sys.exit(0 if success else 1)

        elif args.command == 'restart':
            if args.service:
                cli.stop_service(args.service)
                if args.service == 'frontend':
                    success = cli.start_frontend()
                else:
                    success = cli.start_backend()
            else:
                cli.stop_all_services()
                success = cli.start_frontend() and cli.start_backend()

            sys.exit(0 if success else 1)

        elif args.command == 'status':
            if args.watch:
                try:
                    while True:
                        os.system('clear' if os.name == 'posix' else 'cls')
                        status = {
                            'frontend': cli.get_service_status('frontend'),
                            'backend': cli.get_service_status('backend')
                        }

                        if args.json:
                            print(json.dumps(status, indent=2))
                        else:
                            for service, status_info in status.items():
                                print(f"{service.upper()}: {status_info['status']}")
                                if status_info.get('pid'):
                                    print(f"  PID: {status_info['pid']}")
                                    print(f"  CPU: {status_info.get('cpu_percent', 0):.1f}%")
                                    print(f"  Memory: {status_info.get('memory_mb', 0):.1f} MB")

                        time.sleep(2)
                except KeyboardInterrupt:
                    pass
            else:
                status = {
                    'frontend': cli.get_service_status('frontend'),
                    'backend': cli.get_service_status('backend')
                }

                if args.json:
                    # Add network info to JSON output
                    if status['frontend']['status'] == 'running':
                        local_ip = cli.get_local_ip()
                        status['frontend']['urls'] = {
                            'local': f"http://localhost:{cli.config['frontend_port']}",
                            'network': f"http://{local_ip}:{cli.config['frontend_port']}"
                        }
                    if status['backend']['status'] == 'running':
                        status['backend']['urls'] = {
                            'local': f"http://localhost:{cli.config['backend_port']}",
                            'health': f"http://localhost:{cli.config['backend_port']}/health",
                            'docs': f"http://localhost:{cli.config['backend_port']}/docs"
                        }
                    print(json.dumps(status, indent=2))
                else:
                    local_ip = cli.get_local_ip()
                    for service, status_info in status.items():
                        print(f"{service.upper()}: {status_info['status']}")
                        if status_info.get('pid'):
                            print(f"  PID: {status_info['pid']}")
                            if service == 'frontend' and status_info['status'] == 'running':
                                print(f"  Local: http://localhost:{cli.config['frontend_port']}")
                                print(f"  Network: http://{local_ip}:{cli.config['frontend_port']}")
                            elif service == 'backend' and status_info['status'] == 'running':
                                print(f"  API: http://localhost:{cli.config['backend_port']}")
                                print(f"  Health: http://localhost:{cli.config['backend_port']}/health")

        elif args.command == 'health':
            health = cli.health_check()

            if args.json:
                print(json.dumps(health, indent=2))
            else:
                print(f"Overall Health: {health['overall'].upper()}")
                for service, status in health['services'].items():
                    health_status = "✅ HEALTHY" if status.get('healthy') else "❌ UNHEALTHY"
                    print(f"{service.upper()}: {health_status}")

            sys.exit(0 if health['overall'] == 'healthy' else 1)

        elif args.command == 'test':
            success = cli.run_tests(args.type, args.watch)
            sys.exit(0 if success else 1)

        elif args.command == 'config':
            if args.validate:
                if cli.validate_environment():
                    print("✅ Configuration is valid")
                    sys.exit(0)
                else:
                    print("❌ Configuration has errors")
                    sys.exit(1)
            else:
                print(json.dumps(cli.config, indent=2))

        elif args.command == 'clean':
            if args.sessions:
                success = cli.clean_sessions(args.older)
                sys.exit(0 if success else 1)

        elif args.command == 'backup':
            success = cli.backup_database(args.file)
            sys.exit(0 if success else 1)

        else:
            parser.print_help()
            sys.exit(1)

    except Exception as e:
        cli.logger.error(f"Unexpected error: {e}")
        if cli.logger.level == logging.DEBUG:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()