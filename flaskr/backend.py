from google.cloud import storage
import os


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
        blob = self.content_bucket.blob("pages/" + name + ".html")

        # Check if the blob exists
        if not blob.exists():
            return None

        # Download the blob content as text
        blob_content = blob.download_as_string().decode("utf-8")

        return blob_content


    def get_all_page_names(self):
        prefix = 'pages/'
        delimiter = '/'
        blob_list = self.content_bucket.list_blobs(prefix=prefix, delimiter=delimiter)
        page_names = [blob.name.split('/')[-1].split('.')[0] for blob in blob_list]
        return page_names



    # I changed this method's parameters!! added path and name
    def upload(self, file_path, file_name):
        # Create the blob with the given name
        blob = self.content_bucket.blob(file_name)
        # Upload the file's content to the blob
        blob.upload_from_file(file_path)
        pass

    def sign_up(self):
        pass

    def sign_in(self):
        pass

    def get_image(self):
        pass 