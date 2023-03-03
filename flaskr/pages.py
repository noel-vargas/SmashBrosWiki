from flask import Flask, render_template
from google.cloud import storage
from .backend import Backend


backend = Backend()

def make_endpoints(app):

    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    def home():
        # TODO(Checkpoint Requirement 2 of 3): Change this to use render_template
        # to render main.html on the home page.
        return render_template("main.html")

    # when the "About" button is clicked, we change templates
    @app.route("/about")
    def about():
        return render_template("about.html")


     # when the "pages" button is clicked, we change templates
    @app.route("/pages")
    def pages():
        name_list = backend.get_all_page_names()
        return render_template("pages.html", name_list = name_list)



    
    # TODO(Project 1): Implement additional routes according to the project requirements.
