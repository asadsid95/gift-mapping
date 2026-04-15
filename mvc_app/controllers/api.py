from datetime import datetime

from flask import Blueprint, jsonify, request

from mvc_app.models import Event, GiftIdea, Recipient, db, User


api_bp = Blueprint('api', __name__, url_prefix='/api')


def _date_to_str(value):
    return value.isoformat() if value else None


def _parse_date(raw_value):
    return datetime.strptime(raw_value, '%Y-%m-%d').date()


@api_bp.get('/health')
def health():
    return jsonify({'status': 'ok'})


@api_bp.get('/recipients')
def list_recipients():
    recipients = Recipient.query.all()
    payload = [
        {
            'id': r.id,
            'name': r.name,
            'relationship': r.relationship,
            'preferences': r.preferences,
            'restrictions': r.restrictions,
        }
        for r in recipients
    ]
    return jsonify(payload)


@api_bp.post('/recipients')
def create_recipient():
    body = request.get_json(silent=True) or {}
    if not body.get('name'):
        return jsonify({'error': 'name is required'}), 400

    recipient = Recipient(
        name=body['name'],
        relationship=body.get('relationship'),
        preferences=body.get('preferences'),
        restrictions=body.get('restrictions'),
    )
    db.session.add(recipient)
    db.session.commit()

    return (
        jsonify(
            {
                'id': recipient.id,
                'name': recipient.name,
                'relationship': recipient.relationship,
                'preferences': recipient.preferences,
                'restrictions': recipient.restrictions,
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
