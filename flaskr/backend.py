from google.cloud import storage
import os, base64
import hashlib


class Backend:
    # When the class is created, should it have a parameter or nothing?
    # Can I choose any name for the content_bucket?
    def __init__(self):
        self.content_bucket_name = 'nbs-wiki-content'
        self.users_bucket_name = 'nbs-usrs-psswrds'

        self.content_bucket = storage.Client().get_bucket(self.content_bucket_name)
        self.users_bucket = storage.Client().get_bucket(self.users_bucket_name)
        
    def get_wiki_page(self, name):
        # Get the blob with the given name
        blob = self.content_bucket.blob("pages/" + name + ".csv")

        # Check if the blob exists
        if not blob.exists():
            return None

        # Download the blob content as text
        blob_content = blob.download_as_string().decode("utf-8")
        

        return blob_content


    def get_all_page_names(self, prefix):
        delimiter = '/'
        blob_list = self.content_bucket.list_blobs(prefix=prefix, delimiter=delimiter)
        page_names = [blob.name.split('/')[-1].split('.')[0] for blob in blob_list]
        return page_names



    # I changed this method's parameters!! added path and name
    def upload(self, f):
        # Create the blob with the given name
        f.save("temp")
        blob = self.content_bucket.blob("character-images/" + f.filename)
        # Upload the file's content to the blob
        blob.upload_from_filename("temp")
        f.close()
        pass

    def sign_up(self, new_user_name: str, new_password: str):
        """Adds new to user to GCP Bucket."""
        # The ID of your new GCS object
        blob_name = new_user_name
        blob = self.users_bucket.blob(blob_name)
        
        if blob.exists():
            return False  # User name already exsists. TODO Determine appropiate action.

        salted_password = f"{new_user_name}nbs{new_password}"
        hashed_password = hashlib.blake2b(salted_password.encode()).hexdigest()

        with blob.open("w") as f:
            f.write(hashed_password)
        return True

    def sign_in(self, username: str, password: str):
        """Determines if user provided correct information to log in."""
        blob_name = username
        blob = self.users_bucket.get_blob(blob_name)

        if not blob:
            return -1  # User does not exsist. TODO Determine appropiate action.

        hashed_password = ""
        with blob.open("r") as f:
            hashed_password = f.read()
        
        verify_passwod = hashlib.blake2b(f"{username}nbs{password}".encode()).hexdigest()
        return verify_passwod == hashed_password

    def get_image(self,filepath, page_name):
        blob = self.content_bucket.blob(filepath + page_name + ".png")
        image_data = blob.download_as_bytes()
        encoded_image_data = base64.b64encode(image_data).decode('utf-8')
        return encoded_image_data
         


    #Extra
    def get_authors(self):
        blobs = self.content_bucket.list_blobs(prefix='authors/')
        authors_list = []
        for blob in blobs:
            image_data = blob.download_as_bytes()
            encoded_image_data = base64.b64encode(image_data).decode('utf-8')
            authors_list.append(encoded_image_data)
        return authors_list
