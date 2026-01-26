#!/usr/bin/env python3
"""
Deploy App Orchestrator for SaaS Node
Purpose: Automate the complete deployment workflow for new applications
Author: Auto-generated
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DeploymentOrchestrator:
    """Orchestrates the deployment workflow for new applications."""

    def __init__(self, app_name: str, repo_url: str, internal_port: int, domain: str):
        """
        Initialize deployment orchestrator.

        Args:
            app_name: Application name
            repo_url: GitHub repository URL
            internal_port: Internal port assigned by Coolify
            domain: Domain name (e.g., myapp.example.com)
        """
        self.app_name = app_name
        self.repo_url = repo_url
        self.internal_port = internal_port
        self.domain = domain
        self.host = os.getenv("SAAS_NODE_HOST", "192.168.31.88")

    def generate_deployment_plan(self) -> str:
        """
        Generate a detailed deployment plan.

        Returns:
            Formatted deployment plan as string
        """
        plan = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         DEPLOYMENT PLAN                                      ║
╚══════════════════════════════════════════════════════════════════════════════╝

Application: {self.app_name}
Repository: {self.repo_url}
Domain: {self.domain}
Internal Port: {self.internal_port}
Host: {self.host}

┌──────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: COOLIFY CONFIGURATION                                                │
└──────────────────────────────────────────────────────────────────────────────┘

1. Access Coolify at http://{self.host}:8000
2. Create new application:
   - Connect GitHub repository: {self.repo_url}
   - Application name: {self.app_name}
   - Set build/start commands as needed
3. Note the assigned internal port: {self.internal_port}
4. Deploy the application

┌──────────────────────────────────────────────────────────────────────────────┐
│ STEP 2: NGINX PROXY MANAGER CONFIGURATION                                    │
└──────────────────────────────────────────────────────────────────────────────┘

1. Access NPM Admin at http://{self.host}:81
2. Create new Proxy Host:
   
   Domain Names:
   - {self.domain}
   
   Forward Hostname / IP:
   - {self.host}
   
   Forward Port:
   - {self.internal_port}
   
   Cache Assets: OFF
   Block Common Exploits: ON
   Websockets Support: ON (if needed)

3. SSL Configuration:
   - Request a new SSL Certificate (Let's Encrypt)
   - Force SSL: ON
   - HTTP/2 Support: ON
   - HSTS Enabled: ON

┌──────────────────────────────────────────────────────────────────────────────┐
│ STEP 3: CLOUDFLARE VERIFICATION                                              │
└──────────────────────────────────────────────────────────────────────────────┘

If using wildcard tunnel (*.example.com -> {self.host}:80):
- No additional configuration needed in Cloudflare
- NPM will handle the routing locally

Otherwise:
- Add DNS record in Cloudflare pointing to your tunnel

┌──────────────────────────────────────────────────────────────────────────────┐
│ STEP 4: TESTING & VALIDATION                                                 │
└──────────────────────────────────────────────────────────────────────────────┘

1. Test local access:
   curl -I http://{self.host}:{self.internal_port}

2. Test proxy access:
   curl -I http://{self.domain}

3. Test SSL:
   curl -I https://{self.domain}

4. Check SSL certificate:
   openssl s_client -connect {self.domain}:443 -servername {self.domain}

┌──────────────────────────────────────────────────────────────────────────────┐
│ QUICK REFERENCE                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

Coolify URL:      http://{self.host}:8000
NPM Admin URL:    http://{self.host}:81
Application URL:  https://{self.domain}
Internal URL:     http://{self.host}:{self.internal_port}

╔══════════════════════════════════════════════════════════════════════════════╗
║ Ready to deploy? Follow the steps above in order.                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        return plan

    def generate_nginx_config(self) -> str:
        """
        Generate NPM proxy host configuration snippet.

        Returns:
            Configuration snippet
        """
        config = f"""
# Nginx Proxy Manager - Proxy Host Configuration
# Application: {self.app_name}

