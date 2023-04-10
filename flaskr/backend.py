from google.cloud import datastore
import os, base64, csv
import hashlib


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
    """

    def __init__(self) -> None:
        self.client = datastore.Client('sds-project-nbs-wiki')

    def get_wiki_page(self, name: str) -> str:
        key = self.client.key('Character', name)
        wiki_page = self.client.get(key)
        if wiki_page:
            character_name = wiki_page['Name']
            info = wiki_page['Info']
            world = wiki_page['World']
            return f"{character_name}|{info}|{world}"
        return None



    def get_all_page_names(self) -> list[str]:
        query = self.client.query(kind='Character')
        results = list(query.fetch())
        return [entity.key.name for entity in results]


    # I changed this method's parameters!! added path and name
    def upload(self, f, char_name, char_info):
        f.save("imageTemp")
        with open("imageTemp", "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

        wiki_page_key = self.client.key('Character', char_name)
        wiki_page = datastore.Entity(key=wiki_page_key)
        wiki_page.update({
        'content': char_info,
        'image': encoded_image
        })
        self.client.put(wiki_page)


    def sign_up(self, new_user_name: str, new_password: str) -> bool:
        user_key = self.client.key('User', new_user_name)
        user = self.client.get(user_key)
        if user:
            return False

        salted_password = f"{new_user_name}nbs{new_password}"
        hashed_password = hashlib.blake2b(salted_password.encode()).hexdigest()

        new_user = datastore.Entity(key=user_key)
        new_user.update({
            'hashed_password': hashed_password
        })
        self.client.put(new_user)
        return True


    def sign_in(self, username: str, password: str) -> bool or int:
        user_key = self.client.key('User', username)
        user = self.client.get(user_key)
        if not user:
            return -1

        hashed_password = user['hashed_password']
        verify_password = hashlib.blake2b(f"{username}nbs{password}".encode()).hexdigest()
        return verify_password == hashed_password


    # def get_image(self, page_name: str) -> str:
    #     key = self.client.key('Character', page_name)
    #     wiki_page = self.client.get(key)
    #     if wiki_page:
    #         return wiki_page['image']
    #     return None


    def allowed_file(self, filename):
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    # #Extra
    # def get_authors(self):
    #     blobs = self.content_bucket.list_blobs(prefix='authors/')
    #     authors_list = []
    #     for blob in blobs:
    #         image_data = blob.download_as_bytes()
    #         encoded_image_data = base64.b64encode(image_data).decode("utf-8")
    #         authors_list.append(encoded_image_data)
    #     return authors_list
