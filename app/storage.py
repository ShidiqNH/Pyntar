import os
import boto3
from botocore.config import Config

def get_r2_client():
    import os
    import re

    r2_account_id = os.environ.get("R2_ACCOUNT_ID")
    r2_access_key_id = os.environ.get("R2_ACCESS_KEY_ID")
    r2_secret_access_key = os.environ.get("R2_SECRET_ACCESS_KEY")
    endpoint_url = os.environ.get("R2_ENDPOINT_URL")

    # DEBUG LOG
    print("========== R2 DEBUG ==========")
    print("R2_ACCOUNT_ID:", repr(r2_account_id))
    print("R2_ACCESS_KEY_ID:", repr(r2_access_key_id))
    print("R2_SECRET_ACCESS_KEY exists:", bool(r2_secret_access_key))
    print("R2_ENDPOINT_URL:", repr(endpoint_url))
    print("R2_BUCKET_NAME:", repr(os.environ.get("R2_BUCKET_NAME")))
    print("==============================")

    # Fallback jika account ID tidak ada tetapi endpoint URL ada
    if not r2_account_id and endpoint_url:
        match = re.search(
            r"https://([^.]+)\.r2\.cloudflarestorage\.com",
            endpoint_url
        )
        if match:
            r2_account_id = match.group(1)

    # Validasi kredensial
    if not all([
        r2_account_id or endpoint_url,
        r2_access_key_id,
        r2_secret_access_key
    ]):
        raise ValueError(
            "Kredensial Cloudflare R2 tidak lengkap di environment variables"
        )

    # Generate endpoint jika belum ada
    if not endpoint_url:
        endpoint_url = (
            f"https://{r2_account_id}.r2.cloudflarestorage.com"
        )

    return boto3.client(
        service_name="s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=r2_access_key_id,
        aws_secret_access_key=r2_secret_access_key,
        region_name="auto",
        config=Config(signature_version="s3v4")
    )
    

def upload_file_to_r2(file_body, object_name):
    bucket_name = os.environ.get("R2_BUCKET_NAME")
    if not bucket_name:
        raise ValueError("R2_BUCKET_NAME tidak diset di environment variables")
        
    s3_client = get_r2_client()
    s3_client.put_object(
        Bucket=bucket_name,
        Key=object_name,
        Body=file_body,
        ContentType="text/x-python"
    )
    
    # Generate presigned URL valid for 24 hours (86400 seconds)
    presigned_url = s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket_name, "Key": object_name},
        ExpiresIn=86400
    )
    
    return presigned_url
