#!/usr/bin/env python3
"""
Simple Configuration Manager for Pizza Counter
"""

import yaml
import json
import logging
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class Config:
    """Simple configuration manager with defaults."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load config from file or return defaults."""
        # Try to load from file
        paths = [config_path, 'config.yaml', '/app/config.yaml'] if config_path else ['config.yaml', '/app/config.yaml']
        
        for path in paths:
            if path and Path(path).exists():
                try:
                    with open(path, 'r') as f:
                        config = yaml.safe_load(f) or {}
                    logger.info(f"Loaded config from: {path}")
                    return self._merge_defaults(config)
                except Exception as e:
                    logger.warning(f"Failed to load {path}: {e}")
        
        logger.info("Using default configuration")
        return self._get_defaults()
    
    def _get_defaults(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'MODEL_CONFIG': {
                'confidence_threshold': 0.5
            },
            'TRACKING_CONFIG': {
                'max_disappeared': 30,
                'max_distance': 50
            },
            'COUNTING_CONFIG': {
                'min_track_length': 5
            }
        }
    
    def _merge_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge loaded config with defaults."""
        defaults = self._get_defaults()
        
        for section, values in defaults.items():
            if section not in config:
                config[section] = values
            else:
                for key, default_value in values.items():
                    if key not in config[section]:
                        config[section][key] = default_value
        
        return config
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(section, {}).get(key, default)
    
    def load_zones_from_config(self, config_path: str = 'zones_config.json') -> Optional[Tuple[int, int, int, int]]:
        """
        Load counting zones from configuration file.
        
        Args:
            config_path: Path to zones configuration file
            
        Returns:
            Tuple of (x1, y1, x2, y2) coordinates or None if not found
        """
        # Try multiple locations for the config file
        config_paths = [
            config_path,
            f'/app/host_config/{config_path}',
            f'/app/{config_path}'
        ]
        
        for path in config_paths:
            try:
                with open(path, 'r') as f:
                    config = json.load(f)
                
                zones = config.get('zones', [])
                if zones:
                    # Handle both list and dict formats
                    if isinstance(zones, list) and len(zones) > 0:
                        # Use first zone from list
                        first_zone = zones[0]
                        if first_zone.get('type') == 'rectangle':
                            coords = first_zone['coordinates']
                            logger.info(f"Loaded zone: {first_zone.get('name', 'zone_1')} from {path}")
                            return tuple(coords)
                    elif isinstance(zones, dict):
                        # Use first zone from dict
                        first_zone = list(zones.values())[0]
                        if first_zone['type'] == 'rectangle':
                            coords = first_zone['coordinates']
                            logger.info(f"Loaded zone: {first_zone['name']} from {path}")
                            return tuple(coords)
                
            except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
                if path == config_paths[-1]:  # Only log warning for the last attempt
                    logger.warning(f"Could not load zones config from any location: {e}")
                continue
        
        logger.info("No zone config found, will use default zone")
        return None

# Global instance
_config = None

def get_config(config_path: Optional[str] = None) -> Config:
    """Get global config instance."""
    global _config
    if _config is None:
        _config = Config(config_path)
    return _config
