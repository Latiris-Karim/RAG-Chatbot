import os
from google.cloud import secretmanager


def get_secrets():
    
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    secret_ids = ["example1","example2"]

    client = secretmanager.SecretManagerServiceClient()

    for secret_id in secret_ids:
        parent = f"projects/{project_id}/secrets/{secret_id}/versions/1"
        response = client.access_secret_version(request={"name": parent})
        os.environ[secret_id] = response.payload.data.decode("UTF-8")
