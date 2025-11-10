"""
Ingress Panel for HA Cursor Agent
Renders configuration panel using Jinja2 template
"""
from pathlib import Path
from jinja2 import Template


def generate_ingress_html(api_key: str, agent_version: str) -> str:
    """
    Generate HTML for Ingress Panel using Jinja2 template
    
    Args:
        api_key: Agent API key
        agent_version: Current agent version
        
    Returns:
        Rendered HTML string
    """
    # Full JSON config for user to copy
    json_config = f'''{{
  "mcpServers": {{
    "home-assistant": {{
      "command": "npx",
      "args": ["-y", "@coolver/home-assistant-mcp@latest"],
      "env": {{
        "HA_AGENT_URL": "http://homeassistant.local:8099",
        "HA_AGENT_KEY": "{api_key}"
      }}
    }}
  }}
}}'''
    
    # Masked key for display
    masked_key = f"{api_key[:12]}...{api_key[-12:]}" if len(api_key) > 24 else api_key
    
    # Load Jinja2 template
    template_path = Path(__file__).parent / 'templates' / 'ingress_panel.html'
    template_content = template_path.read_text(encoding='utf-8')
    template = Template(template_content)
    
    # Render template with context
    html = template.render(
        api_key=api_key,
        agent_version=agent_version,
        json_config=json_config,
        masked_key=masked_key
    )
    
    return html
