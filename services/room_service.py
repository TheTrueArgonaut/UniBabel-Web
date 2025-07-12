"""
Room Service - Microservice Architecture
This file provides backward compatibility by importing the new modular room services.
"""

from .room import RoomService, get_room_service

# Export the service for backward compatibility
__all__ = ['RoomService', 'get_room_service']