from datetime import datetime
from typing import Literal

from flask import Blueprint, jsonify, request,session
from flask.wrappers import Response

from mvc_app.models import (Event, GiftIdea, Group, Recipient, db, User, GiftPreference)
from werkzeug.security import check_password_hash, generate_password_hash



api_bp = Blueprint('api', __name__, url_prefix='/api')


def _date_to_str(value):
    return value.isoformat() if value else None


def _parse_date(raw_value):
    return datetime.strptime(raw_value, '%Y-%m-%d').date()


@api_bp.get('/health')
def health():
    return jsonify({'status': 'ok'})

@api_bp.post('/register')
def register() -> tuple[Response, Literal[400]] | tuple[Response, Literal[500]] | tuple[Response, Literal[201]]:

  
    body = request.get_json(silent=True) or {}

    name = body.get('name')
    email = body.get('email')
    password = body.get('password')
    birthday = body.get('birthday')  # Added birthday field
    gift_preferences = body.get('gift_preferences', [])  # List of gift preferences

    if not name or not email or not password or not birthday:
        return jsonify({"status": "failed", "message": "Name, email, password, and birthday are required."}), 400

    # Check if the email already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"status": "failed", "message": "Email already registered!!"}), 500

    # Add the new user to the database
    hashed_password = generate_password_hash(password)
    new_user = User(name=name, email=email, password=hashed_password, birthday=_parse_date(birthday))
    db.session.add(new_user)
    db.session.commit()

    # Add gift preferences if provided
    for preference in gift_preferences:
        title = preference.get('title')
        price = preference.get('price')
        metadata = preference.get('metadata', {})

        if not title:
            return jsonify({"status": "failed", "message": "Each gift preference must have a title."}), 400

        gift_preference = GiftPreference(
            user_id=new_user.id,
            title=title,
            price=price,
            metadata=metadata
        )
        db.session.add(gift_preference)

    db.session.commit()

    return jsonify({"status": "success", "message": "User registered successfully."}), 201
    
@api_bp.post("/login")
def login():
    body = request.get_json(silent=True) or {}

    email = body.get('email')
    password = body.get('password')

    if not email or not password:
        return jsonify({"status": "failed", "message": "Email, and password are required."}), 400

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        # print("login passed")
        session['user_id'] = user.id
        return jsonify({"message": 'Successful login'}), 200
    else:
        return jsonify({"message": 'Invalid credentials.'}), 500

@api_bp.get('/users')
def list_users():
    users = User.query.all()
    payload = [
        {
            'id': u.id,
            'email': u.email,
            'name': u.name
            # 'username': u.username,
            # 'created_at': u.created_at.isoformat() if u.created_at else None
        }
        for u in users
    ]
    return jsonify(payload)


@api_bp.get('/groups')
def list_groups():
    groups = Group.query.all()
    payload = [
        {
            'id': g.id,
            'name': g.name,
            'created_by': g.created_by,
            'created_at': _date_to_str(g.created_at),
            # How to get group memebers?
        }
        for g in groups
    ]
    return jsonify(payload)


@api_bp.post('/group')
def create_group():
    body = request.get_json(silent=True) or {}
    name = body.get('name')
    member_ids = body.get('members', [])  # List of user IDs to add as members

    print(body)

    if not name:
        return jsonify({'error': 'Group name is required'}), 400

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User must be logged in to create a group'}), 401


    # Validate member IDs
    valid_members = User.query.filter(User.id.in_(member_ids)).all()
    if len(valid_members) != len(member_ids):
        return jsonify({'error': 'Some user IDs are invalid'}), 400

    group = Group(name=name, created_by=user_id)
    db.session.add(group)
    db.session.commit()


    # Add members to the group
    for member in valid_members:
        group.members.append(member)

    # Add the creator as a member (optional, if not already included)
    creator = User.query.get(user_id)
    if creator not in group.members:
        group.members.append(creator)

    db.session.commit()

    return (
        jsonify(
            {
                'id': group.id,
                'name': group.name,
                'created_by': group.created_by,
                'created_at': _date_to_str(group.created_at),
                'members': [{'id': m.id, 'name': m.name, 'email': m.email} for m in group.members],

            }
        ),
        201,
    )



@api_bp.get('/events')
def list_events():
    events = Event.query.all()
    payload = [
        {
            'id': e.id,
            'recipient_id': e.recipient_id,
            'type': e.type,
            'date': _date_to_str(e.date),
            'group_id': e.group_id,
            'min_budget': e.min_budget,
            'max_budget': e.max_budget,
            'reminder_date': _date_to_str(e.reminder_date),
        }
        for e in events
    ]
    return jsonify(payload)


@api_bp.post('/events')
def create_event():
    body = request.get_json(silent=True) or {}
    required = ['recipient_id', 'type', 'date', 'group_id']
    missing = [field for field in required if not body.get(field)]
    if missing:
        return jsonify({'error': f"missing fields: {', '.join(missing)}"}), 400

    event = Event(
        recipient_id=body['recipient_id'],
        type=body['type'],
        date=_parse_date(body['date']),
        group_id=body['group_id'],
        min_budget=body.get('min_budget'),
        max_budget=body.get('max_budget'),
        reminder_date=_parse_date(body['reminder_date']) if body.get('reminder_date') else None,
    )
    db.session.add(event)
    db.session.commit()

    return (
        jsonify(
            {
                'id': event.id,
                'recipient_id': event.recipient_id,
                'type': event.type,
                'date': _date_to_str(event.date),
                'group_id': event.group_id,
                'min_budget': event.min_budget,
                'max_budget': event.max_budget,
                'reminder_date': _date_to_str(event.reminder_date),
            }
        ),
        201,
    )


@api_bp.get('/gifts')
def list_gifts():
    gifts = GiftIdea.query.all()
    payload = [
        {
            'id': g.id,
            'event_id': g.event_id,
            'title': g.title,
            'description': g.description,
            'estimated_cost': g.estimated_cost,
        }
        for g in gifts
    ]
    return jsonify(payload)


@api_bp.post('/gifts')
def create_gift():
    body = request.get_json(silent=True) or {}
    required = ['event_id', 'title']
    missing = [field for field in required if not body.get(field)]
    if missing:
        return jsonify({'error': f"missing fields: {', '.join(missing)}"}), 400

    gift = GiftIdea(
        event_id=body['event_id'],
        title=body['title'],
        description=body.get('description'),
        estimated_cost=body.get('estimated_cost'),
    )
    db.session.add(gift)
    db.session.commit()

    return (
        jsonify(
            {
                'id': gift.id,
                'event_id': gift.event_id,
                'title': gift.title,
                'description': gift.description,
                'estimated_cost': gift.estimated_cost,
            }
        ),
        201,
    )


