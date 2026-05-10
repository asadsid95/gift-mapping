from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


user_group = db.Table(
    'user_group',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True),
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    birthday = db.Column(db.Date, nullable=False)  # Added birthday field
    groups = db.relationship('Group', secondary=user_group, back_populates='members')
    gift_preferences = db.relationship('GiftPreference', back_populates='user', cascade='all, delete-orphan')
    gift_ideas = db.relationship('GiftIdea', back_populates='user', cascade='all, delete-orphan')
    votes = db.relationship('Vote', back_populates='user', cascade='all, delete-orphan')

class GiftPreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=True)

    # Relationship to User
    user = db.relationship('User', back_populates='gift_preferences')

class GiftIdea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)  # Link to the event
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # User who proposed the idea
    title = db.Column(db.String(100), nullable=False)  # Gift idea title
    description = db.Column(db.String(200))  # Optional description
    estimated_cost = db.Column(db.Float)  # Estimated cost of the gift

    votes = db.relationship('Vote', back_populates='gift_idea', cascade='all, delete-orphan')  # Votes for the idea

    # Relationships
    event = db.relationship('Event', back_populates='gift_ideas')
    user = db.relationship('User', back_populates='gift_ideas')

class Vote(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)  # User who voted
    gift_idea_id = db.Column(db.Integer, db.ForeignKey('gift_idea.id'), primary_key=True)  # Gift idea being voted on
    score = db.Column(db.Integer, nullable=False)  # Voting score (e.g., 1 for upvote, -1 for downvote)

    # Relationships
    user = db.relationship('User', back_populates='votes')
    gift_idea = db.relationship('GiftIdea', back_populates='votes')
 
class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    4members = db.relationship('User', secondary=user_group, back_populates='groups')

class Invitation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')  # pending, accepted, declined
    sent_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    responded_at = db.Column(db.DateTime)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # This is of the user the event belongs to
    min_budget = db.Column(db.Float)
    max_budget = db.Column(db.Float)
    reminder_date = db.Column(db.Date)
    status = db.Column(db.String(100), nullable=True) # i.e. upcoming, completed, cancelled
    user = db.relationship('User')
    gift_ideas = db.relationship('GiftIdea', back_populates='event', cascade='all, delete-orphan')
