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