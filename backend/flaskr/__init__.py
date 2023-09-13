import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

# Define the number of questions per page for pagination
QUESTIONS_PER_PAGE = 10

# Create and configure the Flask app
def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # Set up CORS to allow cross-origin requests
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods', 'GET, PUT, POST, DELETE, OPTIONS')
        return response

    # Endpoint to retrieve all categories
    @app.route('/categories')
    def get_categories():
        categories = Category.query.all()
        formatted_categories = {category.id: category.type for category in categories}

        if len(formatted_categories) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': formatted_categories
        })

    # Endpoint to retrieve questions with pagination
    @app.route('/questions')
    def get_questions():
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = Question.query.all()
        formatted_questions = [question.format() for question in questions]
        current_questions = formatted_questions[start:end]

        categories = Category.query.all()
        formatted_categories = {category.id: category.type for category in categories}

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(formatted_questions),
            'categories': formatted_categories,
            'current_category': None
        })

    # Endpoint to delete a question by ID
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.filter(Question.id == question_id).one_or_none()

        if question is None:
            abort(404)

        try:
            question.delete()
            return jsonify({
                'success': True,
                'deleted': question_id
            })
        except Exception as e:
            print(e)
            abort(422)

    # Endpoint to create a new question
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()

        # Check if all required fields are provided in the request
        required_fields = ['question', 'answer', 'category', 'difficulty']
        if not all(field in body for field in required_fields):
            abort(400)

        question = body['question']
        answer = body['answer']
        category = body['category']
        difficulty = body['difficulty']

        if not (question and answer and category and difficulty):
            abort(400)

        try:
            new_question = Question(question=question, answer=answer, category=category, difficulty=difficulty)
            new_question.insert()
            return jsonify({
                'success': True,
                'created': new_question.id
            })
        except Exception as e:
            print(e)
            abort(422)

    # Endpoint to search for questions
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        search_term = body.get('searchTerm', '')

        if search_term:
            questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
            formatted_questions = [question.format() for question in questions]

            if len(formatted_questions) == 0:
                abort(404)

            return jsonify({
                'success': True,
                'questions': formatted_questions,
                'total_questions': len(formatted_questions),
                'current_category': None
            })
        else:
            return jsonify({
                'success': True,
                'questions': [],
                'total_questions': 0,
                'current_category': None
            })

    # Endpoint to retrieve questions by category
    @app.route('/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):
        # Find the category by its ID
        category = Category.query.filter(Category.id == category_id).one_or_none()

        if category is None:
            abort(404)

        questions = Question.query.filter(Question.category == str(category.id)).all()
        formatted_questions = [question.format() for question in questions]

        if len(formatted_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': formatted_questions,
            'total_questions': len(formatted_questions),
            'current_category': category.type
        })

    # Endpoint to play the quiz
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        try:
            body = request.get_json()
            previous_questions = body.get('previous_questions', [])
            quiz_category = body.get('quiz_category', None)

            if quiz_category is None:
                abort(400)

            if quiz_category['id'] == 0:
                questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
            else:
                questions = Question.query.filter(Question.category == quiz_category['id'],
                                                   Question.id.notin_(previous_questions)).all()

            if len(questions) == 0:
                return jsonify({
                    'success': True,
                    'question': None
                })

            random_question = random.choice(questions)
            return jsonify({
                'success': True,
                'question': random_question.format()
            })

        except Exception as e:
            print(e)
            abort(422)

    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad request'
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable entity'
        }), 422

    return app

if __name__ == '__main__':
    app = create_app()
    app.run()
