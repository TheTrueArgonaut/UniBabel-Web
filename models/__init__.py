from flask_sqlalchemy import SQLAlchemy

# Initialize the database instance
db = SQLAlchemy()

# Import all models from their respective microservices
from .user_models import (
    User, UserCommonPhrase, UserType, 
    Room, RoomType, RoomMember, RoomMemberRole, RoomPermission,
    RoomRolePermissions, RoomSettings, RoomChannel,
    FriendGroup, FriendGroupType, FriendGroupMember, FriendGroupRole,
    UserFriend
)
from .chat_models import Chat, ChatParticipant, Message, TranslatedMessage
from .subscription_models import UsageLog, DataHarvestingProfile, ConversationIntelligence, DataSalesRecord, ManipulationCampaign
from .safety_models import UserReport, FriendRequest
from .babel_models import BabelPost, BabelLike, BabelComment, BabelFollow, BabelPostType
from .translation_models import Translation, TranslationSubmission, TranslationCache

# Create database tables
def create_tables():
    db.create_all()

# Export everything for easy importing
__all__ = [
    'db',
    'User', 'UserCommonPhrase', 'UserType', 
    'Room', 'RoomType', 'RoomMember', 'RoomMemberRole', 'RoomPermission',
    'RoomRolePermissions', 'RoomSettings', 'RoomChannel',
    'FriendGroup', 'FriendGroupType', 'FriendGroupMember', 'FriendGroupRole',
    'UserFriend',
    'Chat', 'ChatParticipant', 'Message', 'TranslatedMessage',
    'UsageLog', 'DataHarvestingProfile', 'ConversationIntelligence', 'DataSalesRecord', 'ManipulationCampaign',
    'UserReport', 'FriendRequest',
    'BabelPost', 'BabelLike', 'BabelComment', 'BabelFollow', 'BabelPostType',
    'Translation', 'TranslationSubmission', 'TranslationCache',
    'create_tables'
]