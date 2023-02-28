# TODO(Project 1): Implement Backend according to the requirements.
from google.cloud import storage
import os
class Backend:
    
    # when the class is created, should it have a parameter or nothing?
    # chan I choose any name for the bucket?
    def __init__(self):
        self.storage_client = storage.Client()
        self.bucket_name = "Smash-Characters"
        # Instantiates a cliesnt
        self.bucket = self.storage_client.create_bucket(self.bucket_name)
        # add the characters to the bucket
        pages_folder = os.path.join(os.path.dirname(__file__), "pages")
        files_in_folder = os.listdir(pages_folder)

        #go through the files and create a blob for each one and upload it. 
        for file in files_in_folder:
            blob = self.bucket.blob(file)
            with open(os.path.join(pages_folder,file), "rb") as f:
                blob.upload_from_file(f)
        
        pass
        
    def get_wiki_page(self, name):
        # get the blob with the given name O(log(n))
        blob = self.bucket.blob(name)

        blob_content = blob.download_as_string().decode("utf-8")
        return blob_content

    def get_all_page_names(self):
        # get a list of all the blobs in the bucket
        blobs = self.bucket.list_blobs()
        page_names = []

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

