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

def parse_email(bucket_name: str, object_key: str) -> dict:
    """
    Parses an email from the specified S3 bucket and key

    Args:
        bucket_name (str): S3 bucket name
        object_key (str): S3 object key

    Returns:
        A dict in the following format:
        {
            "sender": "person@domain.com",
            "subject": "Some subject",
            "body": "Message body"
        }
    """
    import boto3, email
    s3_client = boto3.client('s3')
    email_object = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    email_content = email_object['Body'].read().decode('utf-8')
    # Parse the email
    parsed_email = email.message_from_string(email_content)
    sender = parsed_email['From']
    subject = parsed_email['Subject']
    body = get_body_from_email(parsed_email)
    return {
        'sender': sender,
        'subject': subject,
        'body': body
    }

def send_email(sender: str, recipient: str, subject: str, body: str) -> dict:
    """
    Send an email

    Arguments:
        sender (str): Email address of the sender
        recipient (str): Email address of the recipient
        subject (str): Subject line of the email message
        body (str): Body of the email message

    Returns:
        dict containing the response from SES upon sending the message
    """
    import boto3
    ses_client = boto3.client('ses')
    # Send the response email using SES
    return ses_client.send_email(
        Source=sender,
        Destination={
            'ToAddresses': [recipient]
        },
        Message={
            'Subject': {
                'Data': subject,
                'Charset': 'UTF-8'
            },
            'Body': {
                'Text': {
                    'Data': body,
                    'Charset': 'UTF-8'
                }
            }
        })