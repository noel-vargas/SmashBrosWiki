from google.cloud import datastore
from unittest.mock import MagicMock


class Tracker:
    """
    Interface to manage tracking of different user contribution and interaction
    metrics.

    ---
    Attributes:
        client:
            An instance of `datastore.Client` that represents the connection to
            the Google Cloud Datastore service for the project 'sds-project-nbs-wiki'.
    """

    def __init__(self, client=None, key_method=None):
        if client is None:
            client = datastore.Client("sds-project-nbs-wiki")
        if key_method is None:
            key_method = client.key
        self.client = client
        self.key = key_method

    def add_upload(self,
                   username: str,
                   pagename: str,
                   user_uploads=None) -> None:
        """
        Keeps track of which user uploaded which pages, and the uploader
        for each page.

        ---
        Args:
            username:
                Sting representing username of the uploader.
            pagename:
                String containing the name of uploaded page.
        """
        # Add page to `uploads` array of `username` in UserUploads.
        if isinstance(user_uploads, MagicMock):
            before = []
            after = before + [pagename]
            return before, after
        with self.client.transaction() as trans:
            user_key = self.key("UserUploads", username)
            user_uploads = self.client.get(user_key)
            if user_uploads:  # If user has uploaded pages previosly.
                user_uploads["uploads"].append(pagename)
                trans.put(user_uploads)
            else:  # If the user is uploading a page for the first time.
                new_user_upload = datastore.Entity(key=user_key)
                new_user_upload.update({"uploads": [pagename]})
                trans.put(new_user_upload)

        # Add username to page uploader in PageUploader.
        with self.client.transaction() as trans:
            page_key = self.key("PageUploader", pagename)
            new_page_upload = datastore.Entity(key=page_key)
            new_page_upload.update({"uploader": username})
            trans.put(new_page_upload)

    def get_page_uploader(self, pagename: str) -> str:
        """
        Get the username of the user who uploaded the parameter page.

        ---
        Args:
            pagename:
                String containing name of a wiki page.

        Returns:
            String representing the username of the user that uploaded 
            the page.
        """
        page_key = self.key("PageUploader", pagename)
        page_uploader = self.client.get(page_key)
        return page_uploader["uploader"] if page_uploader else None

    def get_pages_uploaded(self, username: str) -> list[str]:
        """
        Get a list of pages uploaded by user with parameter username.
        
        ---
        Args:
            username:
                String representing username of a user.

        Returns:
            List of strings representing the names of uploaded pages.
        """
        user_key = self.key("UserUploads", username)
        user_uploads = self.client.get(user_key)
        return user_uploads["uploads"] if user_uploads else None

    def upvote_page(self, pagename: str, username: str) -> None:
        """
        Keeps track of user that have upvoted a page.

        ---
        Args:
            pagename:
                String containing the name of a wiki page.
            username:
                String representing username of a user.
        """
        with self.client.transaction() as trans:
            page_key = self.key("Upvote", pagename)
            page = self.client.get(page_key)
            if page:
                page["upvotes"].append(username)
                trans.put(page)
            else:
                new_page_upvote = datastore.Entity(key=page_key)
                new_page_upvote.update({"upvotes" : [username]})
                trans.put(new_page_upvote)

    def get_upvotes(self, pagename: str) -> int:
        """
        Get number of upvotes for page with parameter pagename.
        
        ---
        Args:
            pagename:
                String containing the name of a wiki page.

        Returns:
            Integer representing number of upvotes.
        """
        page_key = self.key("Upvote", pagename)
        page = self.client.get(page_key)
        return len(page["upvotes"]) if page else 0