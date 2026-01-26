#!/usr/bin/env python3
"""
Payroll System Full Stack Deployment
Purpose: Automated deployment of complete payroll-system (Frontend + Backend + Database)
Author: Auto-generated for douglasdev.com
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PayrollSystemDeployer:
    """Orchestrates complete deployment of Payroll System stack."""

    def __init__(self, domain: str = "douglasdev.com"):
        """
        Initialize deployer.

        Args:
            domain: Base domain (e.g., douglasdev.com)
        """
        self.domain = domain
        self.host = os.getenv("SAAS_NODE_HOST", "192.168.31.88")
        self.repo_url = "https://github.com/DouglasLiao/payroll-system"

        # Component configurations
        self.components = {
            "backend": {
                "name": "payroll-backend",
                "subdomain": f"api-payroll.{domain}",
                "port": 8000,
                "description": "Django Backend API",
                "build_path": "./backend",
                "dockerfile": "Dockerfile",
                "env_vars": [
                    "DATABASE_URL",
                    "SECRET_KEY",
                    "ALLOWED_HOSTS",
                    "DEBUG=False",
                    "CORS_ALLOWED_ORIGINS",
                ],
            },
            "frontend": {
                "name": "payroll-frontend",
                "subdomain": f"payroll.{domain}",
                "port": 3000,
                "description": "React Frontend",
                "build_path": "./frontend",
                "dockerfile": "Dockerfile",
                "env_vars": ["REACT_APP_API_URL", "NODE_ENV=production"],
            },
            "database": {
                "name": "payroll-db",
                "description": "PostgreSQL Database",
                "image": "postgres:15",
                "port": 5432,
                "env_vars": [
                    "POSTGRES_DB=payroll",
                    "POSTGRES_USER=payroll_user",
                    "POSTGRES_PASSWORD",
                ],
            },
        }

    def generate_deployment_plan(self) -> str:
        """Generate complete deployment plan for all components."""

        plan = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║              PAYROLL SYSTEM - FULL STACK DEPLOYMENT PLAN                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

Repository: {self.repo_url}
Target Host: {self.host}
Base Domain: {self.domain}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPONENT 1: DATABASE (PostgreSQL)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. In Coolify (http://{self.host}:8000):
   - Go to Resources → Databases → New Database
   - Select PostgreSQL 15
   - Database name: payroll-db
   - Username: payroll_user
   - Password: [GENERATE SECURE PASSWORD]
   - Note the internal connection string
   
2. Database Configuration:
   Database: payroll
   User: payroll_user
   Internal Host: payroll-db (Coolify internal network)
   Port: 5432

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPONENT 2: BACKEND (Django API)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. In Coolify:
   - New Resource → Application
   - Repository: {self.repo_url}
   - Branch: main
   - Build Pack: Dockerfile
   - Base Directory: ./backend

2. Environment Variables:
   DATABASE_URL=postgresql://payroll_user:PASSWORD@payroll-db:5432/payroll
   SECRET_KEY=[GENERATE DJANGO SECRET KEY]
   DEBUG=False
   ALLOWED_HOSTS={self.components['backend']['subdomain']},{self.host}
   CORS_ALLOWED_ORIGINS=https://{self.components['frontend']['subdomain']}

3. Build Settings:
   - Port: {self.components['backend']['port']}
   - Health Check: /api/health/ (create endpoint)
   
4. Deploy and note the assigned port (e.g., 3005)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPONENT 3: FRONTEND (React)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. In Coolify:
   - New Resource → Application
   - Repository: {self.repo_url}
   - Branch: main
   - Build Pack: Dockerfile
   - Base Directory: ./frontend

2. Environment Variables:
   REACT_APP_API_URL=https://{self.components['backend']['subdomain']}
   NODE_ENV=production

3. Build Settings:
   - Port: {self.components['frontend']['port']} (or 80 if using Nginx)
   - Build Command: npm run build
   
4. Deploy and note the assigned port (e.g., 3006)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPONENT 4: NGINX PROXY MANAGER - BACKEND
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Open NPM Admin (http://{self.host}:81)

2. Create Proxy Host for Backend:
   
   Details Tab:
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Domain Names:        {self.components['backend']['subdomain']}
   Scheme:             http
   Forward Hostname:   {self.host}
   Forward Port:       [PORT FROM COOLIFY BACKEND]
   Cache Assets:       OFF
   Block Exploits:     ON
   Websockets:         OFF

   SSL Tab:
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   SSL Certificate:    Request a new SSL Certificate
   Force SSL:          ON
   HTTP/2 Support:     ON
   HSTS Enabled:       ON

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPONENT 5: NGINX PROXY MANAGER - FRONTEND
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Create Proxy Host for Frontend:
   
   Details Tab:
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Domain Names:        {self.components['frontend']['subdomain']}
   Scheme:             http
   Forward Hostname:   {self.host}
   Forward Port:       [PORT FROM COOLIFY FRONTEND]
   Cache Assets:       ON
   Block Exploits:     ON
   Websockets:         OFF

   SSL Tab:
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   SSL Certificate:    Request a new SSL Certificate
   Force SSL:          ON
   HTTP/2 Support:     ON
   HSTS Enabled:       ON

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TESTING & VALIDATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Test Backend API:
   curl -I https://{self.components['backend']['subdomain']}/api/
   
2. Test Frontend:
   curl -I https://{self.components['frontend']['subdomain']}
   
3. Check Database Connection:
   - SSH into backend container
   - Run: python manage.py dbshell
   
4. Run Migrations:
   - In Coolify backend logs/terminal
   - Run: python manage.py migrate
   
5. Create Superuser:
   - Run: python manage.py createsuperuser
   
6. Access Admin:
   https://{self.components['backend']['subdomain']}/admin/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DEPLOYMENT SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Component          | URL                                           | Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Database           | Internal only (payroll-db:5432)              | □ Pending
Backend API        | https://{self.components['backend']['subdomain']:<40} | □ Pending
Frontend           | https://{self.components['frontend']['subdomain']:<40} | □ Pending

╔══════════════════════════════════════════════════════════════════════════════╗
║ Follow steps in order for successful deployment!                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        return plan

    def generate_npm_configs(self) -> Dict[str, str]:
        """Generate NPM configurations for both frontend and backend."""

        configs = {}

        # Backend config
        configs[
            "backend"
        ] = f"""
# NPM Configuration - Backend API
# Domain: {self.components['backend']['subdomain']}

Domain Names: {self.components['backend']['subdomain']}
Scheme: http
Forward Hostname/IP: {self.host}
Forward Port: [COOLIFY_BACKEND_PORT]
Cache Assets: false
Block Common Exploits: true
Websockets Support: false

SSL Certificate: Let's Encrypt ({self.components['backend']['subdomain']})
Force SSL: true
HTTP/2 Support: true
HSTS Enabled: true

# Custom Nginx Config (Optional - for API optimization)
client_max_body_size 100M;
proxy_connect_timeout 600;
proxy_send_timeout 600;
proxy_read_timeout 600;
"""

        # Frontend config
        configs[
            "frontend"
        ] = f"""
# NPM Configuration - Frontend
# Domain: {self.components['frontend']['subdomain']}

Domain Names: {self.components['frontend']['subdomain']}
Scheme: http
Forward Hostname/IP: {self.host}
Forward Port: [COOLIFY_FRONTEND_PORT]
Cache Assets: true
Block Common Exploits: true
Websockets Support: false

SSL Certificate: Let's Encrypt ({self.components['frontend']['subdomain']})
Force SSL: true
HTTP/2 Support: true
HSTS Enabled: true

# Custom Nginx Config (for SPA routing)
location / {{
    proxy_pass http://{self.host}:[COOLIFY_FRONTEND_PORT];
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # SPA fallback
    try_files $uri $uri/ /index.html;
}}
"""

        return configs

    def generate_env_template(self) -> str:
        """Generate environment variables template."""

        template = f"""
# Payroll System - Environment Variables Template
# Generated for deployment to {self.domain}

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================
DATABASE_URL=postgresql://payroll_user:YOUR_PASSWORD@payroll-db:5432/payroll
POSTGRES_DB=payroll
POSTGRES_USER=payroll_user
POSTGRES_PASSWORD=YOUR_SECURE_PASSWORD

# ============================================================================
# BACKEND (Django) CONFIGURATION
# ============================================================================
SECRET_KEY=YOUR_DJANGO_SECRET_KEY
DEBUG=False
ALLOWED_HOSTS={self.components['backend']['subdomain']},{self.host}
CORS_ALLOWED_ORIGINS=https://{self.components['frontend']['subdomain']}

# ============================================================================
# FRONTEND (React) CONFIGURATION
# ============================================================================
REACT_APP_API_URL=https://{self.components['backend']['subdomain']}
NODE_ENV=production

# ============================================================================
# GENERATE SECURE VALUES
# ============================================================================

# Django Secret Key (Run in Python):
# python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# PostgreSQL Password (Run in bash):
# openssl rand -base64 32
"""
        return template

    def save_deployment_artifacts(self, output_dir: Path) -> None:
        """Save all deployment artifacts to files."""

        output_dir.mkdir(parents=True, exist_ok=True)

        # Deployment plan
        plan_file = output_dir / "payroll_deployment_plan.txt"
        with open(plan_file, "w") as f:
            f.write(self.generate_deployment_plan())
        logger.info(f"✓ Deployment plan: {plan_file}")

        # NPM configs
        configs = self.generate_npm_configs()
        for component, config in configs.items():
            config_file = output_dir / f"npm_config_{component}.txt"
            with open(config_file, "w") as f:
                f.write(config)
            logger.info(f"✓ NPM config ({component}): {config_file}")

        # Environment template
        env_file = output_dir / "payroll_env_template.txt"
        with open(env_file, "w") as f:
            f.write(self.generate_env_template())
        logger.info(f"✓ Environment template: {env_file}")

        print(f"\n{'='*80}")
        print(f"✓ All deployment artifacts saved to: {output_dir}")
        print(f"{'='*80}\n")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Payroll System Full Stack Deployment Orchestrator"
    )
    parser.add_argument(
        "--domain",
        default="douglasdev.com",
        help="Base domain (default: douglasdev.com)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("./deployments/payroll-system"),
        help="Output directory for deployment artifacts",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    try:
        print("\n" + "=" * 80)
        print("PAYROLL SYSTEM - FULL STACK DEPLOYMENT ORCHESTRATOR")
        print("=" * 80 + "\n")

        # Create deployer
        deployer = PayrollSystemDeployer(domain=args.domain)

        # Show deployment plan
        print(deployer.generate_deployment_plan())

        # Save all artifacts
        deployer.save_deployment_artifacts(args.output)

        print("\n" + "=" * 80)
        print("✓ Deployment orchestration completed!")
        print(f"\nNext steps:")
        print(f"1. Review: {args.output / 'payroll_deployment_plan.txt'}")
        print(f"2. Configure environment: {args.output / 'payroll_env_template.txt'}")
        print(f"3. Follow deployment plan step by step")
        print("=" * 80 + "\n")

        logger.info("Deployment orchestration completed successfully")

    except Exception as e:
        logger.error(f"Deployment orchestration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
