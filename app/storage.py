import os
import boto3
from botocore.config import Config

def get_r2_client():
    r2_account_id = os.environ.get("R2_ACCOUNT_ID")
    r2_access_key_id = os.environ.get("R2_ACCESS_KEY_ID")
    r2_secret_access_key = os.environ.get("R2_SECRET_ACCESS_KEY")
    
    if not all([r2_account_id, r2_access_key_id, r2_secret_access_key]):
        raise ValueError("Kredensial Cloudflare R2 tidak lengkap di environment variables")
        
    endpoint_url = f"https://{r2_account_id}.r2.cloudflarestorage.com"
    
    return boto3.client(
        service_name="s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=r2_access_key_id,
        aws_secret_access_key=r2_secret_access_key,
        region_name="auto",  # R2 menggunakan region 'auto'
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