Domain Names: {self.domain}
Scheme: http
Forward Hostname/IP: {self.host}
Forward Port: {self.internal_port}
Cache Assets: false
Block Common Exploits: true
Websockets Support: true

# SSL Configuration
SSL Certificate: Let's Encrypt ({self.domain})
Force SSL: true
HTTP/2 Support: true
HSTS Enabled: true
HSTS Subdomains: false

# Advanced Configuration (Optional)
# Add custom nginx directives if needed:
# proxy_set_header X-Real-IP $remote_addr;
# proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
# proxy_set_header X-Forwarded-Proto $scheme;
"""
        return config

    def save_deployment_artifacts(self, output_dir: Path) -> None:
        """
        Save deployment plan and configuration to files.

        Args:
            output_dir: Output directory path
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save deployment plan
        plan_file = output_dir / f"{self.app_name}_deployment_plan.txt"
        with open(plan_file, "w") as f:
            f.write(self.generate_deployment_plan())
        logger.info(f"Deployment plan saved to {plan_file}")

        # Save nginx config
        config_file = output_dir / f"{self.app_name}_nginx_config.txt"
        with open(config_file, "w") as f:
            f.write(self.generate_nginx_config())
        logger.info(f"Nginx config saved to {config_file}")

        print(f"\n✓ Deployment artifacts saved to {output_dir}")
        print(f"  - {plan_file.name}")
        print(f"  - {config_file.name}\n")


def interactive_mode() -> Dict[str, any]:
    """
    Run interactive mode to collect deployment information.

    Returns:
        Dictionary with deployment parameters
    """
    print("\n" + "=" * 80)
    print("SaaS Node - New Application Deployment")
    print("=" * 80 + "\n")

    app_name = input("Application name: ").strip()
    if not app_name:
        raise ValueError("Application name is required")

    repo_url = input("GitHub repository URL: ").strip()
    if not repo_url:
        raise ValueError("Repository URL is required")

    internal_port = input("Internal port (assigned by Coolify): ").strip()
    if not internal_port or not internal_port.isdigit():
        raise ValueError("Valid port number is required")

    domain = input("Domain name (e.g., myapp.example.com): ").strip()
    if not domain:
        raise ValueError("Domain name is required")

    return {
        "app_name": app_name,
        "repo_url": repo_url,
        "internal_port": int(internal_port),
        "domain": domain,
    }


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Deploy App Orchestrator for SaaS Node Infrastructure"
    )
    parser.add_argument("--app-name", help="Application name")
    parser.add_argument("--repo", help="GitHub repository URL")
    parser.add_argument("--port", type=int, help="Internal port assigned by Coolify")
    parser.add_argument("--domain", help="Domain name (e.g., myapp.example.com)")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("./deployments"),
        help="Output directory for deployment artifacts (default: ./deployments)",
    )
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Run in interactive mode"
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    try:
        # Get deployment parameters
        if args.interactive or not all(
            [args.app_name, args.repo, args.port, args.domain]
        ):
            if not args.interactive:
                logger.info("Missing parameters, switching to interactive mode...")
            params = interactive_mode()
        else:
            params = {
                "app_name": args.app_name,
                "repo_url": args.repo,
                "internal_port": args.port,
                "domain": args.domain,
            }

        # Create orchestrator
        orchestrator = DeploymentOrchestrator(
            app_name=params["app_name"],
            repo_url=params["repo_url"],
            internal_port=params["internal_port"],
            domain=params["domain"],
        )

        # Display deployment plan
        print(orchestrator.generate_deployment_plan())

        # Save artifacts
        orchestrator.save_deployment_artifacts(args.output)

        logger.info("Deployment orchestration completed successfully")
        print("✓ Deployment plan ready!")
        print(
            f"\nNext: Follow the steps in {args.output / params['app_name']}_deployment_plan.txt"
        )

    except KeyboardInterrupt:
        print("\n\nDeployment cancelled by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Deployment orchestration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
