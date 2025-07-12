"""
Translation Management Routes - SRIMI Microservice Routes
Single Responsibility: Translation submission and review endpoints
"""

from flask import Flask, request, jsonify
from flask_login import login_required, current_user
from functools import wraps

def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        if not getattr(current_user, 'is_data_vampire_admin', False):
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def register_translation_management_routes(app: Flask, audit_logger) -> None:
    """Register translation management routes"""
    
    # User Routes
    @app.route('/api/translations/submit-fix', methods=['POST'])
    @login_required
    def submit_translation_fix():
        """User submits translation fix"""
        try:
            from services.translation_submission_service import translation_submission_service
            
            data = request.get_json()
            original_text = data.get('original_text', '').strip()
            suggested_translation = data.get('suggested_translation', '').strip()
            target_language = data.get('target_language', '').strip()
            current_translation = data.get('current_translation', '').strip()
            context = data.get('context', '').strip()
            
            if not original_text:
                return jsonify({'error': 'Original text required'}), 400
            
            if not suggested_translation:
                return jsonify({'error': 'Suggested translation required'}), 400
            
            if not target_language:
                return jsonify({'error': 'Target language required'}), 400
            
            result = translation_submission_service.submit_fix(
                user_id=current_user.id,
                original_text=original_text,
                suggested_translation=suggested_translation,
                target_language=target_language,
                current_translation=current_translation if current_translation else None,
                context=context if context else None
            )
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # Admin Routes
    @app.route('/api/admin/translations/pending')
    @login_required
    @require_admin
    def get_pending_translations():
        """Get pending translation submissions"""
        try:
            from services.translation_submission_service import translation_submission_service
            
            limit = int(request.args.get('limit', 50))
            
            submissions = translation_submission_service.get_pending_submissions(limit=limit)
            
            return jsonify({
                'success': True,
                'submissions': submissions,
                'count': len(submissions)
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/translations/all')
    @login_required
    @require_admin
    def get_all_translations():
        """Get all translation submissions"""
        try:
            from services.translation_submission_service import translation_submission_service
            
            status = request.args.get('status')
            limit = int(request.args.get('limit', 100))
            
            submissions = translation_submission_service.get_all_submissions(
                status=status,
                limit=limit
            )
            
            return jsonify({
                'success': True,
                'submissions': submissions,
                'count': len(submissions)
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/translations/approve/<int:submission_id>', methods=['POST'])
    @login_required
    @require_admin
    def approve_translation(submission_id):
        """Approve translation submission and add to cache"""
        try:
            from services.translation_review_service import translation_review_service
            from services.translation_cache_service import translation_cache_service
            
            data = request.get_json()
            admin_notes = data.get('admin_notes', '').strip()
            apply_to_cache = data.get('apply_to_cache', True)
            
            # First approve the submission
            review_result = translation_review_service.approve_submission(
                submission_id=submission_id,
                admin_id=current_user.id,
                admin_notes=admin_notes if admin_notes else None
            )
            
            if not review_result['success']:
                return jsonify(review_result), 400
            
            # Add to cache if requested and we have submission data
            if apply_to_cache and 'submission_data' in review_result:
                submission_data = review_result['submission_data']
                cache_result = translation_cache_service.add_translation(
                    original_text=submission_data['original_text'],
                    translated_text=submission_data['suggested_translation'],
                    target_language=submission_data['target_language'],
                    source_language='auto',
                    confidence=1.0,  # High confidence for human translations
                    metadata={
                        'source': 'user_submission',
                        'submission_id': submission_id,
                        'reviewed': True
                    }
                )
                
                review_result['applied_to_cache'] = cache_result['success']
                if not cache_result['success']:
                    review_result['cache_error'] = cache_result.get('error', 'Unknown cache error')
            
            # Log the approval
            audit_logger.log_admin_action(
                current_user,
                'approve_translation',
                'translation_management',
                {
                    'submission_id': submission_id,
                    'applied_to_cache': apply_to_cache,
                    'cache_success': review_result.get('applied_to_cache', False)
                }
            )
            
            return jsonify(review_result)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/translations/reject/<int:submission_id>', methods=['POST'])
    @login_required
    @require_admin
    def reject_translation(submission_id):
        """Reject translation submission"""
        try:
            from services.translation_review_service import translation_review_service
            
            data = request.get_json()
            reason = data.get('reason', '').strip()
            
            result = translation_review_service.reject_submission(
                submission_id=submission_id,
                admin_id=current_user.id,
                reason=reason if reason else None
            )
            
            if result['success']:
                audit_logger.log_admin_action(
                    current_user,
                    'reject_translation',
                    'translation_management',
                    {
                        'submission_id': submission_id,
                        'reason': reason
                    }
                )
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/translations/add-custom', methods=['POST'])
    @login_required
    @require_admin
    def add_custom_translation():
        """Add custom translation directly"""
        try:
            from services.translation_submission_service import translation_submission_service
            from services.translation_review_service import translation_review_service
            from services.translation_cache_service import translation_cache_service
            
            data = request.get_json()
            original_text = data.get('original_text', '').strip()
            translation = data.get('translation', '').strip()
            target_language = data.get('target_language', '').strip()
            apply_to_cache = data.get('apply_to_cache', True)
            
            if not original_text:
                return jsonify({'error': 'Original text required'}), 400
            
            if not translation:
                return jsonify({'error': 'Translation required'}), 400
            
            if not target_language:
                return jsonify({'error': 'Target language required'}), 400
            
            # Create submission first
            submission_result = translation_submission_service.submit_fix(
                user_id=current_user.id,
                original_text=original_text,
                suggested_translation=translation,
                target_language=target_language,
                current_translation=None,
                context="Admin-added custom translation"
            )
            
            if not submission_result['success']:
                return jsonify(submission_result), 400
            
            # Auto-approve
            review_result = translation_review_service.approve_submission(
                submission_id=submission_result['submission_id'],
                admin_id=current_user.id,
                admin_notes="Direct admin addition"
            )
            
            if not review_result['success']:
                return jsonify(review_result), 400
            
            # Apply to cache if requested
            if apply_to_cache:
                cache_result = translation_cache_service.add_translation(
                    original_text=original_text,
                    translated_text=translation,
                    target_language=target_language,
                    source_language='auto',
                    confidence=1.0,
                    metadata={
                        'source': 'admin_added',
                        'submission_id': submission_result['submission_id'],
                        'reviewed': True
                    }
                )
                
                review_result['applied_to_cache'] = cache_result['success']
                if not cache_result['success']:
                    review_result['cache_error'] = cache_result.get('error', 'Unknown cache error')
            
            audit_logger.log_admin_action(
                current_user,
                'add_custom_translation',
                'translation_management',
                {
                    'original_text': original_text[:100],
                    'target_language': target_language,
                    'applied_to_cache': apply_to_cache
                }
            )
            
            return jsonify(review_result)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/translations/cache')
    @login_required
    @require_admin
    def get_cache_translations():
        """Get cached translations"""
        try:
            from services.translation_cache_service import translation_cache_service
            
            target_language = request.args.get('target_language')
            limit = int(request.args.get('limit', 100))
            
            translations = translation_cache_service.get_cached_translations(
                target_language=target_language,
                limit=limit
            )
            
            return jsonify({
                'success': True,
                'translations': translations,
                'count': len(translations)
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/translations/cache/<int:cache_id>', methods=['DELETE'])
    @login_required
    @require_admin
    def remove_from_cache(cache_id):
        """Remove translation from cache"""
        try:
            from services.translation_cache_service import translation_cache_service
            
            result = translation_cache_service.remove_translation(cache_id)
            
            if result['success']:
                audit_logger.log_admin_action(
                    current_user,
                    'remove_translation_from_cache',
                    'translation_management',
                    {'cache_id': cache_id}
                )
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/translations/stats')
    @login_required
    @require_admin
    def get_translation_stats():
        """Get translation submission statistics"""
        try:
            from services.translation_submission_service import translation_submission_service
            from services.translation_review_service import translation_review_service
            from services.translation_cache_service import translation_cache_service
            
            # Get stats from all services
            submission_stats = translation_submission_service.get_submission_stats()
            review_stats = translation_review_service.get_review_stats()
            cache_stats = translation_cache_service.get_cache_stats()
            
            return jsonify({
                'success': True,
                'stats': {
                    'submissions': submission_stats,
                    'reviews': review_stats,
                    'cache': cache_stats,
                    'summary': {
                        'total_submissions': submission_stats.get('total_submissions', 0),
                        'pending_submissions': submission_stats.get('pending_submissions', 0),
                        'total_reviews': review_stats.get('total_reviews', 0),
                        'total_cached': cache_stats.get('total_translations', 0)
                    }
                }
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500