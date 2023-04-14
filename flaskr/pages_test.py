from flaskr import create_app

import pytest


# See https://flask.palletsprojects.com/en/2.2.x/testing/
# for more info on testing
@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
    })
    return app


@pytest.fixture
def client(app):
    return app.test_client()


# TODO(Checkpoint (groups of 4 only) Requirement 4): Change test to
# match the changes made in the other Checkpoint Requirements.
def test_home_page(client):
    resp = client.get("/")
    resp_home = client.get("/home")
    assert resp.status_code == 200
    assert resp_home.status_code == 200
    assert b"Welcome" in resp.data
    assert b"Welcome" in resp_home.data


# TODO(Project 1): Write tests for other routes.


def test_about_page(client):
    resp = client.get("/about")
    assert resp.status_code == 200
    assert b"About" in resp.data


def test_pages_page(client):
    resp = client.get("/pages")
    assert resp.status_code == 200
    assert b"Pages" in resp.data


# Test signup page
def test_signup_page(client):
    resp = client.get("/signup")
    assert resp.status_code == 200
    assert b"Sign Up" in resp.data


# Test login page
def test_login_page(client):
    resp = client.get("/login")
    assert resp.status_code == 200
    assert b"Log" in resp.data


def test_logout_page(client):
    resp = client.get("/logout")
    assert resp.status_code == 302
    assert b"Redirecting" in resp.data


def test_upload_page(client):
    resp = client.get("/upload")
    assert resp.status_code == 302
    assert b"Redirecting" in resp.data

def test_users_page(client):
    resp = client.get("/users")
    assert resp.status_code == 200
    assert b"Users" in resp.data
