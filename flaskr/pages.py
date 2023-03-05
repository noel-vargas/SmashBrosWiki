from flask import Flask, render_template, url_for, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired
from .backend import Backend


class SingupForm(FlaskForm):
    username = StringField(validators=[InputRequired()], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired()], render_kw={"placeholder": "Password"})
    submit = SubmitField("Sign Up")

backend = Backend()

def make_endpoints(app):

    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    @app.route("/home")
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
        name_list = backend.get_all_page_names()
        return render_template("pages.html", name_list = name_list)


    @app.route('/pages/<page_name>')
    def show_character_info(page_name):
        page_content = backend.get_wiki_page(page_name)
        return render_template('page.html', page_name=page_name, page_content=page_content)

    
    @app.route("/signup", methods=["GET", "POST"])
    def sign_up():
        form = SingupForm()
        if form.validate_on_submit():
            new_user_name = form.username.data
            new_password = form.password.data
            check = backend.sign_up(new_user_name, new_password)
            return redirect(url_for("home"))

        return render_template("register.html", form=form)


    
    # TODO(Project 1): Implement additional routes according to the project requirements.
