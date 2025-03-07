from google.cloud import storage
import dtlpy as dl
import logging
import base64
import json
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name='GCS Export & Import')


class GCSExport(dl.BaseServiceRunner):
    def __init__(self):
        """
        Initializes the ServiceRunner with GCS Export & Import API credentials.
        """
        self.logger = logger
        self.logger.info('Initializing GCS Export & Import API client')
        raw_credentials = os.environ.get("GCP_SERVICE_ACCOUNT", None)
        if raw_credentials is None:
            raise ValueError(f"Missing GCP service account json.")

        try:
            decoded_credentials = base64.b64decode(raw_credentials).decode("utf-8")
            credentials_json = json.loads(decoded_credentials)
            credentials = json.loads(credentials_json['content'])
        except Exception:
            raise ValueError("Failed to decode the service account JSON. Refer to the guide for proper GCP service "
                             "account usage with Dataloop: "
                             "https://github.com/dataloop-ai-apps/export-gcs/blob/main/README.md")
        self.client = storage.Client.from_service_account_info(info=credentials)

    def export_annotation(self, item: dl.Item, context: dl.Context):
        if context is not None and context.node is not None and 'customNodeConfig' in context.node.metadata:
            bucket_name = context.node.metadata['customNodeConfig']['bucket_name']
            logger.info('Bucket name set to: {}'.format(bucket_name))
        else:
            raise ValueError("Node configration in context is missing, can't determinate the bucket name")

        annotation_json = item.to_json()
        annotation_json['annotations'] = item.annotations.list().to_json()['annotations']
        filename, _ = os.path.splitext(item.filename)
        gcs_bucket = self.client.bucket(bucket_name)
        blob = gcs_bucket.blob(f"{filename[1:]}.json")
        blob.upload_from_string(data=json.dumps(annotation_json), content_type='application/json')
        return item

    def import_annotation(self, item: dl.Item, context: dl.Context):
        if context is not None and context.node is not None and 'customNodeConfig' in context.node.metadata:
            bucket_name = context.node.metadata['customNodeConfig']['bucket_name']
            logger.info('Bucket name set to: {}'.format(bucket_name))
        else:
            raise ValueError("Node configration in context is missing, can't determinate the bucket name")

        gcs_bucket = self.client.bucket(bucket_name)
        filename, _ = os.path.splitext(item.filename)
        blob = gcs_bucket.blob(f"{filename[1:]}.json")
        bytes_data = blob.download_as_bytes()
        data = json.loads(bytes_data.decode('utf-8'))
        item.annotations.upload(annotations=data['annotations'])
        return item
