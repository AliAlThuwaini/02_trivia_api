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
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('student',
                                                             'student', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful
    operation and for expected errors.
    """

    # ************************
    # Get paginated Questions
    # *************************

    # test retrive_questions as paginated
    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    # ************************
    # Get Category
    # *************************

    # Test for valid Categories
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    # Test for invalid Category
    def test_404_get_categories(self):
        res = self.client().get('/categories/10')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], 'not found')

    # ************************
    # Get Questions
    # *************************

    # Test getting question with valid page

    def test_requesting_for_valid_page(self):
        res = self.client().get('/questions?page=2')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    # Test getting question with invalid page

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=5000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    # ************************
    # Delete Quesiton
    # *************************

    # Delete Question

    def test_delete_question(self):
        qid = 30
        res = self.client().delete(f'/questions/{qid}')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == qid).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], qid)
        self.assertEqual(question, None)

    # Tes delete method with non exist question
    def test_422_if_question_does_not_exist(self):
        res = self.client().delete('/questions/500')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    # ************************
    # Add Quesiton
    # *************************

    # Test for adding new question

    def test_add_a_question(self):
        new_question = {
            'question':
            'How long would it take for the sun light to travel to earth?',
            'answer': '8.5 minutes',
            'category': 1,
            'difficulty': 2
        }
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['questions'])

    # Test not allowed action in creation of new question
    def test_405_if_question_creation_not_allowed(self):
        new_question = {
            'question':
            'How long would it take for the sun light to travel to earth?',
            'answer': '8.5 minutes',
            'category': 1,
            'difficulty': 2
        }
        res = self.client().post('/questions/500', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    # ************************
    # Search Quesiton
    # *************************

    def test_search_question(self):
        search_word = {'searchTerm': 'original'}
        res = self.client().post('/questions/search', json=search_word)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    # Review this! it works with empty string but not with unavailable string!!

    def test_422_if_question_doesnt_exist_in_search(self):
        search_word = {'searchTerm': ''}
        res = self.client().post('/questions/search', json=search_word)
        data = json.loads(res.data)
        # print('response = ', data['questions'])
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    # ************************
    # Add Quesiton by Category
    # *************************

    # The below two functions should work, but still not sure why is not!
    # Need more review. Below is the error:

    # cursor.execute(statement, parameters)
    # sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedFunction)
    # operator does not exist: character varying = integer
    # LINE 3: WHERE questions.category = 2
    #                                  ^
    # HINT:  No operator matches the given name and argument types.
    # You might need to add explicit type casts.

    # Ali: I figured out the issue: data type of category colum in
    # question table is character varying while the above sql statement
    #  is trying to equal it to integer (2). Looks like there is no
    # automatic conversion in psql and hence error is raised! solution
    # I made: convert the data type to intger. Below is the statement
    # do do that (it is all one statement):

    # alter table questions alter column category type INT
    # using category::integer;

    def test_get_question_by_available_category(self):
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    def test_404_get_question_by_unavialble_category(self):
        res = self.client().get('/categories/500/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
