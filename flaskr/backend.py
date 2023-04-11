from google.cloud import datastore, storage
import os, base64, csv
import hashlib
""" Provides a backend implementation for the Super Smash Bros. wiki project using Google Cloud Storage (GCS) and Google Cloud Datastore """


class Backend:
    """Provides an interface for underlying GCS buckets.
    
    Handles operations to and from Google Cloud Storage buckets,
    to either download, upload, or verify data.
    
    Attributes:
        content_bucket_name:
            A string with the name of the bucket that stores the wiki's content.
        users_bucket_name: 
            A string with the name of the bucket that stores the users and their passwords.
        content_bucket:
            A Google Cloud Storage bucket that stores the wiki's content.
        users_bucket:
            A Google Cloud Storage bucket that stores the users and their passwords.
        client:
            An instance of `datastore.Client` that represents the connection to
            the Google Cloud Datastore service for the project 'sds-project-nbs-wiki'.
    """

    def __init__(self) -> None:
        self.client = datastore.Client('sds-project-nbs-wiki')
        self.content_bucket_name = "nbs-wiki-content"
        self.users_bucket_name = "nbs-usrs-psswrds"
        self.content_bucket = storage.Client().get_bucket(
            self.content_bucket_name)
        self.users_bucket = storage.Client().get_bucket(self.users_bucket_name)

    def get_wiki_page(self, name: str) -> str:
        """Get a wiki page from the Datastore by name.
        
        Args:
            name: A string representing the name of the character to get.
        
        Returns:
            A string representing the character's information in the format "character_name|info|world",
            or None if the character is not found.
        """
        key = self.client.key('Character', name)
        wiki_page = self.client.get(key)
        if wiki_page:
            character_name = wiki_page['Name']
            info = wiki_page['Info']
            world = wiki_page['World']
            return f"{character_name}|{info}|{world}"
        return None

    def get_all_page_names(self) -> list[str]:
        """ Get a list of all character names from the Datastore.
        
            Returns:
            A list of strings representing all the character names.
        """
        query = self.client.query(kind='Character')
        results = list(query.fetch())
        return [entity.key.name for entity in results]

    # I changed this method's parameters!! added path and name

    def upload(self, f, char_name, char_info, char_world):
        """Uploads an image and character info to the GCS bucket and Datastore.

            Args:
            f: A file object representing the image to be uploaded.
            char_name: A string representing the name of the character.
            char_info: A string representing the info of the character.
            char_world: A string representing the world of the character.
        """
        # Save the image to the GCS bucket
        image_blob = self.content_bucket.blob("character-images/" + char_name +
                                              ".png")
        image_blob.upload_from_file(f, content_type=f.content_type)

        # Save the character info to the Datastore
        wiki_page_key = self.client.key('Character', char_name)
        wiki_page = datastore.Entity(key=wiki_page_key)
        wiki_page.update({
            'Name': char_name,
            'Info': char_info,
            'World': char_world,
        })
        self.client.put(wiki_page)

    def sign_up(self, new_user_name: str, new_password: str) -> bool:
        """Registers a new user with a username and password.

        Args:
            new_user_name: A string representing the username of the new user.
            new_password: A string representing the password of the new user.

        Returns:
            A boolean value indicating whether the registration was successful
            (True) or not (False).
        """
        user_key = self.client.key('User', new_user_name)
        user = self.client.get(user_key)
        if user:
            return False

        salted_password = f"{new_user_name}nbs{new_password}"
        hashed_password = hashlib.blake2b(salted_password.encode()).hexdigest()

        new_user = datastore.Entity(key=user_key)
        new_user.update({'hashed_password': hashed_password})
        self.client.put(new_user)
        return True

    def sign_in(self, username: str, password: str) -> bool or int:
        """Sign in an existing user with the provided username and password.

        Args:
            username: A string representing the username of the existing user.
            password: A string representing the password of the existing user.

        Returns:
            A boolean value indicating whether the sign-in was successful (True) or not (False), or -1 if the user was not found.
        """
        user_key = self.client.key('User', username)
        user = self.client.get(user_key)
        if not user:
            return -1

        hashed_password = user['hashed_password']
        verify_password = hashlib.blake2b(
            f"{username}nbs{password}".encode()).hexdigest()
        return verify_password == hashed_password

    # def hash_password(self, username: str, password: str) -> str:
    #     salted_password = f"{username}nbs{password}"
    #     hashed_password = hashlib.blake2b(salted_password.encode()).hexdigest()
    #     return hashed_password

    def get_image(self, filepath: str, page_name: str) -> str:
        """Get the encoded image data of a character image from the GCS bucket.

        Args:
            filepath: A string representing the file path of the character image in the GCS bucket.
            page_name: A string representing the name of the character whose image to retrieve.

        Returns:
            A string representing the encoded image data of the character image.
        """
        blob = self.content_bucket.blob(filepath + page_name + ".png")
        image_data = blob.download_as_bytes()
        encoded_image_data = base64.b64encode(image_data).decode("utf-8")
        return encoded_image_data

    def allowed_file(self, filename):
        """Check if a given file name has an allowed extension.

        Args:
            filename: A string representing the name of the file to check.

        Returns:
            A boolean value indicating whether the file has an allowed extension (True) or not (False).
        """
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    #Extra
    def get_authors(self):
        """Get the encoded image data of authors from the GCS bucket.

        Returns:
            A list of strings representing the encoded image data of authors.
        """
        blobs = self.content_bucket.list_blobs(prefix='authors/')
        authors_list = []
        for blob in blobs:
            image_data = blob.download_as_bytes()
            encoded_image_data = base64.b64encode(image_data).decode("utf-8")
            authors_list.append(encoded_image_data)
        return authors_list
