import pytest, hashlib, base64
from werkzeug.security import generate_password_hash
from unittest.mock import MagicMock, call
from .backend import Backend


# Mocking Google Cloud Storage and Datastore client
@pytest.fixture
def mock_backend():
    backend = Backend(MagicMock(), MagicMock(), MagicMock(), MagicMock())

    # Mock the key method
    def key_mock(*args, **kwargs):
        key = MagicMock()
        key.name = args[1]  # Set the key name to the input character name
        return key

    backend.key = key_mock
    return backend


def test_get_wiki_page(mock_backend):
    # Configure the mock_backend.client.get method to return the character's information when called with the correct key
    def get_side_effect(key):
        print(key.name)
        if key.name == 'Mario':
            return {
                'Name': 'Mario',
                'Info': 'Plumber from the Mushroom Kingdom',
                'World': 'Super Mario Bros.'
            }
        return None

    mock_backend.client.get.side_effect = get_side_effect

    result = mock_backend.get_wiki_page('Mario')
    assert result == 'Mario|Plumber from the Mushroom Kingdom|Super Mario Bros.'

    result = mock_backend.get_wiki_page('Noel')
    assert result is None


def test_get_all_page_names(mock_backend):
    entity1 = MagicMock()
    entity1.key.name = "Mario"
    entity2 = MagicMock()
    entity2.key.name = "Link"

    mock_backend.client.query.return_value.fetch.return_value = [
        entity1, entity2
    ]

    result = mock_backend.get_all_page_names()
    assert result == ["Mario", "Link"]


def test_get_all_usernames(mock_backend):
    entity1 = MagicMock()
    entity1.key.name = "sebagabs"
    entity2 = MagicMock()
    entity2.key.name = "Noel"
    entity3 = MagicMock()
    entity3.key.name = "Bryan"

    mock_backend.client.query.return_value.fetch.return_value = [
        entity1, entity2, entity3
    ]

    result = mock_backend.get_all_page_names()
    assert result == ["sebagabs", "Noel", "Bryan"]


def test_upload(mock_backend):
    mock_backend.content_bucket.blob.return_value = MagicMock(
        upload_from_file=MagicMock())

    f = MagicMock(content_type='image/png', tell=MagicMock(return_value=0))
    mock_backend.upload("tester", f, 'Mario',
                        'A character from the Mario series.',
                        'Mushroom Kingdom')

    mock_backend.content_bucket.blob.assert_called_with(
        'character-images/Mario.png')
    mock_backend.client.put.assert_called()


def test_sign_up(mock_backend):
    mock_backend.client.get.return_value = None

    result = mock_backend.sign_up("new_user", "new_password")
    assert result is True


def test_sign_in(mock_backend):
    correct_password = 'existing_password'
    salted_password = f"existing_usernbs{correct_password}"
    correct_hash = hashlib.blake2b(salted_password.encode()).hexdigest()
    mock_backend.client.get.return_value = {'hashed_password': correct_hash}

    result = mock_backend.sign_in('existing_user', correct_password)
    assert result is True

    mock_backend.client.get.return_value = None
    result = mock_backend.sign_in('nonexistent_user', 'password')
    assert result == -1


def test_get_user_comments(mock_backend):
    # Prepare the mock data for tracker.get_comments method
    mock_comments = {
        '0': {
            'Noel1827': 'testing testing'
        },
        '1': {
            '2': 'tsting again brrrr'
        },
        '2': {
            '2': 'tsting again brrrr'
        },
        '3': {
            '2': 'one more time'
        },
        '4': {
            '2': 'one more time'
        }
    }
    mock_tracker = MagicMock(get_comments=MagicMock(return_value=mock_comments))
    mock_backend.tracker = mock_tracker

    # Test the get_user_comments function
    username = '2'
    uploaded_pages = ['Donkey Kong']
    result = mock_backend.get_user_comments(username, uploaded_pages)

    # Assert that the expected comments were returned
    expected_result = {
        'Donkey Kong': {
            '1': {
                '2': 'tsting again brrrr'
            },
            '2': {
                '2': 'tsting again brrrr'
            },
            '3': {
                '2': 'one more time'
            },
            '4': {
                '2': 'one more time'
            }
        }
    }
    assert expected_result == result

    # Check that get_comments was called with the expected arguments
    assert mock_tracker.get_comments.call_args_list == [call('Donkey Kong')]


# duda
def test_get_image(mock_backend):
    # Prepare the test image data
    image_data = b'test_image_data'
    encoded_image_data = base64.b64encode(image_data).decode("utf-8")

    # Set up the mock for the blob
    mock_blob = MagicMock(download_as_bytes=MagicMock(return_value=image_data))
    mock_backend.content_bucket.blob.return_value = mock_blob

    # Test the get_image function
    filepath = 'character-images/'
    page_name = 'Mario'
    result = mock_backend.get_image(filepath, page_name)

    # Assert the expected image data is returned
    assert result == encoded_image_data
