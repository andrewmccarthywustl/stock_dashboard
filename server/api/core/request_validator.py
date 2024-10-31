# server/api/core/request_validator.py
from functools import wraps
from flask import request
from typing import Dict, Any, Optional
import logging
from .exceptions import ValidationError

logger = logging.getLogger(__name__)

class RequestValidator:
    """Validate request data against predefined schemas"""
    
    def __init__(self):
        self.schemas: Dict[str, Dict] = {}
        self._register_default_schemas()

    def _register_default_schemas(self) -> None:
        """Register default validation schemas"""
        
        # Schema for trade requests
        self.register_schema('trade', {
            'type': 'object',
            'required': ['symbol', 'quantity', 'price', 'trade_type'],
            'properties': {
                'symbol': {
                    'type': 'string',
                    'pattern': '^[A-Z]+$',
                    'minLength': 1,
                    'maxLength': 5
                },
                'quantity': {
                    'type': 'number',
                    'minimum': 0,
                    'exclusiveMinimum': True
                },
                'price': {
                    'type': 'number',
                    'minimum': 0,
                    'exclusiveMinimum': True
                },
                'trade_type': {
                    'type': 'string',
                    'enum': ['buy', 'sell', 'short', 'cover']
                },
                'date': {
                    'type': 'string',
                    'format': 'date-time'
                }
            },
            'additionalProperties': False
        })

        # Schema for portfolio filters
        self.register_schema('portfolio_filter', {
            'type': 'object',
            'properties': {
                'symbol': {
                    'type': 'string',
                    'pattern': '^[A-Z]+$'
                },
                'position_type': {
                    'type': 'string',
                    'enum': ['long', 'short']
                },
                'sector': {
                    'type': 'string'
                },
                'min_value': {
                    'type': 'number',
                    'minimum': 0
                },
                'max_value': {
                    'type': 'number',
                    'minimum': 0
                }
            },
            'additionalProperties': False
        })

        # Schema for transaction filters
        self.register_schema('transaction_filter', {
            'type': 'object',
            'properties': {
                'symbol': {
                    'type': 'string',
                    'pattern': '^[A-Z]+$'
                },
                'transaction_type': {
                    'type': 'string',
                    'enum': ['buy', 'sell', 'short', 'cover']
                },
                'start_date': {
                    'type': 'string',
                    'format': 'date-time'
                },
                'end_date': {
                    'type': 'string',
                    'format': 'date-time'
                },
                'min_amount': {
                    'type': 'number',
                    'minimum': 0
                },
                'max_amount': {
                    'type': 'number',
                    'minimum': 0
                }
            },
            'additionalProperties': False
        })

    def validate_data(self, data: Dict, schema: Dict) -> None:
        """
        Custom validation implementation without jsonschema dependency
        """
        try:
            self._validate_type(data, schema)
            self._validate_required(data, schema)
            self._validate_properties(data, schema)
            self._validate_additional_properties(data, schema)
        except Exception as e:
            raise ValidationError(str(e))

    def _validate_type(self, data: Any, schema: Dict) -> None:
        """Validate type of data"""
        expected_type = schema.get('type')
        if expected_type == 'object' and not isinstance(data, dict):
            raise ValidationError("Data must be an object")
        elif expected_type == 'array' and not isinstance(data, list):
            raise ValidationError("Data must be an array")
        elif expected_type == 'string' and not isinstance(data, str):
            raise ValidationError("Data must be a string")
        elif expected_type == 'number' and not isinstance(data, (int, float)):
            raise ValidationError("Data must be a number")

    def _validate_required(self, data: Dict, schema: Dict) -> None:
        """Validate required fields"""
        required_fields = schema.get('required', [])
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")

    def _validate_properties(self, data: Dict, schema: Dict) -> None:
        """Validate properties of data"""
        properties = schema.get('properties', {})
        for field, value in data.items():
            if field in properties:
                field_schema = properties[field]
                self._validate_field(value, field_schema, field)

    def _validate_field(self, value: Any, schema: Dict, field_name: str) -> None:
        """Validate individual field"""
        # Type validation
        if 'type' in schema:
            if schema['type'] == 'string':
                if not isinstance(value, str):
                    raise ValidationError(f"Field {field_name} must be a string")
                self._validate_string_constraints(value, schema, field_name)
            elif schema['type'] == 'number':
                if not isinstance(value, (int, float)):
                    raise ValidationError(f"Field {field_name} must be a number")
                self._validate_number_constraints(value, schema, field_name)

        # Enum validation
        if 'enum' in schema and value not in schema['enum']:
            raise ValidationError(
                f"Field {field_name} must be one of: {schema['enum']}"
            )

    def _validate_string_constraints(
        self,
        value: str,
        schema: Dict,
        field_name: str
    ) -> None:
        """Validate string constraints"""
        if 'minLength' in schema and len(value) < schema['minLength']:
            raise ValidationError(
                f"Field {field_name} must be at least {schema['minLength']} characters"
            )
        if 'maxLength' in schema and len(value) > schema['maxLength']:
            raise ValidationError(
                f"Field {field_name} must be at most {schema['maxLength']} characters"
            )
        if 'pattern' in schema and not self._matches_pattern(value, schema['pattern']):
            raise ValidationError(
                f"Field {field_name} must match pattern: {schema['pattern']}"
            )

    def _validate_number_constraints(
        self,
        value: float,
        schema: Dict,
        field_name: str
    ) -> None:
        """Validate number constraints"""
        if 'minimum' in schema:
            if schema.get('exclusiveMinimum', False):
                if value <= schema['minimum']:
                    raise ValidationError(
                        f"Field {field_name} must be greater than {schema['minimum']}"
                    )
            elif value < schema['minimum']:
                raise ValidationError(
                    f"Field {field_name} must be greater than or equal to {schema['minimum']}"
                )

        if 'maximum' in schema:
            if schema.get('exclusiveMaximum', False):
                if value >= schema['maximum']:
                    raise ValidationError(
                        f"Field {field_name} must be less than {schema['maximum']}"
                    )
            elif value > schema['maximum']:
                raise ValidationError(
                    f"Field {field_name} must be less than or equal to {schema['maximum']}"
                )

    def _matches_pattern(self, value: str, pattern: str) -> bool:
        """
        Validate string against pattern
        For now, only implements basic pattern matching
        """
        if pattern == '^[A-Z]+$':
            return value.isalpha() and value.isupper()
        return True

    def _validate_additional_properties(self, data: Dict, schema: Dict) -> None:
        """Validate no additional properties if not allowed"""
        if schema.get('additionalProperties') is False:
            allowed_properties = set(schema.get('properties', {}).keys())
            actual_properties = set(data.keys())
            extra_properties = actual_properties - allowed_properties
            if extra_properties:
                raise ValidationError(
                    f"Additional properties not allowed: {extra_properties}"
                )

    def register_schema(self, name: str, schema: Dict) -> None:
        """Register a new validation schema"""
        if name in self.schemas:
            logger.warning(f"Overwriting existing schema: {name}")
        self.schemas[name] = schema
        logger.info(f"Registered schema: {name}")

    def validate_request(
        self,
        schema_name: str,
        data: Optional[Dict] = None
    ) -> None:
        """Validate request data against named schema"""
        if schema_name not in self.schemas:
            raise ValidationError(f"Schema not found: {schema_name}")

        try:
            data = data or request.get_json()
            self.validate_data(data, self.schemas[schema_name])
        except Exception as e:
            logger.warning(f"Validation failed: {str(e)}")
            raise ValidationError(str(e))

    def __call__(self, schema_name: str):
        """Decorator for route validation"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                self.validate_request(schema_name)
                return f(*args, **kwargs)
            return decorated_function
        return decorator

# Create singleton instance
request_validator = RequestValidator()