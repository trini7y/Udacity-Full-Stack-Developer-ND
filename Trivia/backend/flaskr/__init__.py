import json
import os
from sre_constants import SUCCESS
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):

    app = Flask(__name__)
    setup_db(app)

    cors = CORS(app, resources={
        r"/api/":{'origins':"*"}
    })

    # Pagination function
    def paginate_questions(request, selection):
        page  = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        question = [quest.format() for quest in selection]
        current_question = question[start:end]
        return current_question

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response


    @app.route('/categories', methods=['GET'])
    def getCategories():
        categories = Category.query.all()
        # db.session.query(Category.id).all()
        getData = {}
        for category in categories:
                getData[str(category.id)] = category.type

        return jsonify({
            'success': True,
            'categories': getData
        })


    @app.route('/questions', methods=['GET'])
    def questions():
        question = Question.query.order_by(Question.id).all()
        currentQuestions = paginate_questions(request, question)
        categories = Category.query.all()
        getData = {}
        for category in categories:
                getData[str(category.id)] = category.type

        return jsonify({
            'success': True,
            'questions': currentQuestions,
            'total_questions': len(question),
            'categories':getData,
            'current_category': 0
        })


    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter( Question.id == question_id).first()

            if question is None:
                abort(404)

            question.delete()
            question = Question.query.order_by(Question.id).all()
            currentQuestions = paginate_questions(request, question)
            categories = Category.query.all()
            # currentCategory = Category.query.filter(Question.category == Category.id).first()
            getData = {}
            for category in categories:
                    getData[str(category.id)] = category.type

            return jsonify({
                'success': True,
                'questions': currentQuestions,
                'total_questions': len(question),
                'categories':getData,
                'current_category': 0
            })
        except:
            abort(404)


    @app.route('/questions', methods=['POST'])
    def add_question():
        data = request.get_json()

        if 'searchTerm' in data:
            searchTerm = data.get('searchTerm', None)
            print(searchTerm)
            # questions  = Question.query.filter(Question.question.contains(searchTerm)).order_by(Question.id).all()
            questions = db.session.query(Question).filter(db.func.lower(Question.question).like(
            f"%{searchTerm.lower()}%")).order_by(Question.id).all()
            lstQ = []
            currentCategory = None
            for quest in questions:
                # currentCategory = Category.query.filter(quest.category == Category.id).first()
                lstQ.append({
                    'id': quest.id,
                    'question':quest.question,
                    'answer': quest.answer,
                    'difficulty': quest.difficulty,
                    'category': quest.category
                })

            return jsonify({
            'success': True,
            'questions': lstQ,
            'total_questions': len(questions),
            'current_category': 0
        })

        if 'question' or 'answer' or 'difficulty' or 'category' in data:
            new_question = data.get('question', None)
            new_answer = data.get('answer', None)
            new_difficulty = data.get('difficulty', None)
            new_category = data.get('category',  None)
            try:
                quest = Question(question = new_question, answer = new_answer, difficulty = new_difficulty, category = new_category)
                quest.insert()
                return jsonify({
                    'success':True
                })
            except:
                abort(404)


    @app.route('/categories/<int:id>/questions', methods=['GET'])
    def getCategoriesById(id):
        questions = Question.query.filter(str(id) == Question.category).all()
        currentCategory = None
        quest = []
        for question in questions:
            currentCategory = Category.query.filter(question.category == Category.id).first()
            quest.append( {
                'id': question.id,
                'question': question.question,
                'answer': question.answer,
                'difficulty': question.difficulty,
                'category': question.category
            } )

        print(quest)
        return jsonify({
            'success':True,
            'questions': quest,
            'total': len(quest),
            'currentCategory':  currentCategory.type
        })

    @app.route('/quizzes', methods=['POST'])
    def quizzes():
        data = request.get_json()
        prevQuestion = data.get('previous_questions', None)
        quizCategory = data.get('quiz_category', None)
        getID = str( quizCategory.get('id' ))
        print(quizCategory)
        print(prevQuestion)
        print(getID)

        quest = {}
        logQuestion = []
        GD = int(getID)
        if not prevQuestion:
            if GD == 0:
                questions = Question.query.all()
            else:
                questions = Question.query.filter(
                    Question.category == getID).all()
        else:
            if GD == 0:
                questions = Question.query.filter(Question.id.notin_(prevQuestion)).all()
            else:
                questions = Question.query.filter(getID == Question.category).filter(
                Question.id.notin_(prevQuestion)).all()

            print('Log Question',logQuestion)

        questions = [question.format() for question in questions]
        total_question = len(questions)
        
        if total_question == 1:
            random_quest = questions[0]
        else:
            random_quest = random.choice(questions)
        print(questions)

        return jsonify({
            'success': True,
            'question': random_quest
        })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success':False,
            'error': 404,
            'message': 'Resource not found'
        }), 404

    @app.errorhandler(422)
    def unproccessible(error):
        return jsonify({
            'success':False,
            'error': 422,
            'message': 'Unprocessible entity'
        }), 422
    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            'success':False,
            'error': 405,
            'message': 'method not allowed'
        }), 405

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success':False,
            'error': 400,
            'message': 'Bad Request'
        }), 405
    

    return app