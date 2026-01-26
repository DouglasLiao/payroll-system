#!/usr/bin/env python3
"""
Nginx Config Generator for SaaS Node
Purpose: Generate NPM proxy host configurations for applications
Author: Auto-generated
"""

import argparse
import json
import logging
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


class NginxConfigGenerator:
    """Generates Nginx Proxy Manager configurations."""

    def __init__(
        self,
        domain: str,
        forward_host: str,
        forward_port: int,
        enable_ssl: bool = True,
        enable_websockets: bool = False,
        custom_locations: Optional[Dict] = None,
    ):
        """
        Initialize config generator.

        Args:
            domain: Domain name
            forward_host: Forward hostname/IP
            forward_port: Forward port
            enable_ssl: Enable SSL (default: True)
            enable_websockets: Enable websockets support (default: False)
            custom_locations: Custom location blocks (optional)
        """
        self.domain = domain
        self.forward_host = forward_host
        self.forward_port = forward_port
        self.enable_ssl = enable_ssl
        self.enable_websockets = enable_websockets
        self.custom_locations = custom_locations or {}

    def generate_npm_json(self) -> Dict:
        """
        Generate NPM-compatible JSON configuration.

        Returns:
            Configuration dictionary
        """
        config = {
            "domain_names": [self.domain],
            "forward_scheme": "http",
            "forward_host": self.forward_host,
            "forward_port": self.forward_port,
            "certificate_id": 0,  # Will be set by NPM
            "ssl_forced": self.enable_ssl,
            "caching_enabled": False,
            "block_exploits": True,
            "advanced_config": "",
            "meta": {"letsencrypt_agree": True, "dns_challenge": False},
            "http2_support": True,
            "hsts_enabled": self.enable_ssl,
            "hsts_subdomains": False,
            "locations": [],
        }

        # Add websockets support if enabled
        if self.enable_websockets:
            config[
                "advanced_config"
            ] += """
# WebSocket Support
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
"""

        # Add custom locations
        for path, location_config in self.custom_locations.items():
            config["locations"].append(
                {
                    "path": path,
                    "forward_scheme": location_config.get("scheme", "http"),
                    "forward_host": location_config.get("host", self.forward_host),
                    "forward_port": location_config.get("port", self.forward_port),
                    "advanced_config": location_config.get("advanced_config", ""),
                }
            )

        return config

    def generate_nginx_conf(self) -> str:
        """
        Generate raw Nginx configuration as reference.

        Returns:
            Nginx configuration string
        """
        conf = f"""# Nginx Configuration for {self.domain}
# This is a REFERENCE configuration. Use NPM UI for actual deployment.

server {{
    listen 80;
    listen [::]:80;
    server_name {self.domain};
"""

        if self.enable_ssl:
            conf += f"""
    # Force HTTPS redirect
    return 301 https://$server_name$request_uri;
}}

server {{
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name {self.domain};
    
    # SSL Configuration (managed by NPM/Let's Encrypt)
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers off;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000" always;
"""

        conf += f"""
    # Block common exploits
    include /etc/nginx/snippets/block-exploits.conf;
    
    # Proxy headers
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Host $server_name;
"""

        if self.enable_websockets:
            conf += """
    # WebSocket support
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_http_version 1.1;
"""

        conf += f"""
    location / {{
        proxy_pass http://{self.forward_host}:{self.forward_port};
    }}
"""

        # Add custom locations
        for path, location_config in self.custom_locations.items():
            host = location_config.get("host", self.forward_host)
            port = location_config.get("port", self.forward_port)
            scheme = location_config.get("scheme", "http")
            conf += f"""
    location {path} {{
        proxy_pass {scheme}://{host}:{port};
        {location_config.get("advanced_config", "")}
    }}
"""

        conf += "}\n"
        return conf

    def generate_summary(self) -> str:
        """
        Generate human-readable configuration summary.

        Returns:
            Configuration summary string
        """
        summary = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    NGINX PROXY CONFIGURATION                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

Domain:           {self.domain}
Forward To:       {self.forward_host}:{self.forward_port}
SSL Enabled:      {'Yes' if self.enable_ssl else 'No'}
WebSockets:       {'Enabled' if self.enable_websockets else 'Disabled'}

┌──────────────────────────────────────────────────────────────────────────────┐
│ NPM UI CONFIGURATION                                                         │
└──────────────────────────────────────────────────────────────────────────────┘

1. Open NPM Admin UI
2. Create new Proxy Host with these settings:

   Details Tab:
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Domain Names:        {self.domain}
   Scheme:             http
   Forward Hostname:   {self.forward_host}
   Forward Port:       {self.forward_port}
   Cache Assets:       OFF
   Block Exploits:     ON
   Websockets:         {'ON' if self.enable_websockets else 'OFF'}

   SSL Tab:
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   SSL Certificate:    Request a new SSL Certificate
   Force SSL:          ON
   HTTP/2 Support:     ON
   HSTS Enabled:       ON
   HSTS Subdomains:    OFF

3. Save configuration

╔══════════════════════════════════════════════════════════════════════════════╗
║ Configuration ready for deployment in NPM!                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        return summary


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Nginx Config Generator for SaaS Node Infrastructure"
    )
    parser.add_argument(
        "--domain", required=True, help="Domain name (e.g., myapp.example.com)"
    )
    parser.add_argument(
        "--forward-host",
        default="192.168.31.88",
        help="Forward hostname/IP (default: 192.168.31.88)",
    )
    parser.add_argument(
        "--forward-port", type=int, required=True, help="Forward port (e.g., 3005)"
    )
    parser.add_argument("--no-ssl", action="store_true", help="Disable SSL/HTTPS")
    parser.add_argument(
        "--websockets", action="store_true", help="Enable WebSocket support"
    )
    parser.add_argument("--output", "-o", type=Path, help="Output file path (optional)")
    parser.add_argument(
        "--format",
        choices=["summary", "json", "nginx"],
        default="summary",
        help="Output format (default: summary)",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    try:
        # Create generator
        generator = NginxConfigGenerator(
            domain=args.domain,
            forward_host=args.forward_host,
            forward_port=args.forward_port,
            enable_ssl=not args.no_ssl,
            enable_websockets=args.websockets,
        )

        # Generate output based on format
        if args.format == "json":
            output = json.dumps(generator.generate_npm_json(), indent=2)
        elif args.format == "nginx":
            output = generator.generate_nginx_conf()
        else:  # summary
            output = generator.generate_summary()

        # Display output
        print(output)

        # Save to file if requested
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with open(args.output, "w") as f:
                f.write(output)
            logger.info(f"Configuration saved to {args.output}")

        logger.info("Configuration generation completed successfully")

    except Exception as e:
        logger.error(f"Configuration generation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
