import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass
class ServiceConfig:
    """Configuration for microservices"""
    
    # OpenAI
    openai_api_key: str
    default_model: str = "gpt-4o"
    
    # Flask
    flask_env: str = "development"
    flask_debug: bool = True
    service_port: int = 5002
    
    # RAG System
    manual_db_path: str = "./v2/manuals.db"
    pdf_base_path: str = "./v2/manuals/"
    
    # Timeouts and limits
    llm_timeout: int = 60  # seconds
    max_retries: int = 3
    
    @classmethod
    def from_env(cls) -> 'ServiceConfig':
        """Load configuration from environment variables"""
        return cls(
            openai_api_key=os.getenv('OPENAI_API_KEY', ''),
            default_model=os.getenv('DEFAULT_MODEL', 'gpt-4o'),
            flask_env=os.getenv('FLASK_ENV', 'development'),
            flask_debug=os.getenv('FLASK_DEBUG', 'True').lower() == 'true',
            service_port=int(os.getenv('SERVICE_PORT', '5002')),
            manual_db_path=os.getenv('MANUAL_DB_PATH', './v2/manuals.db'),
            pdf_base_path=os.getenv('PDF_BASE_PATH', './v2/manuals/'),
            llm_timeout=int(os.getenv('LLM_TIMEOUT', '60')),
            max_retries=int(os.getenv('MAX_RETRIES', '3')),
        )
    
    def validate(self):
        """Validate configuration"""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")
        
        if self.service_port < 1024 or self.service_port > 65535:
            raise ValueError("SERVICE_PORT must be between 1024 and 65535")


# Global config instance
config = ServiceConfig.from_env()