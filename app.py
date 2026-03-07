from mvc_app import create_app
from mvc_app.models import Contribution, Event, GiftIdea, GiftRecord, Group, Recipient, User, Vote, db


app = create_app()


__all__ = [
    'app',
    'db',
    'User',
    'Group',
    'Recipient',
    'Event',
    'GiftIdea',
    'Vote',
    'Contribution',
    'GiftRecord',
]
