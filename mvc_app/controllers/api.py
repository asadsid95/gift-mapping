from datetime import datetime
from sqlite3 import IntegrityError
from typing import Literal

from flask import Blueprint, jsonify, request,session
from flask.wrappers import Response

from mvc_app.models import (Group, db, User, GiftPreference, Invitation, Event, GiftIdea)
from ..utils import send_email, is_group_member
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

        if not title:
            return jsonify({"status": "failed", "message": "Each gift preference must have a title."}), 400

        gift_preference = GiftPreference(
            user_id=new_user.id,
            title=title,
            price=price,
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


# must be authenticated
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


@api_bp.get('/group')
def list_groups():
    groups = Group.query.all()
    payload = [
        {
            'id': g.id,
            'name': g.name,
            'created_by': g.created_by,
            'created_at': _date_to_str(g.created_at),
            # How to get group memebers?
            'members': [
                {
                    'id': member.id,
                    'name': member.name,
                    'email': member.email
                }
                for member in g.members
            ]
        }
        for g in groups
    ]
    return jsonify(payload)


@api_bp.post('/group')
def create_group():
    body = request.get_json(silent=True) or {}
    name = body.get('name')
    member_emails = body.get('members', [])  # List of email addresses

    if not name:
        return jsonify({'error': 'Group name is required'}), 400

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User must be logged in to create a group'}), 401

    # Create the group
    group = Group(name=name, created_by=user_id)
    db.session.add(group)
    db.session.commit()

    # Process member emails
    for email in member_emails:
        user = User.query.filter_by(email=email).first()
        print(user)
        if user:
            # User exists, send invitation to accept
            send_email(
                to=email,
                subject="You've been invited to join a group",
                body=f"Click here to accept the invite: http://example.com/accept_invite?group_id={group.id}"
            )
            invitation = Invitation(group_id=group.id, email=email, status='pending')
            db.session.add(invitation)

            '''Review this: Should user be added to group while inivitation is pending?'''
              # Add user to the group
            group.members.append(user)

            # Create a birthday event for the next year
            next_birthday = user.birthday.replace(year=datetime.now().year + 1)
            event = Event(
                type="Birthday",
                date=next_birthday,
                group_id=group.id,
                user_id=user.id,
                status = "upcoming"
            )
            db.session.add(event)
        else:
            # User does not exist, send invitation to register
            send_email(
                to=email,
                subject="Join our platform to accept your group invitation",
                body=f"Click here to register: http://example.com/register?group_id={group.id}"
            )
            invitation = Invitation(group_id=group.id, email=email, status='pending')
            db.session.add(invitation)

    db.session.commit()

    return jsonify({'id': group.id, 'name': group.name, 'created_by': group.created_by}), 201


# TO REVIEW
@api_bp.get('/accept_invite')
def accept_invite():
    group_id = request.args.get('group_id')

    # This will need to be checked again
    email = session.get('email')  # Assume user is logged in and email is in session

    if not email:
        return jsonify({'error': 'User must be logged in to accept the invite'}), 401

    invitation = Invitation.query.filter_by(group_id=group_id, email=email, status='pending').first()
    if not invitation:
        return jsonify({'error': 'Invalid or expired invitation'}), 400

    user = User.query.filter_by(email=email).first()
    group = Group.query.get(group_id)
    group.members.append(user)

    invitation.status = 'accepted'
    invitation.responded_at = db.func.current_timestamp()
    db.session.commit()

    return jsonify({'message': 'Invitation accepted successfully'}), 200

# TO REVIEW
@api_bp.get('/decline_invite')
def decline_invite():
    group_id = request.args.get('group_id')

    # This will need to be checked again
    email = session.get('email')  # Assume user is logged in and email is in session

    if not email:
        return jsonify({'error': 'User must be logged in to decline the invite'}), 401

    invitation = Invitation.query.filter_by(group_id=group_id, email=email, status='pending').first()
    if not invitation:
        return jsonify({'error': 'Invalid or expired invitation'}), 400

    invitation.status = 'declined'
    invitation.responded_at = db.func.current_timestamp()
    db.session.commit()

    return jsonify({'message': 'Invitation declined successfully'}), 200

############## EVENTS ################

@api_bp.get('/groups/<int:group_id>/events')
def get_upcoming_events(group_id):
    group = Group.query.get(group_id)
    if not group:
        return jsonify({'error': 'Group not found'}), 404

    today = datetime.now().date()
    events = Event.query.filter(Event.group_id == group_id, Event.date >= today).all()

    payload = [
        {
            'id': event.id,
            'type': event.type,
            'date': event.date.isoformat(),
            'group_id': event.group_id,
            'user_id': event.user_id,
            'remaining_days': (event.date - today).days,
            'min_budget': event.min_budget,
            'max_budget': event.max_budget,
            'reminder_date': event.reminder_date,
            'status': event.status
        }
        for event in events
    ]
    return jsonify(payload)

@api_bp.patch('/events/<int:event_id>')
def update_event(event_id):
    body = request.get_json(silent=True) or {}
    min_budget = body.get('min_budget')
    max_budget = body.get('max_budget')
    status = body.get('status')

    event = Event.query.get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404

    if min_budget is not None:
        event.min_budget = min_budget
    if max_budget is not None:
        event.max_budget = max_budget

    # Update status if provided
    if status is not None:
        if status not in ['upcoming', 'completed', 'cancelled']:
            return jsonify({'error': 'Invalid status value'}), 400
        event.status = status

    db.session.commit()
    return jsonify({'message': 'Event updated successfully'})

######################### GIFT IDEAS ################################

@api_bp.post('/events/<int:event_id>/gift-ideas')
def create_gift_idea(event_id):
    data = request.get_json(silent=True) or {}
    print(data)
    user_id = data.get('user_id')
    title = data.get('title')
    description = data.get('description')
    estimated_cost = data.get('estimated_cost')

    # Validate event existence
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404

    # Validate user is a group member
    if not is_group_member(user_id, event.group_id):
        
        return jsonify({'error': 'User is not a member of the group'}), 403

    # Validate estimated_cost
    if estimated_cost is not None and estimated_cost < 0:
        return jsonify({'error': 'Estimated cost must be non-negative'}), 400

    # Create gift idea
    gift_idea = GiftIdea(
        event_id=event_id,
        user_id=user_id,
        title=title,
        description=description,
        estimated_cost=estimated_cost
    )
    db.session.add(gift_idea)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Failed to create gift idea'}), 500

    return jsonify({'message': 'Gift idea created successfully', 'gift_idea': gift_idea.id}), 201

# GET /api/events/<event_id>/gift-ideas
@api_bp.route('/events/<int:event_id>/gift-ideas', methods=['GET'])
def get_gift_ideas(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404

    gift_ideas = GiftIdea.query.filter_by(event_id=event_id).all()
    return jsonify([{
        'id': idea.id,
        'title': idea.title,
        'description': idea.description,
        'estimated_cost': idea.estimated_cost,
        'user_id': idea.user_id
    } for idea in gift_ideas]), 200

# @api_bp.get('/gifts')
# def list_gifts():
#     gifts = GiftIdea.query.all()
#     payload = [
#         {
#             'id': g.id,
#             'event_id': g.event_id,
#             'title': g.title,
#             'description': g.description,
#             'estimated_cost': g.estimated_cost,
#         }
#         for g in gifts
#     ]
#     return jsonify(payload)


# @api_bp.post('/gifts')
# def create_gift():
#     body = request.get_json(silent=True) or {}
#     required = ['event_id', 'title']
#     missing = [field for field in required if not body.get(field)]
#     if missing:
#         return jsonify({'error': f"missing fields: {', '.join(missing)}"}), 400

#     gift = GiftIdea(
#         event_id=body['event_id'],
#         title=body['title'],
#         description=body.get('description'),
#         estimated_cost=body.get('estimated_cost'),
#     )
#     db.session.add(gift)
#     db.session.commit()

#     return (
#         jsonify(
#             {
#                 'id': gift.id,
#                 'event_id': gift.event_id,
#                 'title': gift.title,
#                 'description': gift.description,
#                 'estimated_cost': gift.estimated_cost,
#             }
#         ),
#         201,
#     )


