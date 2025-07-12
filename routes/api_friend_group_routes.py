"""
API Friend Group Routes - SRIMI Microservice
Single Responsibility: Handle friend group API endpoints
"""

from flask import request, jsonify, session
from functools import wraps
from auth import login_required
from services.friend_group_service import FriendGroupService
from models.user_models import FriendGroup, FriendGroupMember
from models import db
import logging

# Initialize logger
logger = logging.getLogger(__name__)

def register_api_friend_group_routes(app):
    """Register friend group API micro-components"""
    
    friend_group_service = FriendGroupService()
    
    @app.route('/api/friend-groups/create', methods=['POST'])
    @login_required
    def create_friend_group():
        """Create a new friend group"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': 'No data provided'}), 400
            
            group_name = data.get('group_name', '').strip()
            group_type = data.get('group_type', 'mixed')
            
            if not group_name:
                return jsonify({'success': False, 'error': 'Group name is required'}), 400
            
            if len(group_name) < 2:
                return jsonify({'success': False, 'error': 'Group name must be at least 2 characters'}), 400
            
            if len(group_name) > 50:
                return jsonify({'success': False, 'error': 'Group name must be less than 50 characters'}), 400
            
            # Validate group type
            valid_types = ['mixed', 'chat_only', 'babel_only']
            if group_type not in valid_types:
                return jsonify({'success': False, 'error': 'Invalid group type'}), 400
            
            user_id = session.get('user_id')
            
            # Create the friend group
            result = friend_group_service.create_friend_group(user_id, group_name, group_type)
            
            if result.get('success'):
                return jsonify({
                    'success': True,
                    'group_id': result.get('group_id'),
                    'group_name': result.get('group_name'),
                    'group_type': result.get('group_type'),
                    'message': 'Friend group created successfully'
                }), 201
            else:
                return jsonify({'success': False, 'error': result.get('error', 'Failed to create group')}), 500
            
        except Exception as e:
            logger.error(f"Error creating friend group: {str(e)}")
            return jsonify({'success': False, 'error': 'Internal server error'}), 500
    
    @app.route('/api/friend-groups/my-groups', methods=['GET'])
    @login_required
    def get_my_groups():
        """Get current user's friend groups"""
        try:
            user_id = session.get('user_id')
            
            # Get groups where user is a member
            memberships = FriendGroupMember.query.filter_by(user_id=user_id).all()
            
            groups = []
            for membership in memberships:
                group = membership.friend_group
                if group:
                    # Count members
                    member_count = FriendGroupMember.query.filter_by(friend_group_id=group.id).count()
                    
                    # Determine capabilities based on group type
                    can_chat = group.type.value in ['mixed', 'chat_only']
                    can_babel = group.type.value in ['mixed', 'babel_only']
                    
                    groups.append({
                        'group_id': group.id,
                        'group_name': group.name,
                        'group_type': group.type.value,
                        'member_count': member_count,
                        'can_chat': can_chat,
                        'can_babel': can_babel,
                        'role': membership.role.value,
                        'created_at': group.created_at.isoformat() if group.created_at else None
                    })
            
            return jsonify({
                'success': True,
                'groups': groups,
                'total': len(groups)
            }), 200
            
        except Exception as e:
            logger.error(f"Error getting friend groups: {str(e)}")
            return jsonify({'success': False, 'error': 'Internal server error'}), 500
    
    @app.route('/api/friend-groups/<int:group_id>', methods=['GET'])
    @login_required
    def get_group_details(group_id):
        """Get detailed information about a specific friend group"""
        try:
            user_id = session.get('user_id')
            
            # Check if user is a member of this group
            membership = FriendGroupMember.query.filter_by(
                friend_group_id=group_id,
                user_id=user_id
            ).first()
            
            if not membership:
                return jsonify({'success': False, 'error': 'You are not a member of this group'}), 403
            
            group = membership.friend_group
            if not group:
                return jsonify({'success': False, 'error': 'Group not found'}), 404
            
            # Get all members
            members = []
            for member in group.members:
                members.append({
                    'user_id': member.user_id,
                    'username': member.user.username,
                    'display_name': member.user.display_name,
                    'role': member.role.value,
                    'joined_at': member.joined_at.isoformat() if member.joined_at else None
                })
            
            # Determine capabilities
            can_chat = group.type.value in ['mixed', 'chat_only']
            can_babel = group.type.value in ['mixed', 'babel_only']
            
            return jsonify({
                'success': True,
                'group': {
                    'id': group.id,
                    'name': group.name,
                    'type': group.type.value,
                    'created_at': group.created_at.isoformat() if group.created_at else None,
                    'creator_id': group.creator_id,
                    'can_chat': can_chat,
                    'can_babel': can_babel,
                    'members': members,
                    'member_count': len(members),
                    'user_role': membership.role.value
                }
            }), 200
            
        except Exception as e:
            logger.error(f"Error getting group details: {str(e)}")
            return jsonify({'success': False, 'error': 'Internal server error'}), 500
    
    @app.route('/api/friend-groups/<int:group_id>/delete', methods=['DELETE'])
    @login_required
    def delete_group(group_id):
        """Delete a friend group (only creator can delete)"""
        try:
            user_id = session.get('user_id')
            
            # Check if user is the creator of this group
            group = FriendGroup.query.filter_by(id=group_id, creator_id=user_id).first()
            
            if not group:
                return jsonify({'success': False, 'error': 'Group not found or you are not the creator'}), 404
            
            # Delete all memberships first
            FriendGroupMember.query.filter_by(friend_group_id=group_id).delete()
            
            # Delete the group
            db.session.delete(group)
            db.session.commit()
            
            logger.info(f"Friend group {group_id} deleted by user {user_id}")
            
            return jsonify({
                'success': True,
                'message': 'Friend group deleted successfully'
            }), 200
            
        except Exception as e:
            logger.error(f"Error deleting friend group: {str(e)}")
            db.session.rollback()
            return jsonify({'success': False, 'error': 'Internal server error'}), 500
    
    logger.info("👥 Friend Group API routes registered")