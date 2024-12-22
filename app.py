from chalice import Chalice
import json
app = Chalice(app_name='email-agent')

@app.on_s3_event(bucket='cloudmatica', events=['s3:ObjectCreated:*'], prefix='agent/')
def handle_s3_event(event):
    return process_s3_event(event)

def process_s3_event(event):
    # Fetch the email object from S3
    print(event.to_dict())
    bucket_name = event.bucket  # event['Records'][0]['s3']['bucket']['name']  # event.bucket      #event['s3']['bucket']['name']
    object_key = event.key  # event['Records'][0]['s3']['object']['key']    #  event.key          #event['s3']['object']['key']
    print(bucket_name, object_key)

    from chalicelib.process_email import parse_email
    incoming = parse_email(bucket_name, object_key)
    prompt = f'{incoming["subject"]}\n{incoming["body"]}'

    from chalicelib.ollama_client import call_ollama
    output = call_ollama(prompt=prompt)

    from chalicelib.process_email import send_email
    return send_email(sender='Cloudmatica Agent <agent@cloudmatica.com>', recipient=incoming['sender'], 
           subject='Re: ' + incoming['subject'], body=output)

@app.route('/recent')
def get_most_recent_email():
    import boto3
    from datetime import datetime

    s3 = boto3.client('s3')
    
    # List objects in the agent/ prefix
    response = s3.list_objects_v2(
        Bucket='cloudmatica',
        Prefix='agent/'
    )

    if 'Contents' not in response:
        return {'error': 'No emails found'}

    # Sort by last modified timestamp
    objects = sorted(
        response['Contents'],
        key=lambda x: x['LastModified'],
        reverse=True
    )
    
    if not objects:
        return {'error': 'No emails found'}

    # Get the most recent object key
    most_recent = objects[0]['Key']
    
    return {
        'most_recent_email': f's3://cloudmatica/{most_recent}',
        'timestamp': objects[0]['LastModified'].isoformat()
    }

@app.route('/')
def index():
    return 'email-agent is running. Send an email to agent@cloudmatica.com'

# For local testing
if __name__ == "__main__":
    class S3Event:
        def __init__(self, bucket='my-bucket', key='my-key'):
            self.bucket = bucket
            self.key = key
        def to_dict(self):
            return {'bucket': self.bucket, 'key': self.key}

    event = S3Event(bucket='cloudmatica', key='agent/14c8tfuj0nbeg6r297496ggqkd1es9nlumuiu481')
    result = process_s3_event(event)
    print(result)