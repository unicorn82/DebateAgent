import os
from typing import Optional
from dataclasses import dataclass

@dataclass
class DebateConfig:
    """Configuration class to store debate application parameters"""
    provider: str = os.getenv("PROVIDER")
    model: str = os.getenv("MODEL")
    temperature: float = 0.7
    num_rounds: int = 3
    referee_api_key: str = os.getenv("REFEREE_API_KEY")
    api_key: Optional[str] = None
    
class ConfigService:
    """Service to manage debate application configuration"""
    
    def __init__(self):
        self._config = DebateConfig()
    
    def update_config(self, 
                     
                     temperature: Optional[float] = None,
                     num_rounds: Optional[int] = None,
                     api_key: Optional[str] = None) -> None:
        """Update configuration parameters"""
        
        if temperature is not None:
            self._config.temperature = temperature
        if num_rounds is not None:
            self._config.num_rounds = num_rounds
    
    
    def get_config(self) -> DebateConfig:
        """Get current configuration"""
        return self._config
    
    
    
    def get_temperature(self) -> float:
        return self._config.temperature
    
    def get_num_rounds(self) -> int:
        return self._config.num_rounds
    
    def get_referee_api_key(self) -> str:
        return self._config.referee_api_key
    
    def get_api_key(self) -> str:
        return self._config.api_key
    
   
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values"""
        self._config = DebateConfig()