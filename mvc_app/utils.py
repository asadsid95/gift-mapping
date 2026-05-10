from mvc_app.models import Group

def send_email(to, subject, body):
    # Use an email-sending library like Flask-Mail or an external service like SendGrid
    print(f"Sending email to {to}: {subject}\n{body}")

# Helper function to check if a user is a group member
def is_group_member(user_id, group_id):
    group = Group.query.filter_by(id=group_id).first()
  
    if group and any(member.id == user_id for member in group.members):
        return True
    return False