"""
Admin Models
Handle admin-specific data models and settings
"""

from datetime import datetime
from models import db


class AdminSettings(db.Model):
    """Admin configuration settings"""
    __tablename__ = 'admin_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(100), unique=True, nullable=False)
    setting_value = db.Column(db.Text, nullable=False)
    setting_type = db.Column(db.String(20), default='string')  # string, integer, float, boolean, json
    description = db.Column(db.Text)
    category = db.Column(db.String(50), default='general')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __repr__(self):
        return f'<AdminSettings {self.setting_key}={self.setting_value}>'
    
    @classmethod
    def get_setting(cls, key, default=None):
        """Get a setting value"""
        setting = cls.query.filter_by(setting_key=key).first()
        if not setting:
            return default
        
        # Convert based on type
        if setting.setting_type == 'integer':
            return int(setting.setting_value)
        elif setting.setting_type == 'float':
            return float(setting.setting_value)
        elif setting.setting_type == 'boolean':
            return setting.setting_value.lower() in ['true', '1', 'yes', 'on']
        elif setting.setting_type == 'json':
            import json
            return json.loads(setting.setting_value)
        else:
            return setting.setting_value
    
    @classmethod
    def set_setting(cls, key, value, setting_type='string', description=None, category='general', updated_by=None):
        """Set a setting value"""
        setting = cls.query.filter_by(setting_key=key).first()
        
        # Convert value to string for storage
        if setting_type == 'json':
            import json
            value_str = json.dumps(value)
        else:
            value_str = str(value)
        
        if setting:
            setting.setting_value = value_str
            setting.setting_type = setting_type
            setting.updated_at = datetime.utcnow()
            setting.updated_by = updated_by
            if description:
                setting.description = description
            if category:
                setting.category = category
        else:
            setting = cls(
                setting_key=key,
                setting_value=value_str,
                setting_type=setting_type,
                description=description,
                category=category,
                updated_by=updated_by
            )
            db.session.add(setting)
        
        db.session.commit()
        return setting
    
    @classmethod
    def get_category_settings(cls, category):
        """Get all settings in a category"""
        return cls.query.filter_by(category=category).all()
    
    @classmethod
    def initialize_bot_detection_settings(cls):
        """Initialize default bot detection settings"""
        defaults = [
            # Adult bot detection settings
            {
                'key': 'bot_detection_adult_sensitivity',
                'value': 5,
                'type': 'integer',
                'description': 'Adult bot detection sensitivity (1-10, higher = stricter)',
                'category': 'bot_detection'
            },
            {
                'key': 'bot_detection_adult_threshold',
                'value': 0.6,
                'type': 'float',
                'description': 'Adult bot detection threshold (0.0-1.0)',
                'category': 'bot_detection'
            },
            # Teen bot detection settings
            {
                'key': 'bot_detection_teen_sensitivity',
                'value': 7,
                'type': 'integer',
                'description': 'Teen bot detection sensitivity (1-10, higher = stricter)',
                'category': 'bot_detection'
            },
            {
                'key': 'bot_detection_teen_threshold',
                'value': 0.4,
                'type': 'float',
                'description': 'Teen bot detection threshold (0.0-1.0)',
                'category': 'bot_detection'
            },
            # General settings
            {
                'key': 'bot_detection_enabled',
                'value': True,
                'type': 'boolean',
                'description': 'Enable bot detection system',
                'category': 'bot_detection'
            },
            {
                'key': 'bot_detection_log_level',
                'value': 'info',
                'type': 'string',
                'description': 'Bot detection logging level (debug, info, warning, error)',
                'category': 'bot_detection'
            }
        ]
        
        for default in defaults:
            existing = cls.query.filter_by(setting_key=default['key']).first()
            if not existing:
                cls.set_setting(
                    default['key'],
                    default['value'],
                    default['type'],
                    default['description'],
                    default['category']
                )


class AdminActivityLog(db.Model):
    """Log admin activities"""
    __tablename__ = 'admin_activity_log'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    target_type = db.Column(db.String(50))  # user, setting, data, etc.
    target_id = db.Column(db.String(100))
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    extra_data = db.Column(db.JSON)  # Renamed from metadata to avoid SQLAlchemy conflict
    
    admin = db.relationship('User', backref='admin_activities')
    
    def __repr__(self):
        return f'<AdminActivityLog {self.admin_id}:{self.action}>'
    
    @classmethod
    def log_activity(cls, admin_id, action, description=None, target_type=None, target_id=None, 
                    ip_address=None, user_agent=None, extra_data=None):
        """Log an admin activity"""
        log = cls(
            admin_id=admin_id,
            action=action,
            description=description,
            target_type=target_type,
            target_id=target_id,
            ip_address=ip_address,
            user_agent=user_agent,
            extra_data=extra_data
        )
        db.session.add(log)
        db.session.commit()
        return log