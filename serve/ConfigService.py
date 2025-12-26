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
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._config = DebateConfig()
        self.providers = {}
        self.role_provider = {
            "affirmative": 1,
            "negative": 2,
            "referee": 3
        }
        i = 1
        while True:
            provider = os.getenv(f"PROVIDER{i}")
            if not provider:
                break
            
            model = os.getenv(f"MODEL{i}")
            
            # Find api key with matching index suffix
            api_key = os.getenv(f"API_KEY{i}")
            if not api_key:
                suffix = f"_API_KEY{i}"
                for key, value in os.environ.items():
                    if key.endswith(suffix):
                        api_key = value
                        break
            
            self.providers[i] = {
                "provider": provider,
                "model": model,
                "api_key": api_key
            }
            print("find api key: "+str(i)+" "+api_key)
            i += 1
        
    
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

    def get_provider(self, provide_id: int) -> str:
        return self.providers[provide_id]

    def set_role_provider(self, role: str, provider_id: int) -> None:
        self.role_provider[role] = provider_id

    def get_role_provider(self, role: str) -> int:
        return self.role_provider.get(role)

    def list_providers(self) -> str:
        providers = []
        for provider in self.providers:
            #return provide name and model only in json format
            providers.append({"provider": provider["provider"], "model": provider["model"]})
        return json.dumps(providers)
    