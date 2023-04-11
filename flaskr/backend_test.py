import pytest, hashlib, base64
from werkzeug.security import generate_password_hash
from unittest.mock import MagicMock
from .backend import Backend


# Mocking Google Cloud Storage and Datastore client
@pytest.fixture
def mock_backend():
    backend = Backend()
    backend.client = MagicMock()
    backend.content_bucket = MagicMock()
    backend.users_bucket = MagicMock()
    return backend


def test_get_wiki_page(mock_backend):
    mock_backend.client.get.return_value = {
        'Name': 'Mario',
        'Info': 'Plumber from the Mushroom Kingdom',
        'World': 'Super Mario Bros.'
    }

    result = mock_backend.get_wiki_page('Mario')
    assert result == 'Mario|Plumber from the Mushroom Kingdom|Super Mario Bros.'


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


def test_upload(mock_backend):
    mock_backend.content_bucket.blob.return_value = MagicMock(
        upload_from_file=MagicMock())

    f = MagicMock(content_type='image/png', tell=MagicMock(return_value=0))
    mock_backend.upload(f, 'Mario', 'A character from the Mario series.',
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

    # Assert the content_bucket.blob and download_as_bytes were called with appropriate arguments
    mock_backend.content_bucket.blob.assert_called_with(filepath + page_name +
                                                        ".png")
    mock_blob.download_as_bytes.assert_called()


# import pytest
# from unittest.mock import MagicMock, patch
# from .backend import Backend

# # Sample data for testing
# sample_character = {
#     'Name': 'Mario',
#     'Info': 'A character from the Mario series.',
#     'World': 'Mushroom Kingdom'
# }

# @pytest.fixture
# def backend():
#     return Backend()

# def test_get_wiki_page(backend):
#     with patch('google.cloud.datastore.Client.get') as mock_get:
#         mock_get.return_value = sample_character
#         result = backend.get_wiki_page('Mario')
#         assert result == 'Mario|A character from the Mario series.|Mushroom Kingdom'

# def test_get_all_page_names(backend):
#     with patch('google.cloud.datastore.Client.query') as mock_query:
#         mock_fetch = MagicMock()
#         mock_fetch.return_value = [
#             MagicMock(key=MagicMock(name='Mario')),
#             MagicMock(key=MagicMock(name='Luigi'))
#         ]

#         mock_query.return_value = MagicMock(fetch=mock_fetch)
#         result = backend.get_all_page_names()
#         assert result == ['Mario', 'Luigi']

# def test_upload(backend):
#     with patch('google.cloud.storage.Client.get_bucket') as mock_get_bucket:
#         with patch('google.cloud.datastore.Client.put') as mock_put:
#             mock_content_bucket = MagicMock()
#             mock_content_bucket.blob.return_value = MagicMock(upload_from_file=MagicMock())
#             mock_get_bucket.return_value = mock_content_bucket

#             f = MagicMock(content_type='image/png', tell=MagicMock(return_value=0))
#             backend.upload(f, 'Mario', 'A character from the Mario series.', 'Mushroom Kingdom')

#             mock_content_bucket.blob.return_value.upload_from_file.assert_called_with(f)
#             mock_put.assert_called()

# def test_sign_up(backend):
#     with patch('google.cloud.datastore.Client.get') as mock_get:
#         with patch('google.cloud.datastore.Client.put') as mock_put:
#             mock_get.return_value = None
#             result = backend.sign_up('new_user', 'new_password')
#             assert result == True
#             mock_put.assert_called()

# def test_sign_in(backend):
#     with patch('google.cloud.datastore.Client.get') as mock_get:
#         mock_get.return_value = {'hashed_password': 'bc5b6db1be6b8a0375b6c3b6a5f6c5e5d5c5b5a5b5b5b5'}
#         result = backend.sign_in('existing_user', 'existing_password')
#         assert result == True

#         mock_get.return_value = None
#         result = backend.sign_in('nonexistent_user', 'password')
#         assert result == -1
