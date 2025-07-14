import json
import boto3
import uuid
import os
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    try:
        print("=== UPLOAD HANDLER DEBUG ===")
        print(f"Event: {json.dumps(event, default=str)}")
        
        # Get bucket name
        bucket_name = os.environ.get('BUCKET_NAME')
        if not bucket_name:
            raise ValueError("BUCKET_NAME environment variable is not set")
        
        print(f"Using bucket: {bucket_name}")
        
        # Get filename
        query_params = event.get('queryStringParameters') or {}
        filename = query_params.get('filename', 'test.jpeg')
        print(f"Original filename: {filename}")
        
        # Generate unique key
        file_key = f"uploads/{uuid.uuid4()}.jpeg"
        print(f"Generated file key: {file_key}")
        
        # Create S3 client
        s3_client = boto3.client('s3')
        
        # Generate simple pre-signed URL for PUT
        print("Generating pre-signed URL for PUT operation...")
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket_name,
                'Key': file_key,
                'ContentType': 'image/jpeg'
            },
            ExpiresIn=300
        )
        
        print(f"Generated URL: {presigned_url[:100]}...")
        
        response_data = {
            'uploadUrl': presigned_url,
            'fileKey': file_key,
            'contentType': 'image/jpeg',
            'bucket': bucket_name,
            'debug': {
                'method': 'PUT',
                'expires_in': 300
            }
        }
        
        print(f"Returning response: {json.dumps(response_data, indent=2)}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Content-Type': 'application/json'
            },
            'body': json.dumps(response_data)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }