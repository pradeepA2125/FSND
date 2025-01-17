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
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres', '123','localhost:5432', self.database_name)
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
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_all_categories(self):
        """Test GET all categories. """
        # Step 1: Create a category, so test can fetch something
        
        # Step 2: Test GET Endpoint
        res = self.client().get('/categories')
        
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['categories']) > 0)

    def test_error_405_get_all_categories(self):
        """Test wrong method to GET all categories """
        res = self.client().post('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['error'], 405)
        self.assertEqual(data['message'], "method not allowed")
        self.assertEqual(data['success'], False)

#----------------------------------------------------------------------------#
# Tests for /questions GET
#----------------------------------------------------------------------------#

    def test_get_all_questions_paginated(self):
        """Test GET all questions from all categories. JSON body should not have any impact. """
        res = self.client().get('/questions?page=1', json={'category:' : 'science'})
        
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['totalQuestions'] > 0)
    
    def test_error_405_get_all_questions_paginated(self):
        """Test wrong method to get all questions from all categories """
        res = self.client().patch('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['error'], 405)
        self.assertEqual(data['message'], "method not allowed")
        self.assertEqual(data['success'], False)

    def test_error_404_get_all_questions_paginated(self):
        """Test get all questions with not existing page """
        res = self.client().get('/questions?page=12452512')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], "resource not found")
        self.assertEqual(data['success'], False)

#----------------------------------------------------------------------------#
# Tests for /questions DELETE
#----------------------------------------------------------------------------#

    def test_delete_question(self):
        """Test DELETE /question """
        # First, create a new question so it can later be deleted
        
        # Used as header to POST /question
        json_create_question = {
            'question' : 'triavia?',
            'answer' : 'No!',
            'category' : '1',
            'difficulty' : 1
        } 

        res = self.client().post('/questions', json = json_create_question)
        data = json.loads(res.data)
        question_id = data['created'] # contains id from newly created question

       # Second, make a DELETE request with newly created question
        res = self.client().delete('/questions/{}'.format(question_id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted'], question_id)
    
    def test_404_delete_question(self):
        """Test error DELETE /question with an id which does not exist """
        res = self.client().delete('/questions/{}'.format(1234567879))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

#----------------------------------------------------------------------------#
# Tests for /questions POST
#----------------------------------------------------------------------------#

    def test_create_question(self):
        """Test POST a new question """

        # Used as header to POST /question
        json_create_question = {
            'question' : 'trivia?',
            'answer' : 'Yes!',
            'category' : '1',
            'difficulty' : 1
        } 

        res = self.client().post('/questions', json = json_create_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['created'] > 0)
    
    def test_error_create_question(self):
        """Test POST a new question with missing category """

        # Used as header to POST /question
        json_create_question_error = {
            'question' : 'Is this a test question?',
            'answer' : 'Yes it is!',
            'difficulty' : 1
        } 

        res = self.client().post('/questions/2', json = json_create_question_error)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    def test_search_question(self):
        """Test POST to search a question with an existing search term. """

        # Used as header to POST /question
        json_search_question = {
            'searchTerm' : 'entitled',
        } 

        res = self.client().post('/questions/search', json = json_search_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']) > 0)
        self.assertTrue(data['total_questions'] > 0)

    def test_error_404_search_question(self):
        """Test POST to search a question with non existing search term. """

        # Used as header to POST /question
        json_search_question = {
            'not_providing_arguement' : 'wwwwwwwwwwwwwwww',
        } 

        res = self.client().post('/questions/search', json = json_search_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')

#----------------------------------------------------------------------------#
# Tests for /categories/<string:category_id>/questions GET
#----------------------------------------------------------------------------#
    def test_get_questions_from_category(self):
        """Test GET all questions from selected category."""
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']) > 0)
        self.assertTrue(data['total_questions'] > 0)
        self.assertEqual(data['current_category'], 'Science')

    def test_400_get_questions_from_category(self):
        """Test 400 if no questions with queried category is available."""
        res = self.client().get('/categories/14125412/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'resource not found')

#----------------------------------------------------------------------------#
# Tests for /quizzes POST
#----------------------------------------------------------------------------#
    def test_play_quiz_with_category(self):
        """Test /quizzes succesfully with given category """
        json_play_quizz = {
            'previous_questions' : [1, 2, 5],
            'quiz_category' : {
                'type' : 'Science',
                'id' : '1'
                }
        } 
        res = self.client().post('/quizzes', json = json_play_quizz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['question']['question'])
        # Also check if returned question is NOT in previous question
        self.assertTrue(data['question']['id'] not in json_play_quizz['previous_questions'])
    
    def test_play_quiz_without_category(self):
        """Test /quizzes succesfully without category"""
        json_play_quizz = {
            'previous_questions' : [1, 2, 5],
            'quiz_category': {'type': 'click', 'id': 0}
        } 
        res = self.client().post('/quizzes', json = json_play_quizz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['question']['question'])
        # # Also check if returned question is NOT in previous question
        self.assertTrue(data['question']['id'] not in json_play_quizz['previous_questions'])

    def test_error_400_play_quiz(self):
        """Test /quizzes error without any JSON Body"""
        res = self.client().post('/quizzes')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')

    def test_error_405_play_quiz(self):
        """Test /quizzes error with wrong method"""
        res = self.client().get('/quizzes')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['error'], 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()