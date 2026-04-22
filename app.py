from mvc_app import create_app
from mvc_app.models import  Group, User, db


app = create_app()


__all__ = [
    'app',
    'db',
    'User',
    'Group',
    # 'Event',
    # 'GiftIdea',
    # 'Vote',
    # 'Contribution',
    # 'GiftRecord',
]
