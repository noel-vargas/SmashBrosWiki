import pytest, hashlib, base64
from werkzeug.security import generate_password_hash
from unittest.mock import MagicMock, Mock
from .backend import Backend
import json


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


# def test_upload(mock_backend):
#     mock_backend.content_bucket.blob.return_value = MagicMock(
#         upload_from_file=MagicMock())

#     f = MagicMock(content_type='image/png', tell=MagicMock(return_value=0))
#     mock_backend.upload(f, 'Mario', 'A character from the Mario series.',
#                         'Mushroom Kingdom')

#     mock_backend.content_bucket.blob.assert_called_with(
#         'character-images/Mario.png')
#     mock_backend.client.put.assert_called()


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


def test_get_query_pages(mock_backend):
    mock_backend.get_all_page_names = MagicMock(return_value=["Mario", "Link"])
    mock_backend.get_wiki_page = MagicMock()
    mock_backend.get_wiki_page.side_effect = [
        'Mario|Plumber from the Mushroom Kingdom|Super Mario Bros.',
        'Link|I have a boomerang|La Leyenda de Zelda'
    ]
    result = mock_backend.get_query_pages("Link")
    assert result == ["Link"]

    mock_backend.get_wiki_page.side_effect = [
        'Mario|Plumber from the Mushroom Kingdom|Super Mario Bros.',
        'Link|I have a boomerang|La Leyenda de Zelda'
    ]
    result = mock_backend.get_query_pages("Mario")
    assert result == ["Mario"]


def test_rank_pages(mock_backend):
    mock_backend.tracker.get_upvotes.side_effect = [2, 8, 5, 7, 10]
    result = mock_backend.rank_pages(
        ["Lucario", "Mario", "Link", "Ness", "Lucas"])
    assert result == ["Lucas", "Mario", "Ness", "Link", "Lucario"]

    mock_backend.tracker.get_upvotes.side_effect = [5, 8, 10, 2, 7]
    result = mock_backend.rank_pages(
        ["Lucario", "Mario", "Link", "Ness", "Lucas"])
    assert result == ["Link", "Mario", "Lucas", "Lucario", "Ness"]


def test_get_worlds(mock_backend):
    # Create sample world entities
    world_entities = [
        {
            "world_name": "Super Mario Bros."
        },
        {
            "world_name": "The Legend of Zelda"
        },
        {
            "world_name": "Sonic the Hedgehog"
        },
    ]

    # Set up the mock backend to return the world entities
    mock_backend.client.query.return_value.fetch.return_value = world_entities

    # Test the get_worlds function
    result = mock_backend.get_worlds()
    expected_result = [
        "Super Mario Bros.",
        "The Legend of Zelda",
        "Sonic the Hedgehog",
    ]
    assert result == expected_result


def test_get_worlds_no_worlds(mock_backend):
    # Set up the mock backend to return an empty list
    mock_backend.client.query.return_value.fetch.return_value = []

    # Test the get_worlds function when no worlds exist
    result = mock_backend.get_worlds()
    assert result == []


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


def test_get_characters_by_world(mock_backend):
    # Create sample world entities
    world_entities = [
        {
            "world_name": "Super Mario Bros.",
            "characters": ["Mario"]
        },
        {
            "world_name": "The Legend of Zelda",
            "characters": ["Link"]
        },
        {
            "world_name": "Sonic the Hedgehog",
            "characters": ["Sonic", "Luna"]
        },
    ]

    # Test the get_characters_by_world function
    mock_backend.client.query.return_value.fetch.return_value = [
        world_entities[0]
    ]
    result = mock_backend.get_characters_by_world("Super Mario Bros.")
    assert result == ["Mario"]

    mock_backend.client.query.return_value.fetch.return_value = [
        world_entities[1]
    ]
    result = mock_backend.get_characters_by_world("The Legend of Zelda")
    assert result == ["Link"]

    mock_backend.client.query.return_value.fetch.return_value = [
        world_entities[2]
    ]
    result = mock_backend.get_characters_by_world("Sonic the Hedgehog")
    assert result == ["Sonic", "Luna"]

    mock_backend.client.query.return_value.fetch.return_value = []
    result = mock_backend.get_characters_by_world("Nonexistent World")
    assert result == []
