# server/api/repositories/json_repository.py
import json
import os
from typing import Dict, List, Optional, TypeVar, Generic, Any
from datetime import datetime
import logging
from pathlib import Path
from .base_repository import BaseRepository

T = TypeVar('T')

class JSONRepository(BaseRepository[T], Generic[T]):
    """Base JSON file repository implementation"""

    def __init__(self, file_path: str, entity_class: type):
        """Initialize repository
        
        Args:
            file_path: Path to JSON storage file
            entity_class: Class type of entities to store
        """
        self.file_path = file_path
        self.entity_class = entity_class
        self.entities: Dict[str, T] = {}
        self.logger = logging.getLogger(__name__)
        self._ensure_data_directory()
        self._load_data()

    def _ensure_data_directory(self) -> None:
        """Create data directory if it doesn't exist"""
        try:
            Path(os.path.dirname(self.file_path)).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise RuntimeError(f"Error creating data directory: {str(e)}")

    def _load_data(self) -> None:
        """Load data from JSON file, creating empty file if none exists"""
        if not os.path.exists(self.file_path):
            self.save()
            return

        try:
            with open(self.file_path, 'r') as file:
                data = json.load(file)
                self.entities = {
                    str(k): self.entity_class.from_dict(v)
                    for k, v in data.items()
                }
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            self.logger.error(f"Error loading JSON data: {str(e)}")
            # Reset to empty state if file is corrupted
            self.entities = {}
            self.save()
        except Exception as e:
            raise RuntimeError(f"Error loading JSON data: {str(e)}")

    def save_initial_data(self, initial_data: dict) -> None:
        """Save initial data structure to JSON file
        
        Args:
            initial_data: Dictionary containing initial data structure
        """
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, 'w') as file:
                json.dump(initial_data, file, indent=4)
            self._load_data()  # Reload data after saving
        except Exception as e:
            raise RuntimeError(f"Error saving initial data: {str(e)}")

    def get(self, id: str) -> Optional[T]:
        """Retrieve an entity by ID
        
        Args:
            id: Entity identifier
            
        Returns:
            Entity if found, None otherwise
        """
        return self.entities.get(str(id))

    def get_all(self) -> List[T]:
        """Retrieve all entities
        
        Returns:
            List of all entities
        """
        return list(self.entities.values())

    def add(self, entity: T) -> T:
        """Add a new entity
        
        Args:
            entity: Entity to add
            
        Returns:
            Added entity
            
        Raises:
            ValueError: If entity lacks ID or ID is empty
        """
        if not hasattr(entity, 'id'):
            raise ValueError("Entity must have an 'id' attribute (either as property or attribute)")
        
        entity_id = str(getattr(entity, 'id'))
        if not entity_id:
            raise ValueError("Entity ID cannot be empty")
            
        self.entities[entity_id] = entity
        self.save()
        return entity

    def update(self, entity: T) -> T:
        """Update an existing entity
        
        Args:
            entity: Entity to update
            
        Returns:
            Updated entity
            
        Raises:
            ValueError: If entity not found or lacks proper ID
        """
        if not hasattr(entity, 'id'):
            raise ValueError("Entity must have an 'id' attribute")
            
        entity_id = str(getattr(entity, 'id'))
        if not entity_id:
            raise ValueError("Entity ID cannot be empty")
            
        if entity_id not in self.entities:
            raise ValueError(f"Entity with ID {entity_id} not found")
            
        self.entities[entity_id] = entity
        self.save()
        return entity

    def delete(self, id: str) -> bool:
        """Delete an entity by ID
        
        Args:
            id: Entity identifier
            
        Returns:
            True if entity was deleted, False if not found
        """
        if str(id) in self.entities:
            del self.entities[str(id)]
            self.save()
            return True
        return False

    def save(self) -> None:
        """Save all changes to JSON file
        
        Raises:
            RuntimeError: If save operation fails
        """
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, 'w') as file:
                json.dump(
                    {k: v.to_dict() for k, v in self.entities.items()},
                    file,
                    indent=4
                )
        except Exception as e:
            raise RuntimeError(f"Error saving JSON data: {str(e)}")

    def clear(self) -> None:
        """Clear all entities"""
        self.entities = {}
        self.save()

    def count(self) -> int:
        """Get total number of entities
        
        Returns:
            Number of entities in repository
        """
        return len(self.entities)

    def exists(self, id: str) -> bool:
        """Check if entity exists
        
        Args:
            id: Entity identifier
            
        Returns:
            True if entity exists, False otherwise
        """
        return str(id) in self.entities

    def bulk_add(self, entities: List[T]) -> List[T]:
        """Add multiple entities at once
        
        Args:
            entities: List of entities to add
            
        Returns:
            List of added entities
            
        Raises:
            ValueError: If any entity lacks proper ID
        """
        for entity in entities:
            self.add(entity)
        return entities

    def bulk_delete(self, ids: List[str]) -> int:
        """Delete multiple entities at once
        
        Args:
            ids: List of entity identifiers
            
        Returns:
            Number of entities deleted
        """
        count = 0
        for id in ids:
            if self.delete(id):
                count += 1
        return count

    def find_by_field(self, field: str, value: Any) -> List[T]:
        """Find entities by field value
        
        Args:
            field: Field name to search
            value: Value to match
            
        Returns:
            List of matching entities
        """
        return [
            entity for entity in self.entities.values()
            if hasattr(entity, field) and getattr(entity, field) == value
        ]

    def get_modified_since(self, timestamp: datetime) -> List[T]:
        """Get entities modified since given timestamp
        
        Args:
            timestamp: DateTime to compare against
            
        Returns:
            List of entities modified since timestamp
        """
        return [
            entity for entity in self.entities.values()
            if hasattr(entity, 'last_updated') and entity.last_updated > timestamp
        ]

    def backup(self, backup_path: Optional[str] = None) -> str:
        """Create backup of repository data
        
        Args:
            backup_path: Optional path for backup file
            
        Returns:
            Path to backup file
            
        Raises:
            RuntimeError: If backup operation fails
        """
        if not backup_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"{self.file_path}.{timestamp}.bak"

        try:
            with open(self.file_path, 'r') as source:
                with open(backup_path, 'w') as target:
                    json.dump(json.load(source), target, indent=4)
            return backup_path
        except Exception as e:
            raise RuntimeError(f"Error creating backup: {str(e)}")

    def restore(self, backup_path: str) -> None:
        """Restore repository data from backup
        
        Args:
            backup_path: Path to backup file
            
        Raises:
            RuntimeError: If restore operation fails
        """
        try:
            with open(backup_path, 'r') as file:
                data = json.load(file)
            with open(self.file_path, 'w') as file:
                json.dump(data, file, indent=4)
            self._load_data()
        except Exception as e:
            raise RuntimeError(f"Error restoring from backup: {str(e)}")