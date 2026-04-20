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

class GiftPreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=True)

    # Relationship to User
    user = db.relationship('User', back_populates='gift_preferences')

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    members = db.relationship('User', secondary=user_group, back_populates='groups')


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('recipient.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    min_budget = db.Column(db.Float)
    max_budget = db.Column(db.Float)
    reminder_date = db.Column(db.Date)


class GiftIdea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    estimated_cost = db.Column(db.Float)


class Vote(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    gift_idea_id = db.Column(db.Integer, db.ForeignKey('gift_idea.id'), primary_key=True)
    score = db.Column(db.Integer, nullable=False)


class Contribution(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False)


class GiftRecord(db.Model):
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), primary_key=True)
    final_gift = db.Column(db.String(100), nullable=False)
    contributors = db.Column(db.String(200))
    total_cost = db.Column(db.Float)
    date_completed = db.Column(db.Date)
