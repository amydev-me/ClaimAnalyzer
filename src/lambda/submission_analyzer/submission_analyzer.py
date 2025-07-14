import json
import boto3
import os
import urllib.request
import urllib.error

def lambda_handler(event, context):
    try:
        print(f"=== Lambda Started ===")
        print(f"Received event: {json.dumps(event, default=str)}")
        
        # Handle OPTIONS request for CORS
        if event.get('httpMethod') == 'OPTIONS':
            print("Handling OPTIONS request")
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
                },
                'body': ''
            }

        # Check if body exists
        if not event.get('body'):
            print("ERROR: No body in event")
            raise ValueError("No body in request")
            
        print(f"Request body: {event['body']}")
        
        # Parse body
        try:
            body = json.loads(event['body'])
            print(f"Parsed body: {body}")
        except json.JSONDecodeError as e:
            print(f"ERROR: Failed to parse JSON: {str(e)}")
            raise ValueError(f"Invalid JSON: {str(e)}")
        
        # Extract required fields
        file_key = body.get('fileKey')
        description = body.get('description')
        
        print(f"file_key: {file_key}")
        print(f"description: {description}")
        
        if not file_key or not description:
            raise ValueError("Missing fileKey or description")

        # S3 operations with environment variable
        print("Creating S3 client...")
        s3 = boto3.client("s3")
        
        # ✅ Use environment variable instead of hardcoded bucket
        bucket_name = os.environ.get('BUCKET_NAME')
        if not bucket_name:
            raise ValueError("BUCKET_NAME environment variable is not set")
        
        print(f"Using bucket: {bucket_name}")
        print(f"Generating presigned URL for key: {file_key}")
        
        try:
            presigned_url = s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket_name, "Key": file_key},
                ExpiresIn=300
            )
            print(f"Generated presigned URL: {presigned_url[:50]}...")
        except Exception as s3_error:
            print(f"ERROR: S3 presigned URL failed: {str(s3_error)}")
            raise s3_error

        # Call OpenAI analysis
        print("Starting OpenAI analysis...")
        try:
            analysis_result = analyze_with_openai_http(presigned_url, description)
            print(f"Analysis result: {analysis_result}")
        except Exception as openai_error:
            print(f"ERROR: OpenAI analysis failed: {str(openai_error)}")
            # Return a fallback result instead of failing
            analysis_result = {
                "summary": f"Analysis failed, but processing completed. Description: {description}",
                "error": str(openai_error),
                "processing_method": "fallback"
            }

        # ✅ Better timestamp generation
        from datetime import datetime
        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

        # Prepare response
        response_data = {
            'claimId': f"CLAIM_{file_key.split('/')[-1].split('.')[0] if '/' in file_key else 'unknown'}",
            'analysis': analysis_result,
            'fileKey': file_key,
            'processedAt': timestamp,  # ✅ Dynamic timestamp
            'bucketName': bucket_name  # ✅ Include bucket info for debugging
        }
        
        print(f"Returning response: {response_data}")

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
                'Content-Type': 'application/json'
            },
            'body': json.dumps(response_data)
        }

    except Exception as e:
        print(f"=== MAIN ERROR ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print(f"Event that caused error: {json.dumps(event, default=str)}")
        
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                "error": "Internal Server Error",
                "message": str(e),
                "type": type(e).__name__
            })
        }

def analyze_with_openai_http(image_url, description):
    try:
        print("=== OpenAI Function Started ===")
        
        # Check API key
        api_key = os.environ.get('OPENAI_API_KEY')
        print(f"API key exists: {bool(api_key)}")
        print(f"API key prefix: {api_key[:10] if api_key else 'None'}...")
        
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        # ✅ Enhanced prompt for better analysis
        prompt = f"""
            Analyze this vehicle damage image and provide a JSON response with the following fields:

            {
            "damage_severity": "minor | moderate | severe",
            "estimated_cost_range": "string (e.g., $500–$1,000)",
            "affected_parts": ["list of parts"],
            "safety_concerns": "string",
            "recommended_action": "string",
            "summary": "natural language summary of the incident"
            }

            Description provided: {description}
        """
        
        # Prepare payload
        payload = {
            "model": "gpt-4o",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }],
            "max_tokens": 800  # ✅ Increased for detailed analysis
        }
        
        print(f"Payload prepared. Image URL: {image_url[:50]}...")
        
        # Create request
        req = urllib.request.Request(
            'https://api.openai.com/v1/chat/completions',
            data=json.dumps(payload).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
        )
        
        print("Making OpenAI API request...")
        
        # Make request
        with urllib.request.urlopen(req, timeout=60) as response:
            print(f"OpenAI response status: {response.status}")
            response_text = response.read().decode('utf-8')
            print(f"Response received, length: {len(response_text)}")
            
            data = json.loads(response_text)
            
        print("OpenAI request successful")
            
        return {
            "summary": data['choices'][0]['message']['content'],
            "processing_method": "OpenAI HTTP",
            "success": True,
            "model_used": "gpt-4o"  # ✅ Track model version
        }
        
    except urllib.error.HTTPError as e:
        error_response = e.read().decode('utf-8')
        print(f"OpenAI HTTP Error {e.code}: {error_response}")
        raise Exception(f"OpenAI API HTTP Error {e.code}: {error_response}")
        
    except urllib.error.URLError as e:
        print(f"OpenAI URL Error: {str(e)}")
        raise Exception(f"OpenAI API URL Error: {str(e)}")
        
    except json.JSONDecodeError as e:
        print(f"OpenAI JSON decode error: {str(e)}")
        raise Exception(f"OpenAI response JSON error: {str(e)}")
        
    except Exception as e:
        print(f"OpenAI unexpected error: {str(e)}")
        raise Exception(f"OpenAI unexpected error: {str(e)}")