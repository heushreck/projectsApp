import markdown
import os
import shelve

# Import the framework
from flask import Flask, g, render_template
from flask_restful import Resource, Api, reqparse

# Create an instance of Flask
app = Flask(__name__)

# Create the API
api = Api(app)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = shelve.open("projects.db")
    return db

@app.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

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


class ProjectList(Resource):
    def get(self):
        shelf = get_db()
        keys = list(shelf.keys())

        projects = []

        for key in keys:
            projects.append(shelf[key])

        return {'message': 'Success', 'data': projects}, 200

    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('identifier', required=True)
        parser.add_argument('name', required=True)
        parser.add_argument('githup', required=True)
        parser.add_argument('resources', type=list, required=True)
        parser.add_argument('finished', type=bool, required=True)

        # Parse the arguments into an object
        args = parser.parse_args()

        shelf = get_db()
        shelf[args['identifier']] = args

        return {'message': 'Project added', 'data': args}, 201

class Project(Resource):
    def get(self, identifier):
        shelf = get_db()

        # If the key does not exist in the data store, return a 404 error.
        if not (identifier in shelf):
            return {'message': 'Project not found', 'data': {}}, 404

        return {'message': 'Project found', 'data': shelf[identifier]}, 200

    def delete(self, identifier):
        shelf = get_db()

        # If the key does not exist in the data store, return a 404 error.
        if not (identifier in shelf):
            return {'message': 'Project not found', 'data': {}}, 404

        del shelf[identifier]
        return '', 204

api.add_resource(ProjectList, '/projects')
api.add_resource(Project, '/projects/<string:identifier>')

if __name__ == '__main__':
    app.run(debug=True)
