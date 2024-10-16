from google.cloud import storage
import os
from dotenv import load_dotenv

load_dotenv()

GCLOUD_PROJECT_ID = os.environ['GCLOUD_PROJECT']


def upload_to_gcs(bucket_name, file_path, destination_blob_name):
    """
    Upload the file to Google Cloud Storage
    """

    storage_client = storage.Client(project=GCLOUD_PROJECT_ID)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(file_path)

    gcs_uri = f"gs://{bucket_name}/{destination_blob_name}"

    print(gcs_uri)

    return gcs_uri
