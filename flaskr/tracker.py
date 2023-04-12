from google.cloud import datastore


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

    def __init__(self, client=None):
        if client is None:
            client = datastore.Client("sds-project-nbs-wiki")
        self.client = client
    
    def add_upload(self, username: str, pagename: str) -> None:
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
        with self.client.transaction() as trans:
            user_key = self.client.key("UserUploads", username)
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
            page_key = self.client.key("PageUploader", pagename)
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
        page_key = self.client.key("PageUploader", pagename)
        page_uploader = self.client.get(page_key)
        return page_uploader["uploader"] if page_uploader else None

    def get_pages_uploaded(self, username: str) -> list[str]:
        """
        Get a list of pages uploaded by user with parameter username.
        
        ---
        Args:
            username:
                Sting representing username of a user.

        Returns:
            List of strings representing the names of uploaded pages.
        """
        user_key = self.client.key("UserUploads", username)
        user_uploads = self.client.get(user_key)
        return user_uploads["uploads"] if user_uploads else None
