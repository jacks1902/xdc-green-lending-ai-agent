import boto3
from botocore.exceptions import ClientError
import logging
import io
import http.client as http_client

# Enable detailed debug logs for boto3 (optional)
# Comment out these lines if you don't want debug logs in production
http_client.HTTPConnection.debuglevel = 1
logging.getLogger('botocore').setLevel(logging.DEBUG)
logging.getLogger('boto3').setLevel(logging.DEBUG)
logging.getLogger('urllib3').setLevel(logging.DEBUG)

# Set up basic logging to see messages in your terminal
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class StorXAgent:
    def __init__(self, access_key_id, secret_access_key, endpoint_url, bucket_name):
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.endpoint_url = endpoint_url
        self.bucket_name = bucket_name
        self.is_real_integration_possible = False
        self.s3_client = None

        if not all([access_key_id, secret_access_key, endpoint_url, bucket_name]):
            logging.warning("StorX credentials are incomplete. Running in simulation mode.")
            return

        try:
            self.s3_client = boto3.client(
                's3',
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                verify=False  # Change to True if SSL cert is valid
            )

            try:
                self.s3_client.head_bucket(Bucket=self.bucket_name)
                logging.info(f"StorX vault '{self.bucket_name}' already exists.")
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    logging.info(f"Vault '{self.bucket_name}' not found. Creating it...")
                    self.s3_client.create_bucket(Bucket=self.bucket_name)
                    logging.info(f"Vault '{self.bucket_name}' created successfully.")
                else:
                    logging.error(f"Bucket check failed: {e}")
                    raise

            self.is_real_integration_possible = True
            logging.info("✅ StorXAgent initialized successfully with real credentials.")

        except Exception as e:
            logging.error(f"Initialization failed: {e}")
            logging.warning("Running in simulation mode due to initialization failure.")

    def upload_document(self, file_content_bytes, object_key):
        if not self.is_real_integration_possible:
            logging.info("SIMULATION MODE: Skipping real upload.")
            return {"success": True, "url": f"https://simulated.storx.link/{self.bucket_name}/{object_key}"}

        try:
            if not isinstance(file_content_bytes, bytes):
                logging.error("file_content_bytes is not bytes. Encoding as UTF-8.")
                file_content_bytes = str(file_content_bytes).encode('utf-8')

            # Wrap the bytes in a BytesIO stream
            file_stream = io.BytesIO(file_content_bytes)

            # --- DEBUG PRINTS ---
            print(f"--- DEBUG STORX UPLOAD ---")
            print(f"  Uploading object_key: {object_key}")
            print(f"  File size: {len(file_content_bytes)} bytes")
            print(f"--- END DEBUG ---")

            # More robust alternative to put_object: upload_fileobj
            self.s3_client.upload_fileobj(
                Fileobj=file_stream,
                Bucket=self.bucket_name,
                Key=object_key,
                ExtraArgs={'ContentType': 'text/plain'}
            )

            logging.info(f"✅ File uploaded successfully: {object_key}")
            object_url = f"{self.endpoint_url}/{self.bucket_name}/{object_key}"
            return {"success": True, "url": object_url}

        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            full_error = f"StorX Client Error: {error_code} - {error_message}"
            logging.error(full_error)
            return {"success": False, "error": full_error}

        except Exception as e:
            full_error = f"Unexpected error: {e}"
            logging.error(full_error)
            return {"success": False, "error": full_error}
