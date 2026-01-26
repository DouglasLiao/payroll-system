#!/usr/bin/env python3
"""
SSH Manager for SaaS Node
Purpose: Secure SSH connection management for remote CasaOS server operations
Author: Auto-generated
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Optional, List, Tuple
from dotenv import load_dotenv

try:
    import paramiko
except ImportError:
    print("Error: paramiko is required. Install with: pip install paramiko")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SSHManager:
    """Manages SSH connections to the SaaS node infrastructure."""

    def __init__(
        self,
        host: str,
        username: str,
        password: Optional[str] = None,
        key_path: Optional[Path] = None,
        port: int = 22,
    ):
        """
        Initialize SSH manager.

        Args:
            host: Hostname or IP address
            username: SSH username
            password: SSH password (optional if using key)
            key_path: Path to SSH private key (optional if using password)
            port: SSH port (default: 22)
        """
        self.host = host
        self.username = username
        self.password = password
        self.key_path = key_path
        self.port = port
        self.client: Optional[paramiko.SSHClient] = None

    def connect(self) -> None:
        """
        Establish SSH connection.

        Raises:
            Exception: If connection fails
        """
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            connect_kwargs = {
                "hostname": self.host,
                "username": self.username,
                "port": self.port,
            }

            if self.key_path:
                logger.info(f"Connecting with SSH key: {self.key_path}")
                connect_kwargs["key_filename"] = str(self.key_path)
            elif self.password:
                logger.info("Connecting with password")
                connect_kwargs["password"] = self.password
            else:
                raise ValueError("Either password or key_path must be provided")

            self.client.connect(**connect_kwargs)
            logger.info(f"Successfully connected to {self.host}")

        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            raise

    def execute_command(self, command: str) -> Tuple[str, str, int]:
        """
        Execute a command on the remote server.

        Args:
            command: Command to execute

        Returns:
            Tuple of (stdout, stderr, exit_code)

        Raises:
            RuntimeError: If not connected
        """
        if not self.client:
            raise RuntimeError("Not connected. Call connect() first.")

        try:
            logger.info(f"Executing: {command}")
            stdin, stdout, stderr = self.client.exec_command(command)

            exit_code = stdout.channel.recv_exit_status()
            stdout_str = stdout.read().decode("utf-8")
            stderr_str = stderr.read().decode("utf-8")

            if exit_code == 0:
                logger.info("Command executed successfully")
            else:
                logger.warning(f"Command exited with code {exit_code}")

            return stdout_str, stderr_str, exit_code

        except Exception as e:
            logger.error(f"Error executing command: {e}")
            raise

    def execute_commands(self, commands: List[str]) -> List[Tuple[str, str, int]]:
        """
        Execute multiple commands sequentially.

        Args:
            commands: List of commands to execute

        Returns:
            List of (stdout, stderr, exit_code) tuples
        """
        results = []
        for cmd in commands:
            result = self.execute_command(cmd)
            results.append(result)
        return results

    def disconnect(self) -> None:
        """Close the SSH connection."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from server")
            self.client = None

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="SSH Manager for SaaS Node Infrastructure"
    )
    parser.add_argument(
        "--host",
        default=os.getenv("SAAS_NODE_HOST", "192.168.31.88"),
        help="SSH host (default: from SAAS_NODE_HOST env var)",
    )
    parser.add_argument(
        "--user",
        default=os.getenv("SAAS_NODE_SSH_USER"),
        help="SSH username (default: from SAAS_NODE_SSH_USER env var)",
    )
    parser.add_argument(
        "--password",
        default=os.getenv("SAAS_NODE_SSH_PASSWORD"),
        help="SSH password (default: from SAAS_NODE_SSH_PASSWORD env var)",
    )
    parser.add_argument(
        "--key",
        type=Path,
        default=os.getenv("SAAS_NODE_SSH_KEY_PATH"),
        help="SSH private key path (default: from SAAS_NODE_SSH_KEY_PATH env var)",
    )
    parser.add_argument("--port", type=int, default=22, help="SSH port (default: 22)")
    parser.add_argument("--command", "-c", help="Single command to execute")
    parser.add_argument(
        "--commands-file", type=Path, help="File containing commands (one per line)"
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Validate credentials
    if not args.user:
        logger.error("Username is required (--user or SAAS_NODE_SSH_USER)")
        sys.exit(1)

    if not args.password and not args.key:
        logger.error("Either password or SSH key is required")
        sys.exit(1)

    try:
        # Create SSH manager
        manager = SSHManager(
            host=args.host,
            username=args.user,
            password=args.password,
            key_path=Path(args.key) if args.key else None,
            port=args.port,
        )

        with manager:
            if args.command:
                # Execute single command
                stdout, stderr, exit_code = manager.execute_command(args.command)
                print(stdout, end="")
                if stderr:
                    print(stderr, end="", file=sys.stderr)
                sys.exit(exit_code)

            elif args.commands_file:
                # Execute commands from file
                if not args.commands_file.exists():
                    logger.error(f"Commands file not found: {args.commands_file}")
                    sys.exit(1)

                with open(args.commands_file, "r") as f:
                    commands = [
                        line.strip()
                        for line in f
                        if line.strip() and not line.startswith("#")
                    ]

                results = manager.execute_commands(commands)
                for i, (stdout, stderr, exit_code) in enumerate(results):
                    print(f"\n=== Command {i+1}: {commands[i]} ===")
                    print(stdout, end="")
                    if stderr:
                        print(stderr, end="", file=sys.stderr)
                    print(f"Exit code: {exit_code}")
            else:
                # Interactive mode - just test connection
                logger.info("Connection test successful!")
                print(f"✓ Successfully connected to {args.host}")

        logger.info("Script completed successfully")

    except Exception as e:
        logger.error(f"Script failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
