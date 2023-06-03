import unittest
from flask import current_app, Flask
from project import create_app, db
from project.models import User
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)

class TestWebApp(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['WTF_CSRF_ENABLED'] = False  # no CSRF during tests
        self.appctx = self.app.app_context()
        self.appctx.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.drop_all()
        self.appctx.pop()
        self.app = None
        self.appctx = None
        self.client = None

    def test_app(self):
        assert self.app is not None
        assert current_app == self.app

    def test_homepage_redirect(self):
        response = self.client.get('/', follow_redirects = True)
        assert response.status_code == 200

    def test_registration_form(self):
        response = self.client.get('/signup')
        assert response.status_code == 200

    def test_login_form(self):
        response = self.client.get('/login')
        assert response.status_code == 200

    def test_no_access_to_profile(self):
        response = self.client.get('/profile', follow_redirects = True)
        assert response.status_code == 200
        assert response.request.path == '/login'

    def test_register_user(self):
        response = self.client.post('/signup', data = {
            'email' : 'user@test.com',
            'name' : 'Test',
            'password' : 'test123'
        }, follow_redirects = True)
        assert response.status_code == 200
        # should redirect to the login page
        assert response.request.path == '/login'
        response = self.client.post('/login', data = {
            'email' : 'user@test.com',
            'password' : 'test123'
        }, follow_redirects = True)
        assert response.status_code == 200
        response = self.client.get('/profile', follow_redirects = True)
        html = response.get_data(as_text = True)
        assert 'Test' in html

    def test_hashed_passwords(self):
        response = self.client.post('/signup', data = {
            'email' : 'user@test.com',
            'name' : 'test user',
            'password' : 'test123'
        }, follow_redirects = True)
        assert response.status_code == 200
        # should redirect to the login page
        assert response.request.path == '/login'

        user = User.query.filter_by(email='user@test.com').first()
        assert user is not None
        assert bcrypt.check_password_hash(user.password, 'test123')

    def test_sql_injection(self):
        response = self.client.post('/signup', data = {
            'email' : 'user@test.com"; drop table user; -- ',
            'name' : 'test user',
            'password' : 'test123'
        }, follow_redirects = True)
        assert response.status_code == 200 

    def test_create_restaurant_as_public(self):
        response = self.client.get('/restaurant/new/', follow_redirects = True)
        assert response.status_code == 200
        assert response.request.path == '/login'

    def test_create_restaurant_as_owner(self):
        self.client.post('/signup', data = {
            'email' : 'user@test.com',
            'name' : 'test user',
            'password' : 'test123'
        }, follow_redirects = True)
        self.client.post('/login', data = {
            'email' : 'user@test.com',
            'password' : 'test123'
        }, follow_redirects = True)
        response = self.client.get('/restaurant/new/', follow_redirects = True)
        assert response.status_code == 200
        assert response.request.path == '/restaurant/new/'


