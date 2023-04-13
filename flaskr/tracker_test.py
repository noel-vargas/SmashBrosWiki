import pytest
from unittest.mock import MagicMock
from .tracker import Tracker


# Mocking Datastore client
@pytest.fixture
def mock_tracker():
    tracker = Tracker(MagicMock(), MagicMock())

    # Mock the key method
    def key_mock(*args, **kwargs):
        key = MagicMock()
        key.name = args[1]
        return key

    tracker.key = key_mock
    return tracker


# def test_add_upload(mock_tracker):
#     username, pagename = "tracker_tester", "TestPage"
#     uploads_before, uploads_after = mock_tracker.add_upload(username, pagename)
#     assert len(uploads_before) + 1 == len(uploads_after)

# def test_upload(mock_backend):
#     mock_backend.content_bucket.blob.return_value = MagicMock(
#         upload_from_file=MagicMock())

#     f = MagicMock(content_type='image/png', tell=MagicMock(return_value=0))
#     mock_backend.upload("tester", f, 'Mario', 'A character from the Mario series.',
#                         'Mushroom Kingdom')

#     mock_backend.content_bucket.blob.assert_called_with(
#         'character-images/Mario.png')
#     mock_backend.client.put.assert_called()


def test_get_page_uploader(mock_tracker):
    # Configure the tracker . . . TODO
    def get_side_effect(key):
        if key.name == "Ness":
            return {"uploader": "sebagabs"}
        return None

    mock_tracker.client.get.side_effect = get_side_effect

    result = mock_tracker.get_page_uploader("Ness")
    assert result == "sebagabs"

    result = mock_tracker.get_page_uploader("Noel")
    assert result is None


def test_get_pages_uploaded(mock_tracker):
    # Configure the tracker . . . TODO
    def get_side_effect(key):
        if key.name == "sebagabs":
            return {"uploads": ["Lucas", "Ness"]}
        return None

    mock_tracker.client.get.side_effect = get_side_effect

    result = mock_tracker.get_pages_uploaded("sebagabs")
    assert result == ["Lucas", "Ness"]

    result = mock_tracker.get_pages_uploaded("Noel")
    assert result is None


# def test_upvote_page(mock_tracker):
#     def get_side_effect(key):
#         if key.name == "Ness":
#             return {"upvotes" : ["sebagabs"]}
#     mock_tracker.client.transaction.side_effect = get_side_effect

#     result = mock_tracker.upvote_page(pagname, username)
#     assert result == ""


def test_get_upvotes(mock_tracker):
    # Configure the tracker . . . TODO
    def get_side_effect(key):
        if key.name == "Ryu":
            return {"upvotes": ["sebagabs", "Noel"]}
        return None

    mock_tracker.client.get.side_effect = get_side_effect

    result = mock_tracker.get_upvotes("Ryu")
    assert result == 2

    result = mock_tracker.get_upvotes("Lucario")
    assert result == 0
