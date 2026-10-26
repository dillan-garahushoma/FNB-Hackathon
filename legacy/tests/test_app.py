import os
import re
import sqlite3
import tempfile
import unittest
import uuid
from contextlib import closing

from werkzeug.security import check_password_hash

from app import create_app


class Path2WorkAppTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database = os.path.join(self.temp_dir.name, 'test.sqlite3')
        self.app = create_app({
            'TESTING': True,
            'SECRET_KEY': 'test-secret',
            'DATABASE': self.database,
        })
        self.client = self.app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def csrf_token(self, endpoint):
        response = self.client.get(endpoint)
        self.assertEqual(response.status_code, 200)
        match = re.search(rb'name="csrf_token" value="([^"]+)"', response.get_data())
        self.assertIsNotNone(match)
        return match.group(1).decode()

    def register(self, email='aisha@example.org', password='strongpass8'):
        token = self.csrf_token('/register')
        return self.client.post(
            '/register',
            data={
                'csrf_token': token,
                'full_name': 'Aisha Ndlovu',
                'email': email,
                'password': password,
            },
            follow_redirects=False,
        )

    def post_onboarding(self, step, data):
        token = self.csrf_token(f'/onboarding/{step}')
        return self.client.post(
            f'/onboarding/{step}',
            data={**data, 'csrf_token': token},
            follow_redirects=False,
        )

    def test_public_pages_and_local_assets_are_available(self):
        for path in ('/', '/register', '/opportunities', '/signin'):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200)

        home = self.client.get('/')
        self.assertIn(b'Real skills. Meaningful opportunities.', home.data)
        for asset in ('path2work-logo.png', 'home-hero.jpg', 'signup-male.jpg'):
            response = self.client.get(f'/static/assets/{asset}')
            self.assertEqual(response.status_code, 200)
            response.close()
        self.assertIn(b'No opportunities listed yet', self.client.get('/opportunities').data)

    def test_registration_rejects_invalid_fields_and_csrf(self):
        token = self.csrf_token('/register')
        response = self.client.post(
            '/register',
            data={
                'csrf_token': token,
                'full_name': '',
                'email': 'bad',
                'password': 'short',
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Enter your full name.', response.data)

        response = self.client.post(
            '/register',
            data={
                'csrf_token': token,
                'full_name': 'Aisha',
                'email': 'aisha@example.org',
                'password': 'short',
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Use at least 8 characters', response.data)

    def test_registration_hashes_password_and_signs_user_in(self):
        response = self.register()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], '/onboarding/1')
        with self.client.session_transaction() as session:
            self.assertIn('user_id', session)

        with closing(sqlite3.connect(self.database)) as database:
            password_hash = database.execute(
                'SELECT password_hash FROM users WHERE email = ?',
                ('aisha@example.org',),
            ).fetchone()[0]
        self.assertNotEqual(password_hash, 'strongpass8')
        self.assertTrue(check_password_hash(password_hash, 'strongpass8'))
        self.assertIn(b'Your account is ready.', self.client.get('/').data)

    def test_registration_rejects_duplicate_email_case_insensitively(self):
        self.assertEqual(self.register().status_code, 302)
        response = self.register(email='AISHA@example.org')
        self.assertEqual(response.status_code, 409)
        self.assertIn(b'An account with this email already exists.', response.data)

    def test_sign_in_and_sign_out(self):
        self.assertEqual(self.register().status_code, 302)
        self.client.post('/signout', data={'csrf_token': self.csrf_token('/')}, follow_redirects=True)
        with self.client.session_transaction() as session:
            self.assertNotIn('user_id', session)

        token = self.csrf_token('/signin')
        response = self.client.post(
            '/signin',
            data={
                'csrf_token': token,
                'email': 'aisha@example.org',
                'password': 'strongpass8',
            },
        )
        self.assertEqual(response.status_code, 302)
        with self.client.session_transaction() as session:
            self.assertIn('user_id', session)

        bad_token = self.csrf_token('/signin')
        response = self.client.post(
            '/signin',
            data={
                'csrf_token': bad_token,
                'email': 'aisha@example.org',
                'password': 'incorrect',
            },
        )
        self.assertEqual(response.status_code, 401)
        self.assertIn(b'Email or password is incorrect', response.data)

    def test_registration_starts_and_persists_the_complete_onboarding_flow(self):
        response = self.register()
        self.assertEqual(response.headers['Location'], '/onboarding/1')

        response = self.post_onboarding(1, {'career_goal': 'FIRST_JOB'})
        self.assertEqual(response.headers['Location'], '/onboarding/2')

        response = self.post_onboarding(2, {
            'career_fields': ['Information Technology', 'Design & Creative'],
            'preferred_roles': ['Software Developer', 'Web Designer'],
        })
        self.assertEqual(response.headers['Location'], '/onboarding/3')

        response = self.post_onboarding(3, {
            'preferred_locations': ['Johannesburg', 'Cape Town'],
            'work_arrangement': 'Hybrid',
            'availability': 'Immediately',
            'opportunity_types': ['Jobs', 'Internships'],
        })
        self.assertEqual(response.headers['Location'], '/onboarding/4')
        self.assertIn(b'Review your profile', self.client.get('/onboarding/4').data)

        response = self.client.post(
            '/onboarding/complete',
            data={'csrf_token': self.csrf_token('/onboarding/4')},
            follow_redirects=False,
        )
        self.assertEqual(response.headers['Location'], '/')

        with closing(sqlite3.connect(self.database)) as database:
            user = database.execute(
                'SELECT career_goal, career_fields, preferred_roles, preferred_locations, '
                'work_arrangement, availability, opportunity_types, onboarding_completed '
                'FROM users WHERE email = ?',
                ('aisha@example.org',),
            ).fetchone()
        self.assertEqual(user[0], 'FIRST_JOB')
        self.assertEqual(user[1], '["Information Technology", "Design & Creative"]')
        self.assertEqual(user[2], '["Software Developer", "Web Designer"]')
        self.assertEqual(user[3], '["Johannesburg", "Cape Town"]')
        self.assertEqual(user[4:7], ('Hybrid', 'Immediately', '["Jobs", "Internships"]'))
        self.assertEqual(user[7], 1)

    def test_sign_in_resumes_at_the_first_incomplete_onboarding_step(self):
        self.assertEqual(self.register().headers['Location'], '/onboarding/1')
        self.assertEqual(
            self.post_onboarding(1, {'career_goal': 'BUILD_SKILLS'}).headers['Location'],
            '/onboarding/2',
        )
        self.client.post(
            '/signout',
            data={'csrf_token': self.csrf_token('/')},
            follow_redirects=False,
        )

        token = self.csrf_token('/signin')
        response = self.client.post(
            '/signin',
            data={
                'csrf_token': token,
                'email': 'aisha@example.org',
                'password': 'strongpass8',
            },
        )
        self.assertEqual(response.headers['Location'], '/onboarding/2')

    def test_onboarding_rejects_more_than_three_roles(self):
        self.assertEqual(self.register().headers['Location'], '/onboarding/1')
        self.post_onboarding(1, {'career_goal': 'FIRST_JOB'})

        response = self.post_onboarding(2, {
            'career_fields': ['Information Technology'],
            'preferred_roles': ['Software Developer', 'IT Support', 'Data Analyst', 'Other'],
            'other_role': 'Product manager',
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Choose no more than three roles.', response.data)

    def test_missing_csrf_token_is_rejected(self):
        response = self.client.post(
            '/register',
            data={
                'full_name': 'Aisha',
                'email': 'aisha@example.org',
                'password': 'strongpass8',
            },
        )
        self.assertEqual(response.status_code, 400)
        with closing(sqlite3.connect(self.database)) as database:
            count = database.execute('SELECT count(*) FROM users').fetchone()[0]
        self.assertEqual(count, 0)


if __name__ == '__main__':
    unittest.main()
