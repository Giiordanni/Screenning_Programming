import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, storage
from werkzeug.utils import secure_filename  
from google.api_core.exceptions import GoogleAPIError
load_dotenv()

storage_bucket_name = os.getenv("FIREBASE_STORAGE_BUCKET")
if not storage_bucket_name:
    raise ValueError("FIREBASE_STORAGE_BUCKET environment variable is not set.")

cred = credentials.Certificate('screen-programing.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': storage_bucket_name
})

def upload_image_to_firebase(file_stream, destination_blob_name, max_size_mb=16, allowed_extensions=None):
    if allowed_extensions is None:
        allowed_extensions = ['jpg', 'jpeg', 'png', 'gif']
    
    try:
        file_size_mb = len(file_stream.getvalue()) / (1024 * 1024)
        if file_size_mb > max_size_mb:
            raise ValueError(f"File size exceeds the maximum allowed size of {max_size_mb} MB.")
        
        file_stream.seek(0)
        
        bucket = storage.bucket()
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_file(file_stream, content_type='image/jpeg')
        blob.make_public()
        
        return blob.public_url
    
    except GoogleAPIError as api_error:
        raise Exception(f"Google API error: {str(api_error)}")
    except Exception as e:
        raise Exception(f"Error uploading image to Firebase: {str(e)}")


def handle_image_upload(file,upload_folder='uploads'):
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    if file.filename == '':
        raise ValueError("No selected file")

    filename = secure_filename(file.filename)
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)

    return file_path


def delete_file_from_upload(file_name, upload_folder='uploads'):
    file_path = os.path.join(upload_folder, file_name)

    if os.path.isfile(file_path):
        try:
            os.remove(file_path)
            print(f"File {file_path} deleted successfully.")
        except Exception as e:
            print(f"Error deleting file: {str(e)}")
    else:
        print(f"File {file_path} does not exist.")

def delete_image_from_firebase(image_url):
    file_name = image_url.split('/')[-1]

    bucket = storage.bucket()

    try:
        blob = bucket.blob(file_name)
        blob.delete()
    except Exception as e:
        raise Exception(f"Error deleting image from Firebase: {str(e)}")