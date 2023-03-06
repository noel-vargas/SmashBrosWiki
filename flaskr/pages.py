from flask import Flask, render_template, url_for, redirect, flash
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired
from .backend import Backend


class SingupForm(FlaskForm):
    username = StringField(validators=[InputRequired()], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired()], render_kw={"placeholder": "Password"})
    submit = SubmitField("Sign Up")


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired()], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired()], render_kw={"placeholder": "Password"})
    submit = SubmitField("Log In")


class User():
    def __init__(self, username, active=False):
        self.username = username
        self.active = active

    def is_active(self):
        return self.active 
    
    def is_authenticated(self):
        return True

    def get_id(self):
        return self.username


backend = Backend()
user = User(None)  # /login will update this with current user in session.

def make_endpoints(app):

    # Initiates login_manager for session handling.
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"

    @login_manager.user_loader
    def load_user(username):
        return user

    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    @app.route("/home")
    def home():
        # TODO(Checkpoint Requirement 2 of 3): Change this to use render_template
        # to render main.html on the home page.
        return render_template("main.html", active=user.active, name = user.get_id())
    # when the "About" button is clicked, we change templates
    @app.route("/about")
    def about():
        #its only giving me 1 author, just for testing purposes
        authors_list = backend.get_authors()
        return render_template("about.html", authors_list=authors_list, active=user.active, name = user.get_id())


    # when the "pages" button is clicked, we change templates
    @app.route("/pages")
    def pages():
        name_list = backend.get_all_page_names("/pages")
        return render_template("pages.html", name_list = name_list, active=user.active, name = user.get_id())


    @app.route('/pages/<page_name>')
    def show_character_info(page_name):
        page_content = backend.get_wiki_page(page_name)
        return render_template('page.html', page_name=page_name, page_content=page_content, active=user.active, name = user.get_id())

    
    @app.route("/signup", methods=["GET", "POST"])
    def sign_up():
        form = SingupForm()
        if form.validate_on_submit():
            new_user_name = form.username.data
            new_password = form.password.data
            check = backend.sign_up(new_user_name, new_password)
            if not check:
                flash("Username already exists. Please choose another one.")
            else:
                return redirect(url_for("login"))

        return render_template("register.html", form=form, active=user.active, name = user.get_id())
    

    @app.route("/login", methods=["GET", "POST"])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            check = backend.sign_in(username, password)
            if check == -1:
                flash("User does not exist.")
            elif check == False:
                flash("Wrong credentials. Try again.")
            else:
                user.username = username
                user.active = True
                login_user(user)
                return redirect(url_for("home"))
        
        return render_template("login.html", form=form, active=user.active, name = user.get_id())
    
    
    @app.route("/logout", methods=["GET", "POST"])
    @login_required
    def logout():
        user.active = False
        logout_user()
        return redirect(url_for("login"))

    
    # TODO(Project 1): Implement additional routes according to the project requirements.
