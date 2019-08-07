import json

from django.core.management import call_command
from django.test import Client
from django.test import TestCase


class ApiTests(TestCase):
    def setUp(self) -> None:
        self.c = Client()

    def test_create_person(self):
        person = """{"username": "test1", "person_type": 1}"""
        response = self.c.post('/api/person/', person, content_type='application/json')

        content = response.content.decode()
        expected = {'success': True}

        result_content = json.loads(content)
        self.assertJSONEqual(json.dumps(result_content), json.dumps(expected))

    def test_duplicate_person(self):
        person = """{"username": "test1", "person_type": 1}"""

        self.c.post('/api/person/', person, content_type='application/json')
        response = self.c.post('/api/person/', person, content_type='application/json')

        content = response.content.decode()
        expected = {'message': 'This person already exists', 'success': False}

        result_content = json.loads(content)
        self.assertJSONEqual(json.dumps(result_content), json.dumps(expected))

    def test_long_username(self):
        person = """{"username": "thisisalongusernamewicheexceedsthemaximumdefinedlengthofsixyfivechars", 
        "person_type": 1}"""

        response = self.c.post('/api/person/', person, content_type='application/json')

        content = response.content.decode()
        expected = {'message': 'Username too big', 'success': False}

        result_content = json.loads(content)
        self.assertJSONEqual(json.dumps(result_content), json.dumps(expected))

    def test_missing_person_data(self):
        person = """{}"""

        response = self.c.post('/api/person/', person, content_type='application/json')

        content = response.content.decode()
        expected = {'message': 'Invalid request', 'success': False}

        result_content = json.loads(content)
        self.assertJSONEqual(json.dumps(result_content), json.dumps(expected))

    def test_invalid_person_type(self):
        person = """{"username": "test1", "person_type": 101}"""

        response = self.c.post('/api/person/', person, content_type='application/json')

        content = response.content.decode()
        expected = {'message': 'Invalid person type', 'success': False}

        result_content = json.loads(content)
        self.assertJSONEqual(json.dumps(result_content), json.dumps(expected))

    def test_add_slot_candidate(self):
        # add a person first
        person = """{"username": "ca1", "person_type": 1}"""
        self.c.post('/api/person/', person, content_type='application/json')

        data = """{ "hour": 16, "date": "23/08/2019", "username": "ca1" }"""
        response = self.c.post('/api/slot/', data, content_type='application/json')

        content = response.content.decode()
        expected = {'success': True}

        result_content = json.loads(content)
        self.assertJSONEqual(json.dumps(result_content), json.dumps(expected))

    def test_add_slot_interviewer(self):
        # add a person first
        person = """{"username": "i1", "person_type": 2}"""
        self.c.post('/api/person/', person, content_type='application/json')

        data = """{ "hour": 16, "date": "23/08/2019", "username": "i1" }"""
        response = self.c.post('/api/slot/', data, content_type='application/json')

        content = response.content.decode()
        expected = {'success': True}

        result_content = json.loads(content)
        self.assertJSONEqual(json.dumps(result_content), json.dumps(expected))

    def test_add_slot_without_person(self):
        data = """{ "hour": 16, "date": "23/08/2019", "username": "i1" }"""
        response = self.c.post('/api/slot/', data, content_type='application/json')

        content = response.content.decode()
        expected = {'message': 'Invalid user', 'success': False}

        result_content = json.loads(content)
        self.assertJSONEqual(json.dumps(result_content), json.dumps(expected))

    def test_add_slot_invalid_hour(self):
        data = """{ "hour": 19, "date": "23/08/2019", "username": "i1" }"""
        response = self.c.post('/api/slot/', data, content_type='application/json')

        content = response.content.decode()
        expected = {'message': 'Invalid hour', 'success': False}

        result_content = json.loads(content)
        self.assertJSONEqual(json.dumps(result_content), json.dumps(expected))

    def test_add_slot_invalid_request(self):
        data = """{ "hour": 16}"""
        response = self.c.post('/api/slot/', data, content_type='application/json')

        content = response.content.decode()
        expected = {'message': 'Invalid request', 'success': False}

        result_content = json.loads(content)
        self.assertJSONEqual(json.dumps(result_content), json.dumps(expected))

    def test_events(self):
        # add a candidate and an interviewer
        self.test_add_slot_candidate()
        self.test_add_slot_interviewer()

        # call schedule command
        call_command('schedule_events')

        # call event list with parameter
        response_candidate = self.c.get('/api/event/list?candidate=ca1', content_type='application/json')
        response_interviewer = self.c.get('/api/event/list?interviewer=i1', content_type='application/json')

        content_candidate = response_candidate.content.decode()
        content_interviewer = response_interviewer.content.decode()

        expected = {
            'data': [
                {
                    'date': '2019-08-23',
                    'hour': '16',
                    'users': [
                        {
                            'type': 'Candidate', 'username': 'ca1'
                        },
                       {
                           'type': 'Interviewer', 'username': 'i1'
                       }
                    ]
                }
            ],
            'success': True
        }

        result_candidate = json.loads(content_candidate)
        result_interviewer = json.loads(content_interviewer)

        self.assertJSONEqual(json.dumps(result_candidate), json.dumps(expected))
        self.assertJSONEqual(json.dumps(result_interviewer), json.dumps(expected))

        # call event list without parameters
        response = self.c.get('/api/event/list', content_type='application/json')

        content = response.content.decode()
        expected = {'success': True, 'message': 'Candidate or interviewer list should be set'}

        result_content = json.loads(content)
        self.assertJSONEqual(json.dumps(result_content), json.dumps(expected))
