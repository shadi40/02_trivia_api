import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        # Create a test Flask app and configure it
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)

        # Setup the test database
        setup_db(self.app, self.database_path)

        # Binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)

            # Create all tables in the test database
            self.db.create_all()

    def tearDown(self):
        """Executed after each test"""
        pass

    def test_get_categories(self):
        """Test the endpoint to get all categories."""
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['categories']) > 0)

    def test_get_questions(self):
        """Test the endpoint to get all questions with pagination."""
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']) > 0)
        self.assertTrue(data['total_questions'] > 0)

    def test_delete_question(self):
        """Test the endpoint to delete a question by ID."""
        # Create a test question and insert it into the database
        question = Question(question='Test question', answer='Test answer', category=1, difficulty=1)
        question.insert()
        question_id = question.id

        # Send a DELETE request to delete the question
        res = self.client().delete(f'/questions/{question_id}')
        data = json.loads(res.data)

        # Check the response and status code
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted'], question_id)

    def test_create_question(self):
        """Test the endpoint to create a new question."""
        # Create a test question
        new_question = {
            'question': 'Test question',
            'answer': 'Test answer',
            'category': 1,
            'difficulty': 1
        }

        # Send a POST request to create the question
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)

        # Check the response and status code
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['created'])

    def test_search_questions(self):
        """Test the endpoint to search for questions."""
        # Perform a search for questions containing 'What'
        search_term = 'What'
        res = self.client().post('/questions/search', json={'searchTerm': search_term})
        data = json.loads(res.data)

        # Check the response and status code
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']) > 0)

    def test_get_questions_by_category(self):
        """Test the endpoint to get questions by category."""
        # Request questions from category with string identifier 'Science'
        res = self.client().get('/categories/Science/questions')
        data = json.loads(res.data)

        # Check the response and status code
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']) > 0)


    def test_play_quiz(self):
        """Test the endpoint to play the quiz."""
        # Create a quiz with previous questions and a specific category
        previous_questions = []
        quiz_category = {'id': 1, 'type': 'Science'}

        # Send a POST request to start the quiz
        res = self.client().post('/quizzes', json={'previous_questions': previous_questions, 'quiz_category': quiz_category})
        data = json.loads(res.data)

        # Check the response and status code
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['question'])

    def test_404_not_found(self):
        """Test a 404 error for a nonexistent endpoint."""
        res = self.client().get('/nonexistent')
        data = json.loads(res.data)

        # Check the response and status code
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'Resource not found')

    def test_400_bad_request(self):
        """Test a 400 error for a bad request."""
        # Send a POST request with an empty body to trigger a bad request
        res = self.client().post('/questions', json={})
        data = json.loads(res.data)

        # Check the response and status code
        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['message'], 'Bad request')

    def test_422_unprocessable_entity(self):
        """Test a 422 error for an unprocessable entity."""
        # Send a DELETE request for a nonexistent question
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        # Check the response and status code
        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], 'Unprocessable entity')

if __name__ == "__main__":
    unittest.main()
