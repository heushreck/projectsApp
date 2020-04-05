import markdown
import os
import shelve
import uuid
import jwt
import datetime

# Import the framework
from flask import Flask, g, render_template, request, make_response
from flask_restful import Resource, Api, reqparse
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# Create an instance of Flask
app = Flask(__name__)

# Create the API
api = Api(app)

# Authentication

app.config['SECRET_KEY'] = 'thisissecret'

def get_db():
    db = getattr(g, '_project_database', None)
    if db is None:
        db = g._database = shelve.open("projects.db")
    return db

@app.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_project_database', None)
    if db is not None:
        db.close()

def get_user_db():
    db = getattr(g, '_user_database', None)
    if db is None:
        db = g._database = shelve.open("users.db")
    return db

@app.teardown_appcontext
def teardown_user_db(exception):
    db = getattr(g, '_user_database', None)
    if db is not None:
        db.close()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return {'message': 'Token is missing!'}, 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            shelf = get_user_db()
            current_user = shelf[data['public_id']]
            print(current_user['user_name'])
        except:
            return {'message': 'Token is invalid!'}, 401

        return f(current_user, *args, **kwargs)
    return decorated

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/readme")
def index():
    """Present some documentation"""

    # Open the README file
    with open('README.md', 'r') as markdown_file:

        # Read the content of the file
        content = markdown_file.read()

        # Convert to HTML
        return markdown.markdown(content)

class UserList(Resource):
    @token_required
    def get(current_user, self):
        if not current_user['admin']:
            return {'message': 'no admin', 'data': {}}, 401
        shelf = get_user_db()
        keys = list(shelf.keys())

        users = []

        for key in keys:
            users.append(shelf[key])

        return {'message': 'Success', 'data': users}, 200
    @token_required
    def post(current_user, self):
        if not current_user['admin']:
            return {'message': 'no admin', 'data': {}}, 401
        parser = reqparse.RequestParser()
        parser.add_argument('user_name', required=True)
        parser.add_argument('password', required=True)

        # Parse the arguments into an object
        args = parser.parse_args()

        hashed_password = generate_password_hash(args['password'], method='sha256')
        args['password'] = hashed_password
        args['public_id'] = str(uuid.uuid4())
        args['admin'] = False
        shelf = get_user_db()
        shelf[args['public_id']] = args

        return {'message': 'User created', 'data': args}, 201

class User(Resource):
    @token_required
    def get(current_user, self, public_id):
        if not current_user['admin']:
            return {'message': 'no admin', 'data': {}}, 401
        shelf = get_user_db()

        # If the key does not exist in the data store, return a 404 error.
        if not (public_id in shelf):
            return {'message': 'User not found', 'data': {}}, 404

        return {'message': 'User found', 'data': shelf[public_id]}, 200
    @token_required
    def put(current_user, self, public_id):
        if not current_user['admin']:
            return {'message': 'no admin', 'data': {}}, 401
        shelf = get_user_db()

        # If the key does not exist in the data store, return a 404 error.
        if not (public_id in shelf):
            return {'message': 'Project not found', 'data': {}}, 404

        user = shelf[public_id]
        user['admin'] = True
        del shelf[public_id]
        shelf[public_id] = user
        return {'message': 'User has been promoted', 'data': {}}, 200
    @token_required
    def delete(current_user, self, public_id):
        if not current_user['admin']:
            return {'message': 'no admin', 'data': {}}, 401
        shelf = get_user_db()

        # If the key does not exist in the data store, return a 404 error.
        if not (public_id in shelf):
            return {'message': 'Project not found', 'data': {}}, 404

        del shelf[public_id]
        return {'message': 'User has been deleted', 'data': {}}, 204

class Login(Resource):
    def get(self):
        auth = request.authorization

        if not auth or not auth.username or not auth.password:
            return make_response('Could not verify', 401, {'WWW-Authenticate':'Basic Rrealm="Login required!"'})

        shelf = get_user_db()
        keys = list(shelf.keys())

        user = None
        for key in keys:
            if shelf[key]['user_name'] == auth.username:
                user = shelf[key]

        if user is None:
            return make_response('Could not verify', 401, {'WWW-Authenticate':'Basic Rrealm="Login required!"'})

        if check_password_hash(user.password, auth.password):
            token = jwt.encode({'public_id': user['public_id'], 'exp' : datetime.datetime.utcnow() + datetime.timedelta(hours=3)}, app.config['SECRET_KEY'])
            return {'message': 'Access granted', 'data': token.decode('UTF-8')}, 200

        return make_response('Could not verify', 401, {'WWW-Authenticate':'Basic Rrealm="Login required!"'})

class ProjectList(Resource):
    @token_required
    def get(current_user, self):
        shelf = get_db()
        keys = list(shelf.keys())

        projects = []

        for key in keys:
            if shelf[key]['public_id'] == current_user['public_id']:
                projects.append(shelf[key])

        return {'message': 'Success', 'data': projects}, 200

    @token_required
    def post(current_user, self):
        parser = reqparse.RequestParser()

        parser.add_argument('identifier', required=True)
        parser.add_argument('name', required=True)
        parser.add_argument('githup', required=True)
        parser.add_argument('resources', type=list, required=True)
        parser.add_argument('finished', type=bool, required=True)

        # Parse the arguments into an object
        args = parser.parse_args()

        args['public_id'] = current_user['public_id']

        shelf = get_db()
        shelf[args['identifier']] = args

        return {'message': 'Project added', 'data': args}, 201

class Project(Resource):
    @token_required
    def get(current_user, self, identifier):
        shelf = get_db()

        # If the key does not exist in the data store, return a 404 error.
        if not (identifier in shelf):
            return {'message': 'Project not found', 'data': {}}, 404

        return {'message': 'Project found', 'data': shelf[identifier]}, 200

    @token_required
    def put(current_user, self, identifier):
        shelf = get_db()

        # If the key does not exist in the data store, return a 404 error.
        if not (identifier in shelf):
            return {'message': 'Project not found', 'data': {}}, 404

        project = shelf[identifier]
        if project['public_id'] != current_user['public_id']:
            return {'message': 'This is not your project', 'data': {}}, 401
        project['finished'] = True
        del shelf[identifier]
        shelf[identifier] = project
        return {'message': 'Project is finished', 'data': {}}, 200

    @token_required
    def delete(current_user, self, identifier):
        shelf = get_db()

        # If the key does not exist in the data store, return a 404 error.
        if not (identifier in shelf):
            return {'message': 'Project not found', 'data': {}}, 404

        project = shelf[identifier]
        if project['public_id'] != current_user['public_id']:
            return {'message': 'This is not your project', 'data': {}}, 401
        del shelf[identifier]
        return '', 204

api.add_resource(ProjectList, '/projects')
api.add_resource(Project, '/projects/<string:identifier>')
api.add_resource(UserList, '/users')
api.add_resource(User, '/users/<string:public_id>')
api.add_resource(Login, '/login')

if __name__ == '__main__':
    app.run(debug=True)
