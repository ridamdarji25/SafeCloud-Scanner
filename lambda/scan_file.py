import os, boto3, requests
from urllib.parse import unquote_plus

# AWS clients
s3 = boto3.client('s3')
sns = boto3.client('sns')

# Hardcoded values (your configuration)
VT_API_KEY = "your virus total api key"
SAFE_BUCKET = "safe file bucket"
MALICIOUS_BUCKET = "malicious file bucket"
SNS_TOPIC_ARN = "SNS topic arn"

def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        local_path = '/tmp/' + os.path.basename(key)

        try:
            # Download file from staging bucket
            s3.download_file(bucket, key, local_path)

            # Send file to VirusTotal
            headers = {"x-apikey": VT_API_KEY}
            url = "https://www.virustotal.com/api/v3/files"
            with open(local_path, 'rb') as f:
                resp = requests.post(url, headers=headers, files={"file": (key, f)})
            resp.raise_for_status()
            analysis_id = resp.json()['data']['id']

            # Poll for analysis result
            result = poll_vt(analysis_id, headers)
            malicious = result["data"]["attributes"]["stats"].get("malicious", 0) > 0

            # Decide destination bucket
            dest_bucket = MALICIOUS_BUCKET if malicious else SAFE_BUCKET
            s3.copy_object(Bucket=dest_bucket, CopySource={'Bucket': bucket, 'Key': key}, Key=key)
            s3.delete_object(Bucket=bucket, Key=key)

            # Send SNS notification
            message = f"File '{key}' scanned and stored in '{dest_bucket}'. Malicious: {malicious}"
            sns.publish(TopicArn=SNS_TOPIC_ARN, Message=message)

        except Exception as e:
            # Send SNS notification for errors
            error_message = f"Error processing file '{key}': {str(e)}"
            sns.publish(TopicArn=SNS_TOPIC_ARN, Message=error_message)
            raise e

def poll_vt(analysis_id, headers):
    """
    Poll VirusTotal API until the analysis is complete.
    Maximum 10 attempts (adjust if needed).
    """
    url = f"https://www.virustotal.com/api/v3/analyses/{analysis_id}"
    for _ in range(10):
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        data = r.json()
        if data["data"]["attributes"]["status"] == "completed":
            return data
    return data






