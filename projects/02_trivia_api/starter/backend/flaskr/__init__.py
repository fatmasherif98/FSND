import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  ques = [question.format() for question in selection]
  current_questions = ques[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    categories = Category.query.order_by(Category.id).all()
    categs = []
    for category in categories:
      categs.append(category.id)
    #categs = [category.id for category in categories]
    #categs = {category.id: category.type for category in categories}
    length = len(categs)
    #if len(categs) == 0:
      #abort(404)
    #for c in categs:
     # if c['type'] is None:
       # abort(422)

    return jsonify({
      'success':True,
      'categories': categs,
      'total_length': length
      })



  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 


  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def get_questions():
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request,selection)
    #categs_res= get_categories()
    categories = Category.query.order_by(Category.id).all()
    categs = [category.id for category in categories]

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(Question.query.all()),
      'current_category': None,
      'categories': categs #categs_res.get_json()['categories']
    })
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question == None:
        abort(404)

      question.delete()
      selection = Question.query.order_by(Question.id).all()
      length = len(selection)
      current_questions = paginate_questions(request, selection)

      return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': length
      })

    except:
      abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def add_question():
    try:
      body = request.get_json(force=True)
    except:
      abort(400)

    new_ques = body.get('question', None)
    new_ans = body.get('answer', None)
    new_diff = body.get('difficulty', None)
    new_categ = body.get('category', None)

    try:
      if new_ques is None:
        abort(400)
      question = Question(question = new_ques, answer=new_ans, category=new_categ, difficulty=new_diff)
      question.insert()

      selection = Question.query.order_by(Question.id).all()
      length = len(selection)
      current_questions = paginate_questions(request, selection)

      return jsonify({
        'success': True,
        'created': question.id,
        'questions': current_questions,
        'total_questions': length,
        'current_category': new_categ
      })
    except:
      abort(422)
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  @app.route('/searchQuestions', methods=['POST'])
  def search_question():
    try:
      body = request.get_json(force=True)
    except:
      abort(400)
    try:
      search_term = body.get('searchTerm', None)
      if search_term is None:
        abort(422)
      questions=Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
      length = len(questions)
      current_questions = paginate_questions(request, questions)

      return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': length,
        'current_category': None
      })
    except:
      abort(422)
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

  @app.route('/categories/<int:category_id>/questions')
  def get_category_questions(category_id):
    try:
      if Category.query.filter(Category.id == category_id).count() == 0:
        abort(404)

      questions = Question.query.filter(Question.category == category_id).all()
      length = len(questions)
      current_questions = paginate_questions(request, questions)

      return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': length,
        'current_category': category_id
      })
    except:
      abort(422)


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_next_question():

    try:
      body = request.get_json(force=True)
    except:
      abort(400)
    try:
      body = request.get_json()
      previous_questions = body.get('previous_questions', [])
      quiz_category = body.get('quiz_category', None)
      

      if quiz_category is not None:
        questions = Question.query.filter(Question.category == quiz_category['id'], Question.id.notin_(previous_questions)).all()
        #questions = Question.query.all()
      else:
        questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
        #questions = Question.query.all()
      q = random.choice(questions).format()
      return jsonify({
      'success': True,
      'question': q,
      'current_category': q['category']
      })
    except:
     abort(422)
  

  


 
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({"success": False, "error": 400, "message": "Bad Request" }),400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({"success": False, "error": 404, "message": "Not Found" }),404

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({"success": False, "error": 405, "message": "this method is not allowed" }),405

  @app.errorhandler(422)
  def unprocessable_entity(error):
    return jsonify({"success": False, "error": 422, "message": "unprocessable entity" }),422

  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({"success": False, "error": 500, "message": "internal server error" }),500

  return app

    