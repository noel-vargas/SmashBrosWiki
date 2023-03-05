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
        #its only giving me 1 author, just for testing purposes
        authors_list = backend.get_authors()
        return render_template("about.html", authors_list=authors_list)


    # when the "pages" button is clicked, we change templates
    @app.route("/pages")
    def pages():
        name_list = backend.get_all_page_names('pages/')
        return render_template("pages.html", name_list = name_list)


    @app.route('/pages/<page_name>')
    def show_character_info(page_name):
        page_content = backend.get_wiki_page(page_name)
        page_image = backend.get_image("character-images/",page_name)
        return render_template('page.html', page_name=page_name, page_content=page_content, page_image = page_image)

    
    # TODO(Project 1): Implement additional routes according to the project requirements.
