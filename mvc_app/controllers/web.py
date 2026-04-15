from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, session, url_for, get_flashed_messages

from flask_cors import cross_origin

from werkzeug.security import check_password_hash, generate_password_hash

from mvc_app.models import Event, GiftIdea, GiftRecord, Group, Recipient, User, Vote, db


web_bp = Blueprint('web', __name__)


def _parse_date(raw_value):
    return datetime.strptime(raw_value, '%Y-%m-%d').date()


@web_bp.route('/')
def home():
    current_date = datetime.now()
    # print(request.headers)
    print("X-Request-ID:::: ", request.headers.get("X-Request-ID"))
    return render_template('index.html', current_date=current_date)


@web_bp.route('/dashboard')
def dashboard():
    upcoming_events = Event.query.filter(Event.date >= datetime.now().date()).all()
    recent_gift_history = GiftRecord.query.order_by(GiftRecord.date_completed.desc()).limit(5).all()
    all_groups = Group.query.all()

    return render_template(
        'dashboard.html',
        upcoming_events=upcoming_events,
        recent_gift_history=recent_gift_history,
        all_groups=all_groups,
    )


@web_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        if User.query.filter_by(email=email).first():
            flash('Email already registered.')
            return redirect(url_for('web.register'))

        db.session.add(User(name=name, email=email, password=password))
        db.session.commit()
        flash('Registration successful. Please log in.')
        return redirect(url_for('web.login'))

    return render_template('register.html')


@web_bp.route('/login', methods=['GET', 'POST'])
@cross_origin()
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful.')
            return redirect(url_for('web.dashboard'))

        flash('Invalid email or password.')

    return render_template('login.html')


@web_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully.')
    return redirect(url_for('web.login'))

@web_bp.route('/events', methods=['GET', 'POST'])
def events():
    if request.method == 'POST':
        new_event = Event(
            recipient_id=request.form['recipient_id'],
            type=request.form['type'],
            date=_parse_date(request.form['date']),
            group_id=request.form['group_id'],
        )
        db.session.add(new_event)
        db.session.commit()
        return redirect(url_for('web.events'))

    all_events = Event.query.all()
    return render_template('events.html', events=all_events)


@web_bp.route('/recipients', methods=['GET', 'POST'])
def recipients():
    if request.method == 'POST':
        new_recipient = Recipient(
            name=request.form['name'],
            relationship=request.form['relationship'],
            preferences=request.form['preferences'],
            restrictions=request.form['restrictions'],
        )
        db.session.add(new_recipient)
        db.session.commit()
        return redirect(url_for('web.recipients'))

    all_recipients = Recipient.query.all()
    return render_template('recipients.html', recipients=all_recipients)


@web_bp.route('/recipients/<int:recipient_id>', methods=['GET', 'POST'])
def manage_recipient(recipient_id):
    recipient = Recipient.query.get_or_404(recipient_id)

    if request.method == 'POST':
        recipient.preferences = request.form['preferences']
        recipient.restrictions = request.form['restrictions']
        db.session.commit()
        return redirect(url_for('web.recipients'))

    return render_template('manage_recipient.html', recipient=recipient)


@web_bp.route('/gifts', methods=['GET', 'POST'])
def gifts():
    if request.method == 'POST':
        new_gift = GiftIdea(
            event_id=request.form['event_id'],
            title=request.form['title'],
            description=request.form['description'],
            estimated_cost=request.form['estimated_cost'],
        )
        db.session.add(new_gift)
        db.session.commit()
        return redirect(url_for('web.gifts'))

    all_gifts = GiftIdea.query.all()
    gift_scores = {
        gift.id: sum(v.score for v in Vote.query.filter_by(gift_idea_id=gift.id).all())
        for gift in all_gifts
    }
    return render_template('gifts.html', gifts=all_gifts, gift_scores=gift_scores)


@web_bp.route('/gifts/vote', methods=['POST'])
def vote():
    user_id = request.form['user_id']
    gift_idea_id = request.form['gift_idea_id']
    score = request.form['score']

    existing_vote = Vote.query.filter_by(user_id=user_id, gift_idea_id=gift_idea_id).first()
    if existing_vote:
        existing_vote.score = score
    else:
        db.session.add(Vote(user_id=user_id, gift_idea_id=gift_idea_id, score=score))

    db.session.commit()
    return redirect(url_for('web.gifts'))


@web_bp.route('/history', methods=['GET'])
def history():
    all_gift_records = GiftRecord.query.all()
    return render_template('history.html', gift_records=all_gift_records)


@web_bp.route('/events/budget', methods=['POST'])
def set_budget():
    event = Event.query.get(request.form['event_id'])
    if event:
        event.min_budget = request.form['min_budget']
        event.max_budget = request.form['max_budget']
        db.session.commit()
    return redirect(url_for('web.events'))


@web_bp.route('/events/complete', methods=['POST'])
def complete_event():
    gift_record = GiftRecord(
        event_id=request.form['event_id'],
        final_gift=request.form['final_gift'],
        contributors=request.form['contributors'],
        total_cost=request.form['total_cost'],
        date_completed=datetime.now().date(),
    )
    db.session.add(gift_record)
    db.session.commit()
    return redirect(url_for('web.history'))


@web_bp.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'POST':
        password = request.form.get('password') or generate_password_hash('changeme123')
        db.session.add(User(name=request.form['name'], email=request.form['email'], password=password))
        db.session.commit()
        return redirect(url_for('web.users'))

    all_users = User.query.all()
    return render_template('users.html', users=all_users)


@web_bp.route('/users/update/<int:user_id>', methods=['POST'])
def update_user(user_id):
    user = User.query.get(user_id)
    if user:
        user.name = request.form['name']
        user.email = request.form['email']
        db.session.commit()
    return redirect(url_for('web.users'))


@web_bp.route('/groups', methods=['GET', 'POST'])
def groups():
    if request.method == 'POST':
        db.session.add(Group(name=request.form['name']))
        db.session.commit()
        return redirect(url_for('web.groups'))

    all_groups = Group.query.all()
    return render_template('groups.html', groups=all_groups)


@web_bp.route('/groups/<int:group_id>/add_member', methods=['POST'])
def add_member(group_id):
    group = Group.query.get(group_id)
    user = User.query.get(request.form['user_id'])

    if group and user and user not in group.members:
        group.members.append(user)
        db.session.commit()
    return redirect(url_for('web.groups'))


@web_bp.route('/groups/<int:group_id>/remove_member', methods=['POST'])
def remove_member(group_id):
    group = Group.query.get(group_id)
    user = User.query.get(request.form['user_id'])

    if group and user and user in group.members:
        group.members.remove(user)
        db.session.commit()
    return redirect(url_for('web.groups'))


@web_bp.route('/reminders', methods=['GET', 'POST'])
def reminders():
    if request.method == 'POST':
        event = Event.query.get(request.form['event_id'])
        if event:
            event.reminder_date = _parse_date(request.form['reminder_date'])
            db.session.commit()
        return redirect(url_for('web.reminders'))

    all_events = Event.query.all()
    return render_template('reminders.html', events=all_events)

