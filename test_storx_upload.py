import boto3
import io

ACCESS_KEY = "jvjnzf5qv4tobzhcrahbfgxqd4ta" # YOUR ACTUAL KEY
SECRET_KEY = "jyp3kil5y5wtsw7n4vve2emipi3gttvir3dc4klelh4kmickjadlc" # YOUR ACTUAL SECRET
ENDPOINT_URL = "https://gateway.storx.io"
VAULT_NAME = "xdcprojectarea" # YOUR ACTUAL VAULT NAME
OBJECT_KEY = "test_upload_fileobj.txt" # Changed object key for distinction
FILE_CONTENT = b"Hello StorX, testing upload_fileobj."

def upload_to_storx():
    s3_client = boto3.client(
        's3',
        endpoint_url=ENDPOINT_URL,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        verify=False
    )

    file_stream = io.BytesIO(FILE_CONTENT)

    try:
        # We're now using upload_fileobj
        s3_client.upload_fileobj(
            Fileobj=file_stream,
            Bucket=VAULT_NAME,
            Key=OBJECT_KEY,
            ExtraArgs={'ContentType': 'text/plain'} # ContentType goes in ExtraArgs for upload_fileobj
        )
        print("✅ Upload succeeded!")
        print(f"File URL: {ENDPOINT_URL}/{VAULT_NAME}/{OBJECT_KEY}")
    except Exception as e:
        print(f"❌ Upload failed: {e}")

if __name__ == "__main__":
    upload_to_storx()
