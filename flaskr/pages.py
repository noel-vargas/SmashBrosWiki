from flask import Flask, render_template, url_for, redirect, flash, request
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, TextAreaField
from wtforms.validators import InputRequired


class SignupForm(FlaskForm):
    """Generates form and stores form data for signing up process."""
    username = StringField(validators=[InputRequired()],
                           render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired()],
                             render_kw={"placeholder": "Password"})
    submit = SubmitField("Sign Up")


class LoginForm(FlaskForm):
    """Generates form and stores form data for log in process."""
    username = StringField(validators=[InputRequired()],
                           render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired()],
                             render_kw={"placeholder": "Password"})
    submit = SubmitField("Log In")


class User():
    """Current user in session."""

    def __init__(self, username, active=False):
        self.username = username
        self.active = active

    def is_active(self):
        return self.active

    def is_authenticated(self):
        return True

    def get_id(self):
        return self.username


user = User(None)  # /login will update this with current user in session.


def make_endpoints(app, backend):

    # Initiates login_manager for session handling.
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"

    @login_manager.user_loader
    def load_user(username):
        return user

    @app.route('/')
    @app.route("/home")
    def home():
        """Renders the home/landing page when the page is accessed."""
        return render_template("main.html",
                               active=user.active,
                               name=user.get_id())

    @app.route("/about")
    def about():
        """Renders authors' images and information."""
        authors_list = backend.get_authors()
        return render_template("about.html",
                               authors_list=authors_list,
                               active=user.active,
                               name=user.get_id())

    # when the "pages" button is clicked, we change templates
    @app.route("/pages")
    def pages():
        """Renders the page index for wiki pages."""
        name_list = backend.get_all_page_names()
        return render_template("pages.html",
                               name_list=name_list,
                               active=user.active,
                               name=user.get_id())

    @app.route("/pages/<page_name>")
    def show_character_info(page_name):
        """Renders specific (clicked) wiki page based on page_name."""
        page_content = backend.get_wiki_page(page_name)
        character_name, content, world = page_content.split('|', 2)  
        page_image = backend.get_image(page_name)
        if not page_image:
            page_image = "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"
        return render_template("page.html",
                            character_name=character_name,
                            content=content,
                            world=world,  # Add world to the template
                            page_image=page_image,
                            active=user.active,
                            name=user.get_id())


    @app.route("/signup", methods=["GET", "POST"])
    def sign_up():
        """Handles the sign up process for new users."""
        form = SignupForm()
        if form.validate_on_submit():
            new_user_name = form.username.data
            new_password = form.password.data
            check = backend.sign_up(new_user_name, new_password)
            if not check:
                flash("Username already exists. Please choose another one.")
            else:
                return redirect(url_for("login"))
        return render_template("register.html",
                               form=form,
                               active=user.active,
                               name=user.get_id())

    @app.route("/login", methods=["GET", "POST"])
    def login():
        """Handles the log in process for existing users."""
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
        return render_template("login.html",
                               form=form,
                               active=user.active,
                               name=user.get_id())

    @app.route("/logout", methods=["GET", "POST"])
    @login_required
    def logout():
        user.active = False
        logout_user()
        return redirect(url_for("login"))

    @app.route("/upload", methods=["GET", "POST"])
    @login_required
    def upload_file():
        if request.method == "POST":
            if 'file' not in request.files:
                flash('No file part')
            file = request.files['file']
            name = str(request.values['char_name'])
            info = str(request.values['info'])
            checker = True
            if file.filename == '':
                checker = False
                flash('No selected file')
            if name == '':
                checker = False
                flash('No Character Name Given')
            if info == '':
                checker = False
                flash('No Character Info Given')
            if not backend.allowed_file(file.filename):
                checker = False
                flash('Incorrect File Type')
            if checker:
                backend.upload(file, name, info)
        return render_template("upload.html",
                               active=user.active,
                               name=user.get_id())
