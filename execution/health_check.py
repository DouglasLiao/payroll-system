#!/usr/bin/env python3
"""
Health Check for SaaS Node
Purpose: Monitor all infrastructure services and generate health reports
Author: Auto-generated
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv

try:
    import requests
except ImportError:
    print("Error: requests is required. Install with: pip install requests")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ServiceHealthChecker:
    """Health checker for SaaS node infrastructure services."""

    # Service definitions from manage_saas_node.md
    SERVICES = [
        {
            "name": "Nginx Proxy Manager",
            "url": "http://192.168.31.88:80",
            "critical": True,
            "description": "Gateway Reverso & SSL",
        },
        {
            "name": "NPM Admin",
            "url": "http://192.168.31.88:81",
            "critical": True,
            "description": "Gestão de Domínios",
        },
        {
            "name": "Coolify (PaaS)",
            "url": "http://192.168.31.88:8000",
            "critical": True,
            "description": "CI/CD & Automação",
        },
        {
            "name": "Cloudflared",
            "url": "http://192.168.31.88:14333",
            "critical": True,
            "description": "Túnel Seguro (Zero Trust)",
        },
        {
            "name": "AdGuard Home",
            "url": "http://192.168.31.88:3001",
            "critical": False,
            "description": "DNS Sinkhole Local",
        },
        {
            "name": "CasaOS Dashboard",
            "url": "http://192.168.31.88:89",
            "critical": True,
            "description": "Gestão do Servidor",
        },
    ]

    def __init__(self, host: str = "192.168.31.88", timeout: int = 5):
        """
        Initialize health checker.

        Args:
            host: Host IP address
            timeout: HTTP request timeout in seconds
        """
        self.host = host
        self.timeout = timeout
        self.results: List[Dict] = []

    def check_http_endpoint(self, service: Dict) -> Dict:
        """
        Check if an HTTP endpoint is responding.

        Args:
            service: Service configuration dict

        Returns:
            Health check result dict
        """
        result = {
            "name": service["name"],
            "url": service["url"],
            "critical": service["critical"],
            "description": service["description"],
            "status": "unknown",
            "response_time": None,
            "error": None,
            "timestamp": datetime.now().isoformat(),
        }

        try:
            logger.info(f"Checking {service['name']}...")
            response = requests.get(
                service["url"],
                timeout=self.timeout,
                allow_redirects=True,
                verify=False,  # For local network usage
            )

            result["response_time"] = response.elapsed.total_seconds()

            if response.status_code < 400:
                result["status"] = "healthy"
                logger.info(f"✓ {service['name']} is healthy ({response.status_code})")
            else:
                result["status"] = "degraded"
                result["error"] = f"HTTP {response.status_code}"
                logger.warning(f"⚠ {service['name']} returned {response.status_code}")

        except requests.exceptions.Timeout:
            result["status"] = "unhealthy"
            result["error"] = "Request timeout"
            logger.error(f"✗ {service['name']} timeout")

        except requests.exceptions.ConnectionError:
            result["status"] = "unhealthy"
            result["error"] = "Connection failed"
            logger.error(f"✗ {service['name']} connection failed")

        except Exception as e:
            result["status"] = "unhealthy"
            result["error"] = str(e)
            logger.error(f"✗ {service['name']} error: {e}")

        return result

    def check_docker_containers(self) -> Dict:
        """
        Check Docker container statuses via SSH.

        Returns:
            Docker health check result
        """
        # This requires SSH access - we'll use the ssh_manager if available
        result = {
            "name": "Docker Containers",
            "status": "skipped",
            "error": "SSH check not implemented in standalone mode",
            "timestamp": datetime.now().isoformat(),
        }

        # Check if ssh_manager is available
        ssh_user = os.getenv("SAAS_NODE_SSH_USER")
        if ssh_user:
            try:
                from ssh_manager import SSHManager

                manager = SSHManager(
                    host=self.host,
                    username=ssh_user,
                    password=os.getenv("SAAS_NODE_SSH_PASSWORD"),
                    key_path=(
                        Path(os.getenv("SAAS_NODE_SSH_KEY_PATH"))
                        if os.getenv("SAAS_NODE_SSH_KEY_PATH")
                        else None
                    ),
                )

                with manager:
                    stdout, stderr, exit_code = manager.execute_command(
                        "docker ps --format '{{.Names}}\t{{.Status}}'"
                    )

                    if exit_code == 0:
                        containers = []
                        for line in stdout.strip().split("\n"):
                            if line:
                                name, status = line.split("\t", 1)
                                containers.append({"name": name, "status": status})

                        result["status"] = "healthy"
                        result["containers"] = containers
                        result["total"] = len(containers)
                        result["error"] = None
                        logger.info(f"✓ Found {len(containers)} running containers")
                    else:
                        result["status"] = "unhealthy"
                        result["error"] = stderr

            except ImportError:
                logger.warning("ssh_manager not available, skipping Docker check")
            except Exception as e:
                result["status"] = "unhealthy"
                result["error"] = str(e)
                logger.error(f"Docker check failed: {e}")

        return result

    def run_all_checks(self) -> Dict:
        """
        Run all health checks.

        Returns:
            Complete health check report
        """
        logger.info("=" * 60)
        logger.info("Starting SaaS Node Health Check")
        logger.info("=" * 60)

        # Check HTTP endpoints
        for service in self.SERVICES:
            result = self.check_http_endpoint(service)
            self.results.append(result)

        # Check Docker containers
        docker_result = self.check_docker_containers()
        self.results.append(docker_result)

        # Generate summary
        total_services = len(self.SERVICES)
        healthy_count = sum(1 for r in self.results if r["status"] == "healthy")
        critical_unhealthy = [
            r
            for r in self.results
            if r.get("critical", False) and r["status"] == "unhealthy"
        ]

        overall_status = "healthy"
        if critical_unhealthy:
            overall_status = "critical"
        elif healthy_count < total_services:
            overall_status = "degraded"

        report = {
            "timestamp": datetime.now().isoformat(),
            "host": self.host,
            "overall_status": overall_status,
            "summary": {
                "total_services": total_services,
                "healthy": healthy_count,
                "unhealthy": total_services - healthy_count,
                "critical_issues": len(critical_unhealthy),
            },
            "services": self.results,
            "critical_issues": critical_unhealthy,
        }

        logger.info("=" * 60)
        logger.info(f"Health Check Complete: {overall_status.upper()}")
        logger.info(f"Healthy: {healthy_count}/{total_services}")
        logger.info("=" * 60)

        return report


def print_report(report: Dict, format: str = "text") -> None:
    """
    Print health check report.

    Args:
        report: Health check report dict
        format: Output format ('text' or 'json')
    """
    if format == "json":
        print(json.dumps(report, indent=2))
        return

    # Text format
    print("\n" + "=" * 60)
    print(f"SaaS Node Health Report - {report['timestamp']}")
    print("=" * 60)
    print(f"Host: {report['host']}")
    print(f"Overall Status: {report['overall_status'].upper()}")
    print(
        f"Healthy Services: {report['summary']['healthy']}/{report['summary']['total_services']}"
    )

    if report["summary"]["critical_issues"] > 0:
        print(f"\n⚠️  CRITICAL ISSUES: {report['summary']['critical_issues']}")
        for issue in report["critical_issues"]:
            print(f"  ✗ {issue['name']}: {issue['error']}")

    print("\nService Details:")
    print("-" * 60)
    for service in report["services"]:
        status_icon = {
            "healthy": "✓",
            "degraded": "⚠",
            "unhealthy": "✗",
            "skipped": "-",
        }.get(service["status"], "?")

        print(
            f"{status_icon} {service['name']:<25} {service['status'].upper():<10}",
            end="",
        )
        if service.get("response_time"):
            print(f" ({service['response_time']:.2f}s)", end="")
        if service.get("error"):
            print(f" - {service['error']}", end="")
        print()

    print("=" * 60 + "\n")


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Health Check for SaaS Node Infrastructure"
    )
    parser.add_argument(
        "--host",
        default=os.getenv("SAAS_NODE_HOST", "192.168.31.88"),
        help="Host IP address (default: from SAAS_NODE_HOST env var)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=5,
        help="HTTP request timeout in seconds (default: 5)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument("--output", "-o", type=Path, help="Save report to file")
    parser.add_argument(
        "--alert-on-critical",
        action="store_true",
        help="Exit with error code if critical services are unhealthy",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    try:
        # Run health checks
        checker = ServiceHealthChecker(host=args.host, timeout=args.timeout)
        report = checker.run_all_checks()

        # Print report
        print_report(report, format=args.format)

        # Save to file if requested
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with open(args.output, "w") as f:
                if args.format == "json":
                    json.dump(report, f, indent=2)
                else:
                    # Redirect stdout to file for text format
                    import io
                    from contextlib import redirect_stdout

                    text_buffer = io.StringIO()
                    with redirect_stdout(text_buffer):
                        print_report(report, format="text")
                    f.write(text_buffer.getvalue())
            logger.info(f"Report saved to {args.output}")

        # Alert on critical issues
        if args.alert_on_critical and report["overall_status"] == "critical":
            logger.error("Critical issues detected!")
            sys.exit(1)

        logger.info("Health check completed successfully")

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
