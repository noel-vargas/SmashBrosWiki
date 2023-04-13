import pytest
from google.cloud import datastore
from unittest.mock import MagicMock
from .tracker import Tracker


# Mocking Datastore client
@pytest.fixture
def mock_tracker():
    tracker = Tracker(MagicMock(), MagicMock())

    # Mock the key method
    def key_mock(*args, **kwargs):
        key = MagicMock()
        key.kind = args[0]
        key.name = args[1]
        return key

    tracker.key = key_mock
    return tracker


def test_add_upload(mock_tracker):

    def get_side_effect(key):
        if key.kind == "UserUploads":
            if key.name == "sebagabs":
                return {"uploads": ["Ryu"]}
            if key.name == "Noel":
                return None
        if key.kind == "PageUploader":
            if key.name == "Sheik":
                return {"uploader": "sebagabs"}
            if key.name == "Shulk":
                return {"uploader": "sebagabs"}
        return None

    mock_tracker.client.get.side_effect = get_side_effect
    
    mock_transaction = MagicMock()
    mock_transaction.__enter__.return_value = mock_transaction

    # User uploading second page.
    mock_tracker.client.transaction.return_value = mock_transaction
    mock_tracker.add_upload("sebagabs", "Sheik")

    uploaded = mock_transaction.put.call_args.args[0]  # First Argument passed in to `put` (a dict)
    assert uploaded["uploader"] == "sebagabs"

    # User uploading third page.
    mock_tracker.client.transaction.return_value = mock_transaction
    mock_tracker.add_upload("sebagabs", "Shulk")

    uploaded = mock_transaction.put.call_args.args[0]  # First Argument passed in to `put` (a dict)
    assert uploaded["uploader"] == "sebagabs"

    # User uploading for the first time.
    mock_tracker.client.transaction.return_value = mock_transaction
    mock_tracker.add_upload("Noel", "Villager")

    uploaded = mock_transaction.put.call_args.args[0]  # First Argument passed in to `put` (a dict)
    assert uploaded["uploader"] == "Noel"


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


def test_upvote_page(mock_tracker):

    def get_side_effect(key):
        if key.name == "Ness":
            return {"upvotes": ["sebagabs"]}

    mock_tracker.client.get.side_effect = get_side_effect
    
    mock_transaction = MagicMock()
    mock_transaction.__enter__.return_value = mock_transaction

    # User upvoted Ness page.
    mock_tracker.client.transaction.return_value = mock_transaction
    mock_tracker.upvote_page("Ness", "sebagabs")

    uploaded = mock_transaction.put.call_args.args[0]  # First Argument passed in to `put` (a dict)
    # Either .remove or .append were done, so dict remains empty.
    assert uploaded["upvotes"] == []

    result = mock_tracker.upvote_page("Ness", "sebagabs")
    assert result == "You had already upvoted this page. Removed upvote from page."

    result = mock_tracker.upvote_page("Ness", "Noel")
    assert result == "Page upvoted!"


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


def test_add_comment(mock_tracker):

    def get_side_effect(key):
        if key.name == "Ness":
            return { "comments": {
                "0": {"sebagabs": "I love Ness."},
                "1": {"Noel": "Me too!"}
            }}
        return None

    mock_tracker.client.get.side_effect = get_side_effect
    
    mock_transaction = MagicMock()
    mock_transaction.__enter__.return_value = mock_transaction

    # Commenting on a page with previous comments.
    mock_tracker.client.transaction.return_value = mock_transaction
    mock_tracker.add_comment("Ness", "bryan", "EarthBound sucks!")

    uploaded = mock_transaction.put.call_args.args[0]  # First Argument passed in to `put` (a dict)
    assert uploaded["comments"] ==  str({"0": {"sebagabs": "I love Ness."}, "1": {"Noel": "Me too!"}, "2": {"bryan": "EarthBound sucks!"}})

    # Commenting on a page with no comments; leaving first comment on page.
    mock_tracker.client.transaction.return_value = mock_transaction
    mock_tracker.add_comment("Ryu", "sebagabs", "I haven't played Street Fighter.")

    uploaded = mock_transaction.put.call_args.args[0]  # First Argument passed in to `put` (a dict)
    assert uploaded["comments"] == str({"0": {"sebagabs": "I haven`t played Street Fighter."}})


def test_get_comments(mock_tracker):
    
    def get_side_effect(key):
        if key.name == "Ness":
            return { "comments": {
                "0": {"sebagabs": "I love Ness."},
                "1": {"Noel": "Me too!"}
            }}
        return None

    mock_tracker.client.get.side_effect = get_side_effect

    result = mock_tracker.get_comments("Ness")
    assert result == {"0": {"sebagabs": "I love Ness."}, "1": {"Noel": "Me too!"}}

    result = mock_tracker.get_comments("Lucario")
    assert result == None
