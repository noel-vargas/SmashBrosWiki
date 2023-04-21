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

    @app.route("/pages/<page_name>", methods=["GET", "POST"])
    def show_character_info(page_name):
        """Renders specific (clicked) wiki page based on page_name."""
        page_content = backend.get_wiki_page(page_name)
        character_name, description, world, = page_content.split('|', 3)
        page_image = backend.get_image("character-images/", page_name)
        uploader = backend.tracker.get_page_uploader(page_name)
        comments = backend.tracker.get_comments(page_name)
        upvotes = backend.tracker.get_upvotes(page_name)
        if request.method == "POST":
            if not request.form.get("comment"):  # If upvote button was clicked.
                if user.active:
                    action = backend.tracker.upvote_page(
                        character_name, user.get_id())
                    flash(action)
                else:
                    flash("You need to be logged in to upvote a page.")
            else:  # If comment button was clicked.
                if user.active:
                    backend.tracker.add_comment(character_name, user.get_id(),
                                                request.form["comment"])
                    flash("Comment posted successfully!")
                else:
                    flash("You need to be logged in to leave a comment.")
        return render_template("page.html",
                               character_name=character_name,
                               description=description,
                               comments=comments,
                               upvotes=upvotes,
                               uploader=uploader,
                               page_image=page_image,
                               world=world,
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
        """Handles the log out process for logged-in users."""
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
            world = str(request.values['world'])
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
            if world == '':
                checker = False
                flash('No Character World Given')
            if not backend.allowed_file(file.filename):
                checker = False
                flash('Incorrect File Type')
            if checker:
                backend.upload(user.get_id(), file, name, info, world)
        return render_template("upload.html",
                               active=user.active,
                               name=user.get_id())

    @app.route('/users')
    def users():
        # Retrieve the list of users here
        users_list = backend.get_all_usernames()
        return render_template('users.html', users=users_list)

    @app.route('/users/<username>')
    def user_contributions(username):
        uploaded_pages = backend.get_uploaded_pages(username)
        comments = backend.get_user_comments(username, uploaded_pages)
        total_upvotes = backend.tracker.get_upvotes(username)
        return render_template('contributions.html',
                               username=username,
                               uploaded_pages=uploaded_pages,
                               comments=comments,
                               total_upvotes=total_upvotes)
