import boto3, json
import email
from chalice import Chalice, BadRequestError
from ollama_client import call_ollama

app = Chalice(app_name='email-agent')

# Initialize boto3 clients
s3_client = boto3.client('s3')
ses_client = boto3.client('ses')

@app.on_s3_event(bucket='cloudmatica', events=['s3:ObjectCreated:*'], prefix='agent/')
def handle_s3_event(event):
    return process_s3_event(event)

def process_s3_event(event):
    # Fetch the email object from S3
    print(event)
    bucket_name = event['s3']['bucket']['name']
    object_key = event['s3']['object']['key']

    email_object = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    email_content = email_object['Body'].read().decode('utf-8')

    # Parse the email
    parsed_email = email.message_from_string(email_content)
    sender = parsed_email['From']
    subject = parsed_email['Subject']
    body = get_body_from_email(parsed_email)
    prompt = f'{subject}\n{body}'

    response = call_ollama(model='mistral', prompt=prompt)
    if response.status_code != 200:
        raise BadRequestError("Failed to call Ollama service")

    response_data = response.json()

    # Parse the response
    response_subject = response_data.get('subject', 'Re: ' + subject)
    response_body = response_data.get('body', 'Thank you for your email.')

    # Send the response email using SES
    ses_client.send_email(
        Source=sender,
        Destination={
            'ToAddresses': [sender]
        },
        Message={
            'Subject': {
                'Data': response_subject,
                'Charset': 'UTF-8'
            },
            'Body': {
                'Text': {
                    'Data': response_body,
                    'Charset': 'UTF-8'
                }
            }
        }
    )

    return {'status': 'Email processed successfully'}

def get_body_from_email(parsed_email):
    """Extracts the body from the email message."""
    if parsed_email.is_multipart():
        for part in parsed_email.walk():
            content_type = part.get_content_type()
            disposition = str(part.get('Content-Disposition'))

            if content_type == 'text/plain' and 'attachment' not in disposition:
                return part.get_payload(decode=True).decode('utf-8')
    else:
        return parsed_email.get_payload(decode=True).decode('utf-8')
    return ''


# For local testing
if __name__ == "__main__":
    with open('mock_s3_event.json') as f:
        mock_event = json.load(f)
    result = process_s3_event(mock_event['Records'][0])
    print(result)