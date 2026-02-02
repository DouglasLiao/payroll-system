from jinja2 import Template, Environment, BaseLoader
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class TemplateEngine:
    """Render email templates using Jinja2"""

    def __init__(self):
        self.env = Environment(loader=BaseLoader())

    def render_string(self, template_string: str, context: Dict[str, Any]) -> str:
        """Render a template string with context"""
        try:
            template = self.env.from_string(template_string)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Template rendering error: {e}")
            raise ValueError(f"Failed to render template: {e}")

    def render_file(self, template_path: str, context: Dict[str, Any]) -> str:
        """Render a template file with context"""
        try:
            with open(template_path, "r") as f:
                template_string = f.read()
            return self.render_string(template_string, context)
        except Exception as e:
            logger.error(f"Template file rendering error: {e}")
            raise ValueError(f"Failed to render template file: {e}")
