# Chat Routes - SRIMI: Single Responsibility for Chat Domain
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

def register_chat_routes(app: Flask) -> None:
    """Register chat-related routes with clear interfaces"""
    
    @app.route('/chat')
    @login_required
    def chat():
        """Chat interface - single responsibility"""
        from services import get_chat_service
        
        chat_service = get_chat_service()
        room_id = request.args.get('room')
        
        if room_id:
            result = chat_service.join_room_by_id(current_user, int(room_id))
            if result['status'] != 200:
                flash(f'Cannot join room: {result["error"]}', 'error')
                return redirect(url_for('rooms'))
            current_room = result['room']
        else:
            current_room = None
        
        user_chats = chat_service.get_user_chats(current_user)
        
        return render_template('chat.html', 
                             user=current_user, 
                             chats=user_chats,
                             current_room=current_room,
                             usage_info={'messages_used': 0, 'message_limit': 100, 'data_value': f"${current_user.id * 50}"})

    @app.route('/rooms')
    @login_required
    def rooms():
        """Rooms interface"""
        return render_template('rooms.html', user=current_user)

    @app.route('/babel')
    @login_required
    def babel():
        """Babel translation interface"""
        return render_template('babel.html', user=current_user)