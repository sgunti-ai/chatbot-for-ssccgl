import boto3
import os
from botocore.exceptions import ClientError
import tempfile

class S3Client:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
    
    def download_file(self, bucket: str, key: str) -> str:
        """Download file from S3 and return local file path"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                self.s3_client.download_file(bucket, key, temp_file.name)
                return temp_file.name
        except ClientError as e:
            raise Exception(f"Error downloading from S3: {str(e)}")
    
    def list_pdf_files(self, bucket: str, prefix: str = "") -> list:
        """List all PDF files in S3 bucket"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=bucket,
                Prefix=prefix
            )
            
            pdf_files = []
            for obj in response.get('Contents', []):
                if obj['Key'].lower().endswith('.pdf'):
                    pdf_files.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified']
                    })
            
            return pdf_files
        except ClientError as e:
            raise Exception(f"Error listing S3 files: {str(e)}")
    
    def upload_processed_data(self, bucket: str, key: str, data: dict):
        """Upload processed question data to S3"""
        try:
            import json
            self.s3_client.put_object(
                Bucket=bucket,
                Key=key,
                Body=json.dumps(data),
                ContentType='application/json'
            )
        except ClientError as e:
            raise Exception(f"Error uploading to S3: {str(e)}")