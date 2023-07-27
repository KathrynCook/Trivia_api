import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import sys

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # Create and configure the app.
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={r"/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers",
            "Content-Type,Authorization")
        response.headers.add(
            "Access-Control-Allow-Methods",
            "GET,PUT,POST,DELETE,OPTIONS")
        return response

    """
    Endpoint to handle GET requests for all available categories.
    """
    @app.route("/categories")
    def get_categories():
        categories = Category.query.all()
        current_categories = {}
        for cat in categories:
            current_categories[cat.id] = cat.type

        if len(current_categories) == 0:
            abort(404)

        return jsonify({
            "success": True,
            "categories": current_categories,
            "total_categories": len(categories)
        })

    """
    Endpoint to handle GET requests for questions, including pagination
    (every 10 questions). This endpoint returns a list of questions, number
    of total questions, current category, and categories.
    """
    @app.route('/questions')
    def get_all_questions():
        questions = Question.query.all()
        current_questions = paginate_questions(request, questions)

        categories = Category.query.all()
        all_categories = {}
        for cat in categories:
            all_categories[cat.id] = cat.type

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            "success": True,
            "questions": current_questions,
            "total_questions": len(questions),
            "categories": all_categories,
            "current_category": None
        })

    """
    Endpoint to DELETE a question using a question ID.
    """
    @app.route('/questions/<int:question_id>', methods=["DELETE"])
    def delete_question(question_id):
        question = Question.query.filter(
            Question.id == question_id).one_or_none()

        if question is None:
            abort(404)

        try:
            question.delete()
            questions = Question.query.all()
            current_questions = paginate_questions(request, questions)

            return jsonify({
                "success": True,
                "deleted": question_id,
                "questions": current_questions,
                "total_questions": len(questions)
            })

        except BaseException:
            abort(422)

    """
    Endpoint to POST a new question, which requires the question and
    answer text, category, and difficulty score.
    """
    @app.route('/questions', methods=['POST'])
    def new_question():
        body = request.get_json()

        new_question = body.get("question", None)
        new_answer = body.get("answer", None)
        new_category = body.get("category", None)
        new_difficulty = body.get("difficulty", None)

        if ((new_question is None) or (new_answer is None) or (
                new_category is None) or (new_difficulty is None)):
            abort(422)

        try:
            trivia = Question(
                question=new_question,
                answer=new_answer,
                category=new_category,
                difficulty=new_difficulty)
            trivia.insert()

            questions = Question.query.all()
            current_questions = paginate_questions(request, questions)

            return jsonify({
                "success": True,
                "created": trivia.id,
                "questions": current_questions,
                "total_questions": len(questions)
            })

        except BaseException:
            abort(422)

    """
    A POST endpoint to get questions based on a search term, which returns any
    questions that include the search term as a substring of the question.
    """
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        search = body.get('searchTerm', '')

        questions = Question.query.filter(
            Question.question.ilike(f'%{search}%')).all()
        current_questions = paginate_questions(request, questions)

        return jsonify({
            "success": True,
            "questions": current_questions,
            "total_questions": len(questions)
        })

    """
    A GET endpoint to get questions based on category.
    """
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_category_list(category_id):
        questions = Question.query.filter(
            Question.category == category_id).all()
        current_questions = paginate_questions(request, questions)

        if len(questions) == 0:
            abort(404)

        return jsonify({
            "success": True,
            "questions": current_questions,
            "total_questions": len(questions)
        })

    """
    A POST endpoint to get questions to play the quiz. This endpoint takes
    an optional category and previous question parameters and returns a random question
    which is not one of the previous questions within the given category, if specified.
    """
    @app.route('/quizzes', methods=['POST'])
    def get_quiz_questions():
        try:
            body = request.get_json()
            quiz_category = body.get('quiz_category', 0)
            previous_questions = body.get('previous_questions', [])

            if quiz_category['id'] == 0:
                quiz_questions = Question.query.filter(
                    Question.id.notin_(previous_questions)).all()
            else:
                quiz_questions = Question.query.filter_by(
                    category=quiz_category['id']).filter(
                    Question.id.notin_(previous_questions)).all()

            if len(quiz_questions) == 0:
                return jsonify({
                    "success": True,
                    "question": None
                }), 200

            questions = [q.format() for q in quiz_questions]
            next_q = random.choice(questions)

            return jsonify({
                "success": True,
                "question": next_q
            })

        except BaseException:
            abort(422)

    """
    Error handlers for all expected errors.
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource not found"
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "Method not allowed"
        }), 405

    @app.errorhandler(422)
    def not_able_to_process(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Not able to be processed"
        }), 422

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Server error"
        }), 500

    return app
