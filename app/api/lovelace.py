"""Lovelace Dashboard API Endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
import yaml

from app.models.schemas import Response
from app.auth import verify_token
from app.services.lovelace_generator import lovelace_generator
from app.services.ha_client import ha_client
from app.services.file_manager import file_manager
from app.services.git_manager import git_manager

logger = logging.getLogger('ha_cursor_agent')
router = APIRouter()

# ==================== Request Models ====================

class GenerateDashboardRequest(BaseModel):
    """Request model for generating dashboard"""
    style: str = 'modern'  # modern, classic, minimal
    title: str = 'Home'
    include_views: Optional[List[str]] = None  # ['lights', 'climate', 'media']

class ApplyDashboardRequest(BaseModel):
    """Request model for applying dashboard"""
    dashboard_config: Dict[str, Any]
    create_backup: bool = True

# ==================== Endpoints ====================

@router.get("/analyze", response_model=Response, dependencies=[Depends(verify_token)])
async def analyze_entities():
    """
    Analyze entities and provide dashboard generation recommendations
    
    Returns:
        - Entity counts by domain and area
        - Recommended views
        - Grouping suggestions
    """
    try:
        logger.info("Analyzing entities for dashboard generation")
        
        # Get all entities from Home Assistant
        entities = await ha_client.get_states()
        
        if not entities or len(entities) == 0:
            return Response(
                success=False,
                message="No entities found in Home Assistant",
                data={}
            )
        
        # Analyze entities
        analysis = lovelace_generator.analyze_entities(entities)
        
        return Response(
            success=True,
            message=f"Analyzed {analysis['total_entities']} entities",
            data=analysis
        )
    
    except Exception as e:
        logger.error(f"Error analyzing entities: {e}")
        return Response(success=False, message=f"Failed to analyze entities: {str(e)}")


@router.post("/generate", response_model=Response, dependencies=[Depends(verify_token)])
async def generate_dashboard(request: GenerateDashboardRequest):
    """
    Generate complete Lovelace dashboard configuration
    
    Args:
        request: Dashboard generation parameters
        
    Returns:
        Generated dashboard configuration ready to apply
    """
    try:
        logger.info(f"Generating {request.style} dashboard: {request.title}")
        
        # Get all entities
        entities = await ha_client.get_states()
        
        if not entities or len(entities) == 0:
            return Response(
                success=False,
                message="No entities found to generate dashboard",
                data={}
            )
        
        # Generate dashboard
        dashboard_config = lovelace_generator.generate_dashboard(
            entities=entities,
            style=request.style
        )
        
        # Update title if provided
        if request.title:
            dashboard_config['title'] = request.title
        
        # Filter views if specified
        if request.include_views:
            dashboard_config['views'] = [
                view for view in dashboard_config['views']
                if view.get('path') in request.include_views or view.get('title') in request.include_views
            ]
        
        # Convert to YAML for preview
        dashboard_yaml = yaml.dump(dashboard_config, default_flow_style=False, allow_unicode=True)
        
        return Response(
            success=True,
            message=f"Dashboard generated with {len(dashboard_config['views'])} views",
            data={
                'config': dashboard_config,
                'yaml': dashboard_yaml,
                'views': [v['title'] for v in dashboard_config['views']],
                'total_views': len(dashboard_config['views'])
            }
        )
    
    except Exception as e:
        logger.error(f"Error generating dashboard: {e}")
        return Response(success=False, message=f"Failed to generate dashboard: {str(e)}")


@router.get("/preview", response_model=Response, dependencies=[Depends(verify_token)])
async def preview_current_dashboard():
    """
    Preview current Lovelace dashboard configuration
    
    Returns:
        Current dashboard configuration (if exists)
    """
    try:
        logger.info("Reading current dashboard configuration")
        
        # Try to read ui-lovelace.yaml
        lovelace_path = "ui-lovelace.yaml"
        
        try:
            content = file_manager.read_file(lovelace_path)
            config = yaml.safe_load(content)
            
            return Response(
                success=True,
                message="Current dashboard configuration",
                data={
                    'path': lovelace_path,
                    'config': config,
                    'yaml': content
                }
            )
        except FileNotFoundError:
            return Response(
                success=True,
                message="No custom dashboard configured (using default UI mode)",
                data={
                    'path': lovelace_path,
                    'exists': False,
                    'note': 'Home Assistant is in storage mode or using default dashboard'
                }
            )
    
    except Exception as e:
        logger.error(f"Error previewing dashboard: {e}")
        return Response(success=False, message=f"Failed to preview dashboard: {str(e)}")


@router.post("/apply", response_model=Response, dependencies=[Depends(verify_token)])
async def apply_dashboard(request: ApplyDashboardRequest):
    """
    Apply generated dashboard configuration to Home Assistant
    
    Args:
        request: Dashboard configuration to apply
        
    **⚠️ Warning:** This will overwrite existing ui-lovelace.yaml
    **💾 Backup:** Creates Git backup by default
    """
    try:
        logger.info("Applying dashboard configuration")
        
        # Create backup if requested
        if request.create_backup:
            logger.info("Creating backup before applying dashboard")
            commit_msg = git_manager.commit("Before applying generated dashboard")
            logger.info(f"Backup created: {commit_msg}")
        
        # Convert config to YAML
        dashboard_yaml = yaml.dump(
            request.dashboard_config,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False
        )
        
        # Write to ui-lovelace.yaml
        lovelace_path = "ui-lovelace.yaml"
        file_manager.write_file(lovelace_path, dashboard_yaml)
        
        logger.info(f"Dashboard applied to {lovelace_path}")
        
        # Commit changes
        if request.create_backup:
            git_manager.commit("Applied generated dashboard")
        
        return Response(
            success=True,
            message=f"Dashboard applied successfully to {lovelace_path}",
            data={
                'path': lovelace_path,
                'views': len(request.dashboard_config.get('views', [])),
                'backup_created': request.create_backup,
                'note': 'Refresh your Home Assistant UI to see changes. You may need to enable YAML mode in Lovelace settings.'
            }
        )
    
    except Exception as e:
        logger.error(f"Error applying dashboard: {e}")
        return Response(success=False, message=f"Failed to apply dashboard: {str(e)}")

