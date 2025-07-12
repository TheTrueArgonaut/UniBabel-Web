"""
Admin User Routes - SRIMI Microservice
Single Responsibility: User management API endpoints
"""

from flask import Flask, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from models.user_models import User
from models import db
from datetime import datetime
from enum import Enum

class RoomType(Enum):
    PUBLIC = 'public'
    PRIVATE = 'private'
    VOICE_ONLY = 'voice_only'
    VOICE_CHAT = 'voice_chat'

def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        if not getattr(current_user, 'is_data_vampire_admin', False):
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def register_admin_user_routes(app: Flask, audit_logger) -> None:
    """Register admin user routes in the app"""
    
    @app.route('/api/admin/user-profiles')
    @login_required
    @require_admin
    def get_admin_user_profiles():
        """Get all user profiles for admin management"""
        try:
            users = User.query.all()
            
            user_data = {}
            for user in users:
                user_data[user.id] = {
                    'username': user.username,
                    'email': user.email,
                    'user_type': user.user_type.value,
                    'is_online': user.is_online,
                    'is_blocked': user.is_blocked,
                    'is_premium': user.subscription_tier != 'free',
                    'subscription_tier': user.subscription_tier,
                    'data_collection_enabled': user.should_collect_data(),
                    'market_value': user.market_value,
                    'data_points_collected': user.data_points_collected,
                    'last_seen': user.last_seen.isoformat() if user.last_seen else None,
                    'created_at': user.created_at.isoformat(),
                    'block_reason': user.block_reason,
                    'stripe_customer_id': user.stripe_customer_id,
                }
            
            # Calculate stats
            total_users = len(users)
            online_users = sum(1 for user in users if user.is_online)
            premium_users = sum(1 for user in users if user.subscription_tier != 'free')
            blocked_users = sum(1 for user in users if user.is_blocked)
            
            # Log admin action
            audit_logger.log_admin_action(
                current_user, 
                'view_user_profiles', 
                'user_management', 
                {'total_users': total_users}
            )
            
            return jsonify({
                'users': user_data,
                'total_users': total_users,
                'online_users': online_users,
                'premium_users': premium_users,
                'blocked_users': blocked_users
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/admin/user/<int:user_id>/toggle-data-collection', methods=['POST'])
    @login_required
    @require_admin
    def toggle_user_data_collection(user_id):
        """Toggle data collection for a specific user"""
        try:
            user = User.query.get_or_404(user_id)
            
            # Get reason from request
            data = request.get_json() or {}
            reason = data.get('reason', 'Admin override')
            
            # Toggle data collection with admin override
            old_status = user.should_collect_data()
            new_status = user.toggle_data_collection(
                admin_user_id=current_user.id,
                reason=reason
            )
            
            # Log the action
            audit_logger.log_admin_action(
                current_user,
                'toggle_data_collection',
                f'user_{user_id}',
                {
                    'user_id': user_id,
                    'username': user.username,
                    'old_status': old_status,
                    'new_status': new_status,
                    'reason': reason
                }
            )
            
            return jsonify({
                'success': True,
                'data_collection_enabled': new_status,
                'message': f'Data collection {"enabled" if new_status else "disabled"} for {user.username}'
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/user/<int:user_id>/ban', methods=['POST'])
    @login_required
    @require_admin
    def ban_user(user_id):
        """Ban a user account"""
        try:
            user = User.query.get_or_404(user_id)
            
            # Prevent banning other admins
            if user.is_data_vampire_admin:
                return jsonify({'error': 'Cannot ban admin users'}), 403
            
            data = request.get_json() or {}
            reason = data.get('reason', 'Admin ban')
            
            user.is_blocked = True
            user.block_reason = reason
            db.session.commit()
            
            # Log the action
            audit_logger.log_admin_action(
                current_user,
                'user_ban',
                f'user_{user_id}',
                {
                    'user_id': user_id,
                    'username': user.username,
                    'reason': reason
                }
            )
            
            return jsonify({
                'success': True,
                'message': f'User {user.username} has been banned'
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/user/<int:user_id>/unban', methods=['POST'])
    @login_required
    @require_admin
    def unban_user(user_id):
        """Unban a user account"""
        try:
            user = User.query.get_or_404(user_id)
            
            user.is_blocked = False
            user.block_reason = None
            db.session.commit()
            
            # Log the action
            audit_logger.log_admin_action(
                current_user,
                'user_unban',
                f'user_{user_id}',
                {
                    'user_id': user_id,
                    'username': user.username
                }
            )
            
            return jsonify({
                'success': True,
                'message': f'User {user.username} has been unbanned'
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/user/<int:user_id>/subscription-info')
    @login_required
    @require_admin
    def get_user_subscription_info(user_id):
        """Get detailed subscription information for a user"""
        try:
            user = User.query.get_or_404(user_id)
            
            subscription_info = user.get_subscription_info()
            
            return jsonify({
                'user_id': user_id,
                'username': user.username,
                'subscription_info': subscription_info
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/user/<int:user_id>/upgrade-premium', methods=['POST'])
    @login_required
    @require_admin
    def upgrade_user_premium(user_id):
        """Manually upgrade user to premium (for testing/support)"""
        try:
            user = User.query.get_or_404(user_id)
            
            data = request.get_json() or {}
            tier = data.get('tier', 'premium_monthly')
            
            user.upgrade_to_premium(tier=tier)
            
            # Log the action
            audit_logger.log_admin_action(
                current_user,
                'user_upgrade_premium',
                f'user_{user_id}',
                {
                    'user_id': user_id,
                    'username': user.username,
                    'tier': tier
                }
            )
            
            return jsonify({
                'success': True,
                'message': f'User {user.username} upgraded to {tier}',
                'subscription_info': user.get_subscription_info()
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/user/<int:user_id>/downgrade-free', methods=['POST'])
    @login_required
    @require_admin
    def downgrade_user_free(user_id):
        """Manually downgrade user to free (for testing/support)"""
        try:
            user = User.query.get_or_404(user_id)
            
            data = request.get_json() or {}
            reason = data.get('reason', 'Admin downgrade')
            
            user.downgrade_to_free(reason=reason)
            
            # Log the action
            audit_logger.log_admin_action(
                current_user,
                'user_downgrade_free',
                f'user_{user_id}',
                {
                    'user_id': user_id,
                    'username': user.username,
                    'reason': reason
                }
            )
            
            return jsonify({
                'success': True,
                'message': f'User {user.username} downgraded to free',
                'subscription_info': user.get_subscription_info()
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500


    @app.route('/api/admin/user/<int:user_id>/chat', methods=['GET', 'POST'])
    @login_required
    @require_admin
    def user_chat(user_id):
        """Chat with a specific user"""
        try:
            user = User.query.get_or_404(user_id)
            
            if request.method == 'GET':
                # Get chat history
                messages = []
                try:
                    from models import Message, Room, RoomMember
                    
                    # Find DM room between admin and user
                    dm_room = db.session.query(Room).join(RoomMember).filter(
                        Room.type == RoomType.PRIVATE,
                        RoomMember.user_id.in_([current_user.id, user_id])
                    ).group_by(Room.id).having(
                        db.func.count(RoomMember.user_id) == 2
                    ).first()
                    
                    if dm_room:
                        messages_query = Message.query.filter_by(chat_id=dm_room.id).order_by(Message.timestamp.desc()).limit(50).all()
                        messages = [{
                            'text': msg.original_text,
                            'timestamp': msg.timestamp.isoformat(),
                            'is_admin': msg.sender_id == current_user.id
                        } for msg in reversed(messages_query)]
                    
                except Exception as e:
                    print(f"Error loading chat messages: {e}")
                    messages = []
                
                return jsonify({
                    'success': True,
                    'messages': messages,
                    'user': {
                        'id': user.id,
                        'username': user.username
                    }
                })
            
            elif request.method == 'POST':
                # Send message to user
                data = request.get_json()
                message_text = data.get('text', '').strip()
                
                if not message_text:
                    return jsonify({'success': False, 'error': 'Message cannot be empty'}), 400
                
                # Use the admin messaging service
                from services.admin_messaging_service import admin_messaging_service
                
                result = admin_messaging_service.send_direct_message(
                    admin_user_id=current_user.id,
                    target_user_id=user_id,
                    content=message_text,
                    message_type='admin_direct',
                    ip_address=request.remote_addr or 'unknown',
                    user_agent=request.headers.get('User-Agent', 'unknown')
                )
                
                if result['success']:
                    # Log the action
                    audit_logger.log_admin_action(
                        current_user,
                        'send_direct_message',
                        f'user_{user_id}',
                        {
                            'user_id': user_id,
                            'username': user.username,
                            'message_length': len(message_text)
                        }
                    )
                    
                    return jsonify({
                        'success': True,
                        'message': 'Message sent successfully',
                        'timestamp': result.get('timestamp')
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': result.get('error', 'Failed to send message')
                    }), 400
                    
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/admin/user/<int:user_id>/details')
    @login_required
    @require_admin
    def get_user_details(user_id):
        """Get detailed user information for admin view"""
        try:
            user = User.query.get_or_404(user_id)
            
            # Get subscription info safely
            try:
                subscription_info = user.get_subscription_info()
            except:
                subscription_info = {
                    'tier': getattr(user, 'subscription_tier', 'free'),
                    'status': getattr(user, 'subscription_status', 'active'),
                    'data_collection_enabled': getattr(user, 'data_collection_enabled', True),
                    'market_value': getattr(user, 'market_value', 0),
                    'data_points_collected': getattr(user, 'data_points_collected', 0),
                    'lifetime_value': 0,
                    'monthly_value': 0
                }
            
            # Get activity stats safely
            activity_stats = {
                'total_messages': 0,
                'total_translations': 0,
                'login_count': 0,
                'last_login': user.last_seen.isoformat() if user.last_seen else None,
                'account_age_days': (datetime.now() - user.created_at).days if user.created_at else 0,
                'data_points_collected': getattr(user, 'data_points_collected', 0),
                'last_activity': user.last_seen.isoformat() if user.last_seen else None
            }
            
            # Try to get message count from database
            try:
                from models import Message
                message_count = Message.query.filter_by(sender_id=user_id).count()
                activity_stats['total_messages'] = message_count
            except Exception:
                pass
            
            # Try to get translation count
            try:
                from models.translation_models import Translation
                translation_count = Translation.query.filter_by(user_id=user_id).count()
                activity_stats['total_translations'] = translation_count
            except Exception:
                pass
            
            # Get payment history
            payment_history = []
            try:
                from models.subscription_models import SubscriptionRecord
                payments = SubscriptionRecord.query.filter_by(user_id=user_id).order_by(SubscriptionRecord.created_at.desc()).limit(10).all()
                for payment in payments:
                    payment_history.append({
                        'date': payment.created_at.isoformat(),
                        'amount': payment.amount_paid,
                        'status': payment.status,
                        'subscription_tier': payment.subscription_tier,
                        'payment_method': payment.payment_method,
                        'stripe_subscription_id': payment.stripe_subscription_id
                    })
            except Exception:
                pass
            
            # Get data collection history
            data_collection_history = []
            try:
                if hasattr(user, 'get_data_collection_history'):
                    data_collection_history = user.get_data_collection_history()
            except Exception:
                pass
            
            # Calculate user value metrics
            user_value = {
                'market_value': user.market_value or 0,
                'lifetime_value': subscription_info.get('lifetime_value', 0),
                'monthly_value': subscription_info.get('monthly_value', 0),
                'data_value': (user.data_points_collected or 0) * 0.01,  # $0.01 per data point
                'engagement_score': min(100, max(0, (
                    (activity_stats['total_messages'] * 0.1) + 
                    (activity_stats['total_translations'] * 0.2) + 
                    (activity_stats['account_age_days'] * 0.1)
                )))
            }
            
            # Get account health metrics safely
            try:
                data_collection_enabled = user.should_collect_data()
            except:
                data_collection_enabled = getattr(user, 'data_collection_enabled', True)
                
            account_health = {
                'risk_score': 0,
                'compliance_status': 'compliant',
                'data_consent_status': 'granted' if data_collection_enabled else 'denied',
                'account_status': 'banned' if user.is_blocked else 'active',
                'verification_status': 'verified' if getattr(user, 'email_verified', False) else 'unverified'
            }
            
            # Add risk factors
            if user.is_blocked:
                account_health['risk_score'] += 50
            if not getattr(user, 'email_verified', False):
                account_health['risk_score'] += 10
            if activity_stats['account_age_days'] < 7:
                account_health['risk_score'] += 20
                
            # Log admin action safely
            try:
                audit_logger.log_admin_action(
                    current_user,
                    'view_user_details',
                    f'user_{user_id}',
                    {
                        'user_id': user_id,
                        'username': user.username
                    }
                )
            except:
                pass
            
            return jsonify({
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'user_type': user.user_type.value if hasattr(user.user_type, 'value') else str(user.user_type),
                    'created_at': user.created_at.isoformat() if user.created_at else None,
                    'last_seen': user.last_seen.isoformat() if user.last_seen else None,
                    'is_online': user.is_online,
                    'is_blocked': user.is_blocked,
                    'block_reason': getattr(user, 'block_reason', None),
                    'is_premium': getattr(user, 'subscription_tier', 'free') != 'free',
                    'subscription_tier': getattr(user, 'subscription_tier', 'free'),
                    'stripe_customer_id': getattr(user, 'stripe_customer_id', None),
                    'email_verified': getattr(user, 'email_verified', False),
                    'is_data_vampire_admin': getattr(user, 'is_data_vampire_admin', False)
                },
                'subscription_info': subscription_info,
                'activity_stats': activity_stats,
                'payment_history': payment_history,
                'data_collection_history': data_collection_history,
                'user_value': user_value,
                'account_health': account_health,
                'data_collection_enabled': user.should_collect_data()
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/admin/user/<int:user_id>/privacy-report')
    @login_required
    @require_admin
    def generate_user_privacy_report(user_id):
        """Generate a comprehensive privacy report for a user"""
        try:
            user = User.query.get_or_404(user_id)
            
            # Generate comprehensive privacy report
            report = f"""
PRIVACY REPORT - ARGONAUT DIGITAL VENTURES LLC
UniBabel Translation Platform
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

USER INFORMATION:
- User ID: {user.id}
- Username: {user.username}
- Email: {user.email}
- User Type: {user.user_type.value}
- Account Created: {user.created_at.strftime('%Y-%m-%d') if user.created_at else 'Unknown'}
- Last Seen: {user.last_seen.strftime('%Y-%m-%d %H:%M:%S') if user.last_seen else 'Never'}

PRIVACY & DATA COLLECTION STATUS:
- Data Collection Enabled: {"Yes" if user.should_collect_data() else "No"}
- Subscription Tier: {user.subscription_tier}
- Premium Status: {"Yes" if user.subscription_tier != 'free' else "No"}
- Data Points Collected: {user.data_points_collected or 0}
- Market Value: ${user.market_value or 0}

ACCOUNT STATUS:
- Account Status: {"Banned" if user.is_blocked else "Active"}
- Email Verified: {"Yes" if user.email_verified else "No"}
- Admin Account: {"Yes" if user.is_data_vampire_admin else "No"}
{"- Block Reason: " + (user.block_reason or "N/A") if user.is_blocked else ""}

GDPR COMPLIANCE:
- Right to Access: Available via admin dashboard
- Right to Rectification: Available via admin dashboard
- Right to Erasure: Available via admin dashboard
- Right to Portability: Available via export function
- Right to Object: Data collection can be disabled

PRIVACY POLICY COMPLIANCE:
- Transparent Data Collection: {"Active" if user.should_collect_data() else "Disabled"}
- User Consent: {"Granted" if user.should_collect_data() else "Denied"}
- Data Minimization: Only necessary data collected
- Purpose Limitation: Data used only for stated purposes
- Storage Limitation: Data retained as per privacy policy

CONTACT INFORMATION:
- Company: Argonaut Digital Ventures LLC
- CEO: Sakelarios All
- Phone: 503-765-0420
- Address: 2420 Bahia Vista St, Sarasota, FL 34239
- Privacy Officer: privacy@argonautdv.com

This report was generated automatically and contains current privacy settings
for the specified user account. For questions about this report, please contact
our privacy officer at privacy@argonautdv.com.
"""
            
            # Log the action
            audit_logger.log_admin_action(
                current_user,
                'generate_privacy_report',
                f'user_{user_id}',
                {
                    'user_id': user_id,
                    'username': user.username,
                    'report_generated': True
                }
            )
            
            return jsonify({
                'success': True,
                'report': report,
                'user': {
                    'id': user.id,
                    'username': user.username
                }
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
