"""
API Babel Routes - SRIMI Microservice
Single Responsibility: Social media functionality only
"""

from flask import Flask, request, jsonify
from flask_login import login_required, current_user

def register_api_babel_routes(app: Flask) -> None:
    """Register Babel social media routes - under 120 lines"""
    
    @app.route('/api/babel/posts', methods=['POST'])
    @login_required
    def create_babel_post():
        """Create a new Babel post"""
        try:
            from services.babel_service import get_babel_service
            
            babel_service = get_babel_service()
            
            data = request.get_json()
            content = data.get('content', '').strip()
            post_type = data.get('post_type', 'text')
            
            if not content:
                return jsonify({
                    'success': False,
                    'error': 'Post content is required'
                }), 400
            
            result = babel_service.create_post(
                user_id=current_user.id,
                content=content,
                post_type=post_type
            )
            
            if result.get('status') == 201:
                return jsonify({'success': True, 'post': result['post']}), 201
            else:
                return jsonify({'success': False, 'error': result.get('error', 'Failed to create post')}), 400
                
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/babel/timeline')
    @login_required
    def get_babel_timeline():
        """Get Babel timeline posts"""
        try:
            from services.babel_service import get_babel_service
            
            babel_service = get_babel_service()
            
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            
            result = babel_service.get_timeline(
                user_id=current_user.id,
                page=page,
                per_page=per_page
            )
            
            return jsonify(result), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/babel/posts/<int:post_id>/like', methods=['POST'])
    @login_required
    def like_babel_post(post_id):
        """Like or unlike a Babel post"""
        try:
            from services.babel_service import get_babel_service
            
            babel_service = get_babel_service()
            
            result = babel_service.like_post(
                user_id=current_user.id,
                post_id=post_id
            )
            
            if result.get('status') == 200:
                return jsonify({'success': True, 'action': result['action'], 'likes_count': result['likes_count']}), 200
            else:
                return jsonify({'success': False, 'error': result.get('error', 'Failed to like post')}), 400
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/babel/posts/<int:post_id>/comments')
    @login_required
    def get_babel_comments(post_id):
        """Get comments for a Babel post"""
        try:
            from services.babel_service import get_babel_service
            
            babel_service = get_babel_service()
            
            page = request.args.get('page', 1, type=int)
            
            result = babel_service.get_post_comments(
                post_id=post_id,
                user_id=current_user.id,
                page=page
            )
            
            return jsonify(result), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/babel/posts/<int:post_id>/comments', methods=['POST'])
    @login_required
    def create_babel_comment(post_id):
        """Create a comment on a Babel post"""
        try:
            from services.babel_service import get_babel_service
            
            babel_service = get_babel_service()
            
            data = request.get_json()
            content = data.get('content', '').strip()
            
            if not content:
                return jsonify({
                    'success': False,
                    'error': 'Comment content is required'
                }), 400
            
            result = babel_service.add_comment(
                user_id=current_user.id,
                post_id=post_id,
                content=content
            )
            
            if result.get('status') == 201:
                return jsonify({'success': True, 'comment': result['comment']}), 201
            else:
                return jsonify({'success': False, 'error': result.get('error', 'Failed to create comment')}), 400
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500