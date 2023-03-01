# TODO(Project 1): Implement Backend according to the requirements.
from google.cloud import storage
import os
class Backend:
    
    # when the class is created, should it have a parameter or nothing?
    # chan I choose any name for the bucket?
    def __init__(self):
        self.storage_client = storage.Client("sds-project-nbs-wiki")
        self.bucket_name = "nbs-wiki-content"
        # Instantiates a cliesnt
        self.bucket = self.storage_client.create_bucket(self.bucket_name)
        
    def get_wiki_page(self, name):
        # get the blob with the given name O(log(n))
        blob = self.bucket.blob(name)

        # check if the blob exists
        if not blob.exists():
            return None

        blob_content = blob.download_as_string().decode("utf-8")
        return blob_content


    def get_all_page_names(self):
        # get a list of all the blobs in the bucket
        blobs = self.bucket.list_blobs()
        page_names = []

        if len(blobs) ==0:
            return None
        for blob in blobs:
            page_names.append(blob.name)

        return page_names

    # I changed this methods parameter!! added path and name
    def upload(self, file_path, file_name):
        #create the blob with the given name
        blob = self.bucket.blob(file_name)
        #upload the file's content to the blob
        blob.upload_from_file(file_path)
        pass

    def sign_up(self):
        pass

    def sign_in(self):
        pass

    def get_image(self):
        pass

