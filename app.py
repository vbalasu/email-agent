from chalice import Chalice
import json
app = Chalice(app_name='email-agent')

@app.on_s3_event(bucket='cloudmatica', events=['s3:ObjectCreated:*'], prefix='agent/')
def handle_s3_event(event):
    return process_s3_event(event)

def process_s3_event(event):
    # Fetch the email object from S3
    print(event.to_dict())
    bucket_name = event['s3']['bucket']['name']
    object_key = event['s3']['object']['key']

    from process_email import parse_email
    incoming = parse_email(bucket_name, object_key)
    prompt = f'{incoming["subject"]}\n{incoming["body"]}'

    from ollama_client import call_ollama
    output = call_ollama(prompt=prompt)

    from process_email import send_email
    return send_email(sender='Cloudmatica Agent <agent@cloudmatica.com>', recipient=incoming['sender'], 
           subject='Re: ' + incoming['subject'], body=output)

# For local testing
if __name__ == "__main__":
    with open('mock_s3_event.json') as f:
        mock_event = json.load(f)
    result = process_s3_event(mock_event['Records'][0])
    print(result)