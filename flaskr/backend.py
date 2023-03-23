from google.cloud import storage
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
        """Initializes an instance that can interact with the GCS."""
        self.content_bucket_name = "nbs-wiki-content"
        self.users_bucket_name = "nbs-usrs-psswrds"
        self.content_bucket = storage.Client().get_bucket(
            self.content_bucket_name)
        self.users_bucket = storage.Client().get_bucket(self.users_bucket_name)

    def get_wiki_page(self, name: str) -> str:
        """Gets an uploaded page from the content bucket.
        
        Args:
            name:
                A string with the page name.

        Returns:
            A strings with the pages content.
        """
        blob = self.content_bucket.blob("pages/" + name + ".csv")
        if not blob.exists():
            return None
        blob_content = blob.download_as_string().decode(
            "utf-8")  # Download the blob content as text
        return blob_content

    def get_all_page_names(self, prefix: str) -> list[str]:
        """Gets the names of all pages from the content bucket.

        Gets all the blobs inside the content bucket as a string
        and then splits it into a list of strings.

        Args:
            prefix:
                A string with a prefix for a directory.

        Returns:
            A list of strings containing all the pages' names.
        """
        delimiter = '/'
        blob_list = self.content_bucket.list_blobs(prefix=prefix,
                                                   delimiter=delimiter)
        page_names = [
            blob.name.split('/')[-1].split('.')[0] for blob in blob_list
        ]
        return page_names

    # I changed this method's parameters!! added path and name
    def upload(self, f, char_name, char_info):
        # Create the blob with the given name
        f.save("imageTemp")
        blob = self.content_bucket.blob("character-images/" + char_name +
                                        ".png")
        # Upload the file's content to the blob
        blob.upload_from_filename("imageTemp")
        f.close()
        with open("infoTemp.csv", 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([char_name, char_info])
            file.close()
        blob = self.content_bucket.blob("pages/" + char_name + ".csv")
        blob.upload_from_filename("infoTemp.csv")

        pass

    def sign_up(self, new_user_name: str, new_password: str) -> bool:
        """Adds user data if it does not exist along with a hashed password.

        Creates a new wiki user by adding user data to the users bucket in GCS.
        Before adding the user, check if the user does not exist already. Then 
        hashes the password. Finally, it creates and adds the user.
        
        Args:
            new_user_name:
                A string with the new user's username.
            new_password:
                A string representing the new user's password (without hashing).

        Returns:
            True if the user was added succesfully, or False if the user already exists.
        """
        blob_name = new_user_name
        blob = self.users_bucket.blob(blob_name)
        if blob.exists():
            return False  # User name already exsists.
        salted_password = f"{new_user_name}nbs{new_password}"
        hashed_password = hashlib.blake2b(salted_password.encode()).hexdigest()
        with blob.open("w") as f:
            f.write(hashed_password)  # Creates new user with hashed password.
        return True

    def sign_in(self, username: str, password: str) -> bool or int:
        """Checks if a password, when hashed, matches the password in the user bucket.
        
        Checks if the user trying to log in exists. If it exists, determines if user 
        provided correct information to log in by taking the input password, hashing it
        and chekcing it against the GCS bucket. 

        Args:
            username:
                A string with a user's username.
            password:
                A string with a user's password (without hashing).

        Returns:
            -1 if the username is not found in the GCS bucket (it does not exist).
            True if the user exists and provided the correct password, or False
            if they provided an incorrect password.
        """
        blob_name = username
        blob = self.users_bucket.get_blob(blob_name)
        if not blob:
            return -1  # User does not exsist.
        hashed_password = ""
        with blob.open("r") as f:
            hashed_password = f.read(
            )  # Get user's hashed password from bucket.
        verify_passwod = hashlib.blake2b(
            f"{username}nbs{password}".encode()).hexdigest()
        return verify_passwod == hashed_password  # Check if passwords match.

    def get_image(self, filepath: str, page_name: str) -> str:
        """Gets an image from the content bucket.

        Gets an image from the GCS content bucket by downloading its information
        in bytes and encoding it into a string. That string is then decoded and used
        to render the image.
        
        Args:
            filepath:
                A string with the path to where to look for the image.
            page_name:
                A string with the name of the page which the image is for.

        Returns:
            A string representing the image's decoded data.
        """
        blob = self.content_bucket.blob(filepath + page_name + ".png")
        image_data = blob.download_as_bytes()
        encoded_image_data = base64.b64encode(image_data).decode("utf-8")
        return encoded_image_data

    def allowed_file(self, filename):
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    #Extra
    def get_authors(self):
        blobs = self.content_bucket.list_blobs(prefix='authors/')
        authors_list = []
        for blob in blobs:
            image_data = blob.download_as_bytes()
            encoded_image_data = base64.b64encode(image_data).decode("utf-8")
            authors_list.append(encoded_image_data)
        return authors_list
