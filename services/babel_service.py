"""
Babel Service - Microservice Architecture
This file provides backward compatibility by importing the new modular babel services.
"""

from .babel import BabelService, get_babel_service

# Export the service for backward compatibility
__all__ = ['BabelService', 'get_babel_service']