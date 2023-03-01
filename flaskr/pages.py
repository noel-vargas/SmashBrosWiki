from flask import Flask, render_template
from google.cloud import storage
from flaskr.backend import Backend


backend = Backend()

def make_endpoints(app):

    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    def home():
        # TODO(Checkpoint Requirement 2 of 3): Change this to use render_template
        # to render main.html on the home page.
        return render_template("main.html")

    # CHECK HOW TO GET THE NAME IN HERE
    @app.route("nbs-wiki-content/smash-characters", methods=["GET"])
    def get_wiki_page(name):
        page = backend.get_wiki_page(name)

    @app.route("nbs-wiki-content/smash-characters", methods=["GET"])
    def get_all_page_names():
        page_names = backend.get_all_page_names()
    

    @app.route("nbs-wiki-content/smash-characters", methods=["GET"])
    def upload(file_path, file_name):
        backend.upload(file_path,file_name)

    
    # TODO(Project 1): Implement additional routes according to the project requirements.
