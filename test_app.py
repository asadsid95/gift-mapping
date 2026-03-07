import unittest
from app import app, db
from app import User, Group, Event, Recipient, GiftIdea, GiftRecord
from werkzeug.security import generate_password_hash

class AppTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_home_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 302)

    def test_register_user(self):
        response = self.app.post('/register', data={
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after registration

    def test_login_user(self):
        with app.app_context():
            user = User(
                name='Test User',
                email='test@example.com',
                password=generate_password_hash('password123')
            )
            db.session.add(user)
            db.session.commit()

        response = self.app.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login

if __name__ == '__main__':
    unittest.main()
