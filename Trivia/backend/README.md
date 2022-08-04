# Backend - Trivia API

## Setting up the Backend

### Install Dependencies

1. **Python 3.7** - Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

2. **Virtual Environment** - We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organized. Instructions for setting up a virual environment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

3. **PIP Dependencies** - Once your virtual environment is setup and running, install the required dependencies by navigating to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

#### Key Pip Dependencies

- [Flask](http://flask.pocoo.org/) is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use to handle the lightweight SQL database. You'll primarily work in `app.py`and can reference `models.py`.

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross-origin requests from our frontend server.

### Set up the Database

With Postgres running, create a `trivia` database:

```bash
createbd trivia
```

Populate the database using the `trivia.psql` file provided. From the `backend` folder in terminal run:

```bash
psql trivia < trivia.psql
```

### Run the Server

From within the `./src` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
flask run --reload
```

The `--reload` flag will detect file changes and restart the server automatically.

## To Do Tasks

These are the files you'd want to edit in the backend:

1. `backend/flaskr/__init__.py`
2. `backend/test_flaskr.py`

One note before you delve into your tasks: for each endpoint, you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior.

1. Use Flask-CORS to enable cross-domain requests and set response headers.
2. Create an endpoint to handle `GET` requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories.
3. Create an endpoint to handle `GET` requests for all available categories.
4. Create an endpoint to `DELETE` a question using a question `ID`.
5. Create an endpoint to `POST` a new question, which will require the question and answer text, category, and difficulty score.
6. Create a `POST` endpoint to get questions based on category.
7. Create a `POST` endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question.
8. Create a `POST` endpoint to get questions to play the quiz. This endpoint should take a category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions.
9. Create error handlers for all expected errors including 400, 404, 422, and 500.

## Documenting your Endpoints

You will need to provide detailed documentation of your API endpoints including the URL, request parameters, and the response body. Use the example below as a reference.

### Documentation Example

`GET '/api/v1.0/categories'`

- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Returns: An object with a single key, `categories`, that contains an object of `id: category_string` key: value pairs.

```json
{
  "1": "Science",
  "2": "Art",
  "3": "Geography",
  "4": "History",
  "5": "Entertainment",
  "6": "Sports"
}
```

## Testing

Write at least one test for the success and at least one error behavior of each endpoint using the unittest library.

To deploy the tests, run

```bash
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```

## API Reference

### Getting Started
- Base URL: Currently this application can only be served locally, the backend application is hosted at the default ```http://127.0.0.1:5000/```, which is set as a proxy in the frontend configuration. 
- Authentication: This version of the application does not require authentication or API keys.

### Error Handling
Errors are returned as JSON objects in the following format:

 ```
{
  'success':False,
  'error': 404
  'message': 'page not found'
}
```
The API will return two error types when request fails

- 404: Resource not found
- 422: Unprocessible entity

### Endpoints

#### GET /categories

- General:
    - Returns a category object, a list of category data, and success value.
- Sample:  ```curl -X GET http://127.0.0.1:5000/categories```


```
  {
    'categories': { 
      '1' : "Science",
      '2' : "Art",
      '3' : "Geography",
      '4' : "History",
      '5' : "Entertainment",
      '6' : "Sports" }
}

```

#### GET /questions?page=${integer}

- General:
    - Returns a question object, a list of questions data, total_questions, categories, current_category, and success value.

    - Results are paginated in groups of 10. include a request argument to choose page number, starting from 1.

- Sample:  ```curl -X GET http://127.0.0.1:5000/questions```

```
    'questions': [
        {
            'id': 1,
            'question': 'This is a question',
            'answer': 'This is an answer',
            'difficulty': 5,
            'category': 2
        },
    ],
    'totalQuestions': 100,
    'categories': { '1' : "Science",
    '2' : "Art",
    '3' : "Geography",
    '4' : "History",
    '5' : "Entertainment",
    '6' : "Sports" },
    'currentCategory': 'History'
    
}

```

 #### DELETE /questions/id

- General:
    -  Deletes a question based on the id of the questions

    -  Returns json object with success value, questions, total_questions, categories, 
      current_category

    - Results are paginated in groups of 10. include a request argument to choose page number, starting from 1.

- Sample:  ```curl -X DELETE http://127.0.0.1:5000/questions/id```


#### POST /questions

- General:
    - Creates a new questions using the question, answer, difficulty, and category. Returns the success value. 

- curl http://127.0.0.1:5000/questions -X POST -H "Content-Type: application/json" -d 
  {'question':'question', 'answer': 'answer', 'difficulty':'difficulty', 'new_category':'new_category'}

 ```
    {
        'question':  'Heres a new question string',
        'answer':  'Heres a new answer string',
        'difficulty': 1,
        'category': 3,
    }
 ```

#### POST /questions   (search)


- General:
    - Search for value using searchTerm. Returns the success value, questions. total_questions, current_category. 

- curl http://127.0.0.1:5000/questions -X POST -H "Content-Type: application/json" -d 
  { 'searchTerm':'searchTerm' }

 ```
Request body
    {
      'searchTerm': 'this is the term the user is looking for'
    }

    {
    'questions': [
        {
            'id': 1,
            'question': 'This is a question',
            'answer': 'This is an answer',
            'difficulty': 5,
            'category': 5
        },
    ],
    'totalQuestions': 100,
    'currentCategory': 'Entertainment'
  }
  
 ```

 
 #### GET /categories/id/questions

- General:
    - Returns a questions based on categories using the id of the category. 
    - Returns id, question, answer, difficulty, category

- curl -X GET http://127.0.0.1:5000/categories/3/questions

 ```
  {
    'questions': [
        {
            'id': 1,
            'question': 'This is a question',
            'answer': 'This is an answer',
            'difficulty': 5,
            'category': 4
        },
    ],
    'totalQuestions': 100,
    'currentCategory': 'History'
  }
 ```

  #### POST /quizzes

- General:
    - Creates quizzes using the previous_questions and the quiz_category and returns success value and a question

- curl  http://127.0.0.1:5000/quizzes -X POST -H  "Content-Type: application/json" -d  {'previous_questions': [], 'quiz_category': 1}
 ```

 Request body
    {
        'previous_questions': [1, 4, 20, 15]
        quiz_category': 'current category'
    }

    {
    'question': {
        'id': 1,
        'question': 'This is a question',
        'answer': 'This is an answer',
        'difficulty': 5,
        'category': 4
    }
  } 
 ```