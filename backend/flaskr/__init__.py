import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

#This function used to paginate questions throughout the website page
def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r'/api/*':{'origins':'*'}})

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
    categories = Category.query.all()

    if len(categories) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'categories': {category.id: category.type for category in categories}
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

  @app.route('/questions', methods=['GET'])
  def get_questions():

    #get all questions
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, selection)
    # get all categories
    categories = Category.query.order_by(Category.type).all()

    #Make sure there are questions to return
    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(selection),
      'categories': {category.id: category.type for category in categories},
      'current_category': None
      }) 

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/questions/<question_id>', methods= ['DELETE'])
  def delete_question(question_id):
    # if try is successful, the book must be delted and value returned
    try:
      qus_to_delete = Question.query.filter(Question.id == question_id).one_or_none()

      #In case tried to delete a non-existant question, it should abort with 404: resource not available
      if qus_to_delete is None:
        abort(404)

      else:
        qus_to_delete.delete()

        return jsonify({
          'success': True,
          'deleted': question_id
          })
    #In case try block failed which means something went wrong, should abort with 422 code: unprocessable
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

  @app.route('/questions', methods= ['POST'])
  def create_question():
    req_body = request.get_json()
    question = req_body.get('question', None)
    answer = req_body.get('answer', None)
    category = req_body.get('category', None)
    difficulty = req_body.get('difficulty', None)
   
    try:
      #Ensure that all required fields to create a question are supplied
      if ((question is None) or (answer is None) or (category is None) or (difficulty is None)):
        # consider the request unprocessible
        abort (422)

      else:
        #Create the question instance
        newQues = Question(question=question, answer=answer, category=category, difficulty=difficulty)

        #insert the new question into db
        newQues.insert()

        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        # return values (RECHECK THIS!!)
        return jsonify({
          'success': True,
          'created': newQues.id,
          'questions': current_questions,
          'total_questoins': len(Question.query.all())
        })
      
    except Exception as error: 
      print(f"\nerror => {error}\n") 
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

  @app.route('/questions/search', methods= ['POST'])
  def search_questions():
    body = request.get_json()
    #Get what the user searched about
    search_term = body.get('searchTerm', None)
    try:
      if search_term:
        search_results = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
        #make sure search term doesn't return empty result or else abort with resource not found
        if len(search_term) == 0:
          abort(404)
        else:
          #This should extract the uniques current categories out of the retrieved questions from searching activity
          current_categories = list(set(result.category for result in search_results))
          #print(current_categories)

          return jsonify({
            'success': True,
            'questions': [question.format() for question in search_results],
            'total_questions': len(search_results),
            #Note: although I returned current_categories, I did not observe a difference!!
            'current_category': current_categories
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


  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_question_by_category(category_id):
    #get all questions with asked category from db
    cat_questions = Question.query.filter(Question.category == category_id).all()
    #ensure availability of questions in that category
    if len(cat_questions) == 0:
      abort(404)

    else:
      return jsonify({
        'success': True,
        'questions': [question.format() for question in cat_questions],
        'total_questions': len(cat_questions),
        'current_category': category_id})

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
  # @app.route('/quizzes', methods=['POST'])
  # def quiz():
  #   body = request.get_json()

  #   if not ('quiz_category' in body and 'previous_questions' in body):
  #     abort(400)
  #   try:
  #     category = body.get('quiz_category')['id']
  #     previous_questions = body.get('previous_questions')

  #     if category == 0:
  #       questions_list = Question.query.filter(Question.id.notin_(
  #         previous_questions)).all()

  #     else:
  #       questions_list = Question.query.filter_by(category=category).filter(
  #         Question.id.notin_(previous_questions)).all()

  #     if len(questions_list) > 0:
  #         random_question = questions_list[random.randint(
  #             0, len(questions_list))].format()
  #     else:
  #         random_question = None
  #     print(random_question)
  #     return jsonify({
  #         'success': True,
  #         'question': random_question
  #     })
  #   except BaseException:
  #       abort(422)


  @app.route('/quizzes', methods=['POST'])

  def retrive_quizQuestion():
    body = request.get_json()
    quiz_category = body.get('quiz_category', None)['id']
    previous_questions = body.get('previous_questions', None)

    # check, if user selected category, pop up related questions, else use all collection
    if quiz_category:
      questions = Question.query.filter(Question.category == quiz_category).all()
    else:
      questions = Question.query.all()

    #create a list of question ids to compare and select from
    q_id = [q.format()['id'] for q in questions]

    if len(q_id) != len(previous_questions):
      #select randomly from our gathered questions knowing that the 
      # selected question is not displayed/selected previously
      new_q_id = random.choice([id for id in q_id if id not in previous_questions])
      previous_questions.append(new_q_id)
      curr_question = Question.query.filter(Question.id == new_q_id).one_or_none().format()
    else:
      #End the list in case all questions are selected previously
      curr_question = None

    return jsonify({
      'success': True,
      'question': curr_question,
      'previous_questions': previous_questions
    })

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
          "success":False,
          "error":404,
          "message":"resource not found"
      }),404


  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
          "success": False,
          "error": 422,
          "message": "unprocessable"
      }),422

  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
          "success":False,
          "error":400,
          "message": "bad request"
      }),400
  
  @app.errorhandler(405)
  def not_allowed(error):
      return jsonify({
          "success": False,
          "error":405,
          "message": "method not allowed"
      }),405   


  return app

    