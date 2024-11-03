# server/api/repositories/base_repository.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Dict, Any

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """Abstract base class for all repositories"""
    
    @abstractmethod
    def get(self, id: str) -> Optional[T]:
        """Retrieve an entity by ID"""
        pass

    @abstractmethod
    def get_all(self) -> List[T]:
        """Retrieve all entities"""
        pass

    @abstractmethod
    def add(self, entity: T) -> T:
        """Add a new entity"""
        pass

    @abstractmethod
    def update(self, entity: T) -> T:
        """Update an existing entity"""
        pass

    @abstractmethod
    def delete(self, id: str) -> bool:
        """Delete an entity by ID"""
        pass

    @abstractmethod
    def save(self) -> None:
        """Save all changes to persistent storage"""
        pass