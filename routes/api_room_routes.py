"""
API Room Routes - SRIMI Microservice
Single Responsibility: Room management only
"""

from flask import Flask, request, jsonify
from flask_login import login_required, current_user

def register_api_room_routes(app: Flask) -> None:
    """Register room API routes - under 150 lines"""
    
    @app.route('/api/rooms')
    @login_required
    def get_rooms():
        """Get available rooms"""
        try:
            from services import get_room_service
            
            rooms = get_room_service().get_rooms(
                current_user,
                category=request.args.get('category', ''),
                age_filter=request.args.get('age', 'all'),
                search_query=request.args.get('search', '')
            )
            
            return jsonify({'rooms': rooms})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/rooms', methods=['POST'])
    @login_required
    def create_room():
        """Create a new room"""
        try:
            from services import get_room_service
            
            data = request.get_json()
            result = get_room_service().create_room(
                current_user,
                name=data.get('name', ''),
                description=data.get('description', ''),
                category=data.get('category', 'general'),
                age_restriction=data.get('age_restriction', 'all'),
                is_private=data.get('is_private', False),
                password=data.get('password', None)
            )
            
            return jsonify(result), result.get('status', 200)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/rooms/<int:room_id>/join', methods=['POST'])
    @login_required
    def join_room(room_id):
        """Join a room"""
        try:
            from services import get_room_service, initialize_websocket_service
            
            data = request.get_json() or {}
            password = data.get('password', None)
            
            result = get_room_service().join_room(current_user, room_id, password)
            
            if result['status'] == 200:
                # Inject websocket service
                from main import socketio
                websocket_service = initialize_websocket_service(socketio)
                websocket_service.emit_user_joined(current_user.id, current_user.username, room_id)
            
            return jsonify(result), result.get('status', 200)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/rooms/trending-categories')
    @login_required
    def get_trending_categories():
        """Get trending room categories"""
        try:
            from models import db, Chat
            from sqlalchemy import func
            
            # Get actual room categories with counts from database
            trending_categories = db.session.query(
                Chat.tags.label('category'),
                func.count(Chat.id).label('room_count')
            ).filter(
                Chat.tags.isnot(None),
                Chat.tags != '',
                Chat.is_public == True
            ).group_by(Chat.tags).order_by(
                func.count(Chat.id).desc()
            ).limit(6).all()
            
            categories = []
            for category_data in trending_categories:
                category_name = category_data.category
                room_count = category_data.room_count
                
                # Only include if there are actual rooms
                if room_count > 0:
                    categories.append({
                        'name': category_name,
                        'room_count': room_count
                    })
            
            return jsonify({'categories': categories})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/rooms/featured')
    @login_required
    def get_featured_rooms():
        """Get featured rooms"""
        try:
            from services import get_room_service
            
            # Get age-appropriate featured rooms based on user's age group
            featured_rooms = get_room_service().get_featured_rooms(current_user)
            
            return jsonify({'rooms': featured_rooms})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/rooms/discoverable', methods=['GET'])
    @login_required
    def get_discoverable_rooms():
        """Get public/discoverable rooms for discovery"""
        try:
            from services.room_service import get_room_service
            
            room_service = get_room_service()
            search_query = request.args.get('search', '')
            category = request.args.get('category', '')
            
            rooms = room_service.get_discoverable_rooms(
                current_user=current_user,
                category=category,
                search_query=search_query
            )
            
            return jsonify({'rooms': rooms}), 200
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/rooms/trending', methods=['GET'])
    @login_required
    def get_trending_rooms():
        """Get trending rooms"""
        try:
            from services.room_service import get_room_service
            
            room_service = get_room_service()
            rooms = room_service.get_trending_rooms(current_user)
            
            return jsonify({'rooms': rooms}), 200
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500