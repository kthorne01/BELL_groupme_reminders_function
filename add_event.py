import boto3
import json
import uuid
from datetime import datetime

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    # Parse input data
    body = json.loads(event['body'])
    event_name = body.get('eventName')
    event_date = body.get('eventDate')
    event_time = body.get('eventTime')

    # Validate input
    if not event_name or not event_date or not event_time:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Missing required fields'})
        }

    # Generate unique EventID
    event_id = str(uuid.uuid4())

    # Add data to DynamoDB
    table = dynamodb.Table('Events')
    table.put_item(
        Item={
            'EventID': event_id,
            'EventName': event_name,
            'EventDate': event_date,
            'EventTime': event_time
        }
    )

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Event added successfully!', 'eventID': event_id})
    }
