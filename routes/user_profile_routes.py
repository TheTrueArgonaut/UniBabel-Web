"""
User Profile Routes - SRIMI Microservice Routes
Single Responsibility: User profile API endpoints
"""

from flask import Flask, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from typing import Dict, Any

def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        if not getattr(current_user, 'is_data_vampire_admin', False):
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def register_user_profile_routes(app: Flask, audit_logger) -> None:
    """Register user profile micro-routes with harmonious coordination"""
    
    # Register with endpoint coordinator for harmony
    from services.endpoint_coordinator import endpoint_coordinator
    endpoint_coordinator.register_endpoint('user_profiles', lambda: 'user_profile_data')
    
    @app.route('/api/admin/user-profiles')
    @login_required
    @require_admin
    def get_user_profiles():
        """Main user profiles endpoint for dashboard harmony"""
        try:
            from services.user_profile_service import user_profile_service
            from services.user_stats_service import user_stats_service
            
            # Get query parameters
            limit = int(request.args.get('limit', 50))
            offset = int(request.args.get('offset', 0))
            
            # Get basic profiles
            profiles = user_profile_service.get_user_profiles_batch(limit=limit, offset=offset)
            
            # Get basic stats
            stats = user_stats_service.get_basic_stats()
            
            # Get unified data from coordinator for harmony
            from services.endpoint_coordinator import endpoint_coordinator
            unified_data = endpoint_coordinator.get_unified_dashboard_data()
            
            # Convert to response format
            users_data = {}
            for profile in profiles:
                users_data[str(profile.user_id)] = {
                    'username': profile.username,
                    'email': profile.email,
                    'user_type': profile.user_type,
                    'is_online': profile.is_online,
                    'is_blocked': profile.is_blocked,
                    'is_premium': profile.is_premium,
                    'last_seen': profile.last_seen.isoformat() if profile.last_seen else None,
                    'created_at': profile.created_at.isoformat() if profile.created_at else None,
                    'blocked_reason': profile.block_reason,
                    'market_value': 0.0,  # Basic endpoint
                    'vulnerability_score': 0.0  # Basic endpoint
                }
            
            audit_logger.log_admin_action(
                current_user, 
                'get_user_profiles', 
                'user_profiles', 
                {'count': len(profiles), 'limit': limit, 'offset': offset}
            )
            
            # Enhanced response with coordination
            response_data = {
                'total_users': stats.total_users,
                'online_users': stats.online_users,
                'premium_users': stats.premium_users,
                'blocked_users': stats.blocked_users,
                'users': users_data,
                'coordination_status': 'active',
                'unified_metrics': unified_data.get('unified_metrics', {}),
                'pagination': {
                    'limit': limit,
                    'offset': offset,
                    'returned_count': len(profiles)
                }
            }
            
            return jsonify(response_data)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/user-profiles/basic')
    @login_required
    @require_admin
    def get_basic_user_profiles():
        """Get basic user profiles without data warehouse enrichment"""
        try:
            from services.user_profile_service import user_profile_service
            from services.user_stats_service import user_stats_service
            
            # Get query parameters
            limit = int(request.args.get('limit', 50))
            offset = int(request.args.get('offset', 0))
            
            # Get basic profiles
            profiles = user_profile_service.get_user_profiles_batch(limit=limit, offset=offset)
            
            # Get basic stats
            stats = user_stats_service.get_basic_stats()
            
            # Convert to response format
            users_data = {}
            for profile in profiles:
                users_data[str(profile.user_id)] = {
                    'username': profile.username,
                    'email': profile.email,
                    'user_type': profile.user_type,
                    'is_online': profile.is_online,
                    'is_blocked': profile.is_blocked,
                    'is_premium': profile.is_premium,
                    'last_seen': profile.last_seen.isoformat() if profile.last_seen else None,
                    'created_at': profile.created_at.isoformat() if profile.created_at else None,
                    'blocked_reason': profile.block_reason,
                    'market_value': 0.0,  # Not enriched
                    'vulnerability_score': 0.0  # Not enriched
                }
            
            audit_logger.log_admin_action(
                current_user, 
                'get_basic_user_profiles', 
                'user_profiles', 
                {'count': len(profiles), 'limit': limit, 'offset': offset}
            )
            
            return jsonify({
                'total_users': stats.total_users,
                'online_users': stats.online_users,
                'premium_users': stats.premium_users,
                'blocked_users': stats.blocked_users,
                'users': users_data,
                'pagination': {
                    'limit': limit,
                    'offset': offset,
                    'returned_count': len(profiles)
                }
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/user-profiles/enriched')
    @login_required
    @require_admin
    def get_enriched_user_profiles():
        """Get user profiles enriched with data warehouse information"""
        try:
            from services.user_profile_service import user_profile_service
            from services.user_stats_service import user_stats_service
            from services.user_enrichment_service import user_enrichment_service
            
            # Get query parameters
            limit = int(request.args.get('limit', 50))
            offset = int(request.args.get('offset', 0))
            
            # Get basic profiles
            profiles = user_profile_service.get_user_profiles_batch(limit=limit, offset=offset)
            
            # Enrich with data warehouse info
            enriched_profiles = user_enrichment_service.enrich_user_profiles_batch(profiles)
            
            # Get stats
            stats = user_stats_service.get_basic_stats()
            system_stats = user_enrichment_service.get_system_stats()
            
            # Convert to response format
            users_data = user_enrichment_service.get_enriched_profiles_as_dict(enriched_profiles)
            
            audit_logger.log_admin_action(
                current_user, 
                'get_enriched_user_profiles', 
                'user_profiles', 
                {'count': len(enriched_profiles), 'limit': limit, 'offset': offset}
            )
            
            return jsonify({
                'total_users': stats.total_users,
                'online_users': stats.online_users,
                'premium_users': stats.premium_users,
                'blocked_users': stats.blocked_users,
                'users': users_data,
                'system_stats': system_stats,
                'pagination': {
                    'limit': limit,
                    'offset': offset,
                    'returned_count': len(enriched_profiles)
                }
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/user-profiles/search')
    @login_required
    @require_admin
    def search_user_profiles():
        """Search user profiles"""
        try:
            from services.user_profile_service import user_profile_service
            from services.user_enrichment_service import user_enrichment_service
            
            # Get search parameters
            search_term = request.args.get('search', '').strip()
            enrich = request.args.get('enrich', 'false').lower() == 'true'
            limit = int(request.args.get('limit', 50))
            
            if not search_term:
                return jsonify({'error': 'Search term is required'}), 400
            
            # Search profiles
            profiles = user_profile_service.search_users(search_term, limit=limit)
            
            if enrich:
                enriched_profiles = user_enrichment_service.enrich_user_profiles_batch(profiles)
                users_data = user_enrichment_service.get_enriched_profiles_as_dict(enriched_profiles)
            else:
                users_data = {}
                for profile in profiles:
                    users_data[str(profile.user_id)] = {
                        'username': profile.username,
                        'email': profile.email,
                        'user_type': profile.user_type,
                        'is_online': profile.is_online,
                        'is_blocked': profile.is_blocked,
                        'is_premium': profile.is_premium,
                        'last_seen': profile.last_seen.isoformat() if profile.last_seen else None,
                        'created_at': profile.created_at.isoformat() if profile.created_at else None,
                        'blocked_reason': profile.block_reason,
                        'market_value': 0.0,
                        'vulnerability_score': 0.0
                    }
            
            audit_logger.log_admin_action(
                current_user, 
                'search_user_profiles', 
                'user_profiles', 
                {'search_term': search_term, 'results_count': len(profiles), 'enriched': enrich}
            )
            
            return jsonify({
                'search_term': search_term,
                'results_count': len(profiles),
                'users': users_data,
                'enriched': enrich
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/user-profiles/filter')
    @login_required
    @require_admin
    def filter_user_profiles():
        """Filter user profiles by status and type"""
        try:
            from services.user_profile_service import user_profile_service
            from services.user_enrichment_service import user_enrichment_service
            
            # Get filter parameters
            status = request.args.get('status', '')
            user_type = request.args.get('user_type', '')
            enrich = request.args.get('enrich', 'false').lower() == 'true'
            limit = int(request.args.get('limit', 50))
            
            profiles = []
            
            # Apply filters
            if status:
                profiles = user_profile_service.filter_users_by_status(status, limit=limit)
            elif user_type:
                profiles = user_profile_service.filter_users_by_type(user_type, limit=limit)
            else:
                profiles = user_profile_service.get_user_profiles_batch(limit=limit)
            
            if enrich:
                enriched_profiles = user_enrichment_service.enrich_user_profiles_batch(profiles)
                users_data = user_enrichment_service.get_enriched_profiles_as_dict(enriched_profiles)
            else:
                users_data = {}
                for profile in profiles:
                    users_data[str(profile.user_id)] = {
                        'username': profile.username,
                        'email': profile.email,
                        'user_type': profile.user_type,
                        'is_online': profile.is_online,
                        'is_blocked': profile.is_blocked,
                        'is_premium': profile.is_premium,
                        'last_seen': profile.last_seen.isoformat() if profile.last_seen else None,
                        'created_at': profile.created_at.isoformat() if profile.created_at else None,
                        'blocked_reason': profile.block_reason,
                        'market_value': 0.0,
                        'vulnerability_score': 0.0
                    }
            
            audit_logger.log_admin_action(
                current_user, 
                'filter_user_profiles', 
                'user_profiles', 
                {'status': status, 'user_type': user_type, 'results_count': len(profiles), 'enriched': enrich}
            )
            
            return jsonify({
                'filters': {
                    'status': status,
                    'user_type': user_type
                },
                'results_count': len(profiles),
                'users': users_data,
                'enriched': enrich
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/user-profiles/stats')
    @login_required
    @require_admin
    def get_user_profile_stats():
        """Get detailed user profile statistics"""
        try:
            from services.user_stats_service import user_stats_service
            from services.user_enrichment_service import user_enrichment_service
            
            # Get various statistics
            basic_stats = user_stats_service.get_basic_stats()
            distribution = user_stats_service.get_user_distribution()
            growth_metrics = user_stats_service.get_growth_metrics()
            system_stats = user_enrichment_service.get_system_stats()
            
            audit_logger.log_admin_action(
                current_user, 
                'get_user_profile_stats', 
                'user_stats', 
                {'total_users': basic_stats.total_users}
            )
            
            return jsonify({
                'basic_stats': {
                    'total_users': basic_stats.total_users,
                    'online_users': basic_stats.online_users,
                    'offline_users': basic_stats.offline_users,
                    'premium_users': basic_stats.premium_users,
                    'blocked_users': basic_stats.blocked_users,
                    'adult_users': basic_stats.adult_users,
                    'teen_users': basic_stats.teen_users
                },
                'distribution': distribution,
                'growth_metrics': growth_metrics,
                'system_stats': system_stats
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/admin/user-profiles/bulk-search')
    @login_required
    @require_admin
    def bulk_search_users():
        """Search users specifically for bulk operations"""
        try:
            from services.user_profile_service import user_profile_service
            from services.user_enrichment_service import user_enrichment_service

            # Get search parameters
            search_term = request.args.get('search', '').strip()
            user_type = request.args.get('user_type', '')
            status = request.args.get('status', '')
            min_market_value = request.args.get('min_market_value', 0, type=float)
            max_market_value = request.args.get('max_market_value', 0, type=float)
            sort_by = request.args.get('sort_by', 'username')
            limit = int(request.args.get('limit', 100))

            # Start with basic search if term provided
            if search_term:
                profiles = user_profile_service.search_users(search_term, limit=limit*2)  # Get more to filter
            else:
                profiles = user_profile_service.get_user_profiles_batch(limit=limit*2)

            # Apply additional filters
            if user_type:
                profiles = [p for p in profiles if p.user_type.lower() == user_type.lower()]

            if status:
                if status == 'online':
                    profiles = [p for p in profiles if p.is_online]
                elif status == 'offline':
                    profiles = [p for p in profiles if not p.is_online]
                elif status == 'blocked':
                    profiles = [p for p in profiles if p.is_blocked]
                elif status == 'premium':
                    profiles = [p for p in profiles if p.is_premium]
                elif status == 'non_admin':
                    # This is the most important filter for bulk operations
                    from models import User
                    non_admin_ids = []
                    for profile in profiles:
                        user = User.query.get(profile.user_id)
                        if user and not getattr(user, 'is_data_vampire_admin', False):
                            non_admin_ids.append(profile.user_id)
                    profiles = [p for p in profiles if p.user_id in non_admin_ids]

            # Enrich with data warehouse info for market value filtering
            enriched_profiles = user_enrichment_service.enrich_user_profiles_batch(profiles)

            # Apply market value filters
            if min_market_value > 0:
                enriched_profiles = [p for p in enriched_profiles if p.market_value >= min_market_value]

            if max_market_value > 0:
                enriched_profiles = [p for p in enriched_profiles if p.market_value <= max_market_value]

            # Sort results
            if sort_by == 'username':
                enriched_profiles.sort(key=lambda x: x.username.lower())
            elif sort_by == 'market_value':
                enriched_profiles.sort(key=lambda x: x.market_value, reverse=True)
            elif sort_by == 'created_at':
                enriched_profiles.sort(key=lambda x: x.created_at or '', reverse=True)
            elif sort_by == 'last_seen':
                enriched_profiles.sort(key=lambda x: x.last_seen or '', reverse=True)

            # Limit final results
            enriched_profiles = enriched_profiles[:limit]

            # Convert to response format
            users_data = user_enrichment_service.get_enriched_profiles_as_dict(enriched_profiles)

            # Add bulk operation safety info
            bulk_info = {
                'total_found': len(enriched_profiles),
                'admin_count': sum(1 for p in enriched_profiles if getattr(p, 'is_admin', False)),
                'non_admin_count': len(enriched_profiles) - sum(1 for p in enriched_profiles if getattr(p, 'is_admin', False)),
                'estimated_rooms_to_delete': 0,  # Could calculate this if needed
                'safety_warnings': []
            }

            # Add safety warnings
            if len(enriched_profiles) > 50:
                bulk_info['safety_warnings'].append('Large deletion - consider processing in batches')

            admin_count = sum(1 for p in enriched_profiles if getattr(p, 'is_admin', False))
            if admin_count > 0:
                bulk_info['safety_warnings'].append(f'{admin_count} admin users found - these will be protected')

            audit_logger.log_admin_action(
                current_user, 
                'bulk_search_users', 
                'bulk_operations', 
                {
                    'search_term': search_term, 
                    'filters': {
                        'user_type': user_type,
                        'status': status,
                        'min_market_value': min_market_value,
                        'max_market_value': max_market_value
                    },
                    'results_count': len(enriched_profiles)
                }
            )

            return jsonify({
                'search_term': search_term,
                'filters_applied': {
                    'user_type': user_type,
                    'status': status,
                    'min_market_value': min_market_value,
                    'max_market_value': max_market_value,
                    'sort_by': sort_by
                },
                'users': users_data,
                'bulk_info': bulk_info
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/admin/user-profiles/bulk-preview')
    @login_required
    @require_admin
    def bulk_preview_deletion():
        """Preview what would be deleted in a bulk operation"""
        try:
            from models import User, Room, RoomMember

            # Get user IDs from request
            user_ids = request.args.getlist('user_ids[]')
            if not user_ids:
                return jsonify({'error': 'No user IDs provided'}), 400

            # Convert to integers
            user_ids = [int(uid) for uid in user_ids]

            # Get users
            users = User.query.filter(User.id.in_(user_ids)).all()

            # Calculate impact
            total_users = len(users)
            admin_users = sum(1 for u in users if getattr(u, 'is_data_vampire_admin', False))
            deletable_users = total_users - admin_users

            # Count rooms that would be deleted
            total_rooms = 0
            total_room_members = 0

            for user in users:
                if not getattr(user, 'is_data_vampire_admin', False):
                    # Count rooms owned by this user
                    user_rooms = Room.query.filter_by(owner_id=user.id).all()
                    total_rooms += len(user_rooms)
                    
                    # Count room members in those rooms
                    for room in user_rooms:
                        total_room_members += RoomMember.query.filter_by(room_id=room.id).count()

            # Safety warnings
            warnings = []
            if admin_users > 0:
                warnings.append(f'{admin_users} admin users will be protected from deletion')
            if total_rooms > 10:
                warnings.append(f'Large number of rooms will be deleted: {total_rooms}')
            if total_room_members > 50:
                warnings.append(f'Many room memberships will be affected: {total_room_members}')

            audit_logger.log_admin_action(
                current_user, 
                'bulk_preview_deletion', 
                'bulk_operations', 
                {
                    'user_ids': user_ids,
                    'impact': {
                        'total_users': total_users,
                        'deletable_users': deletable_users,
                        'total_rooms': total_rooms,
                        'total_room_members': total_room_members
                    }
                }
            )

            return jsonify({
                'impact_summary': {
                    'total_users_selected': total_users,
                    'admin_users_protected': admin_users,
                    'users_to_delete': deletable_users,
                    'rooms_to_delete': total_rooms,
                    'room_memberships_affected': total_room_members
                },
                'warnings': warnings,
                'safe_to_proceed': len(warnings) == 0 or (len(warnings) == 1 and admin_users > 0)
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500