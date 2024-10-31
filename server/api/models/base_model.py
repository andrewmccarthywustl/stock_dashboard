# api/models/base_model.py
from abc import ABC, abstractmethod

class BaseModel(ABC):
    """Abstract base class for all models"""
    
    @abstractmethod
    def to_dict(self) -> dict:
        """Convert model to dictionary representation"""
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict) -> 'BaseModel':
        """Create model instance from dictionary"""
        pass