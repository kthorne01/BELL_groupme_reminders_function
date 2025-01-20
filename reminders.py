import boto3
import json
from datetime import datetime, timedelta

# Initialize AWS clients
eventbridge = boto3.client('events')
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    # Parse event details
    detail = json.loads(event['detail'])
    event_id = detail['EventID']

    # Fetch event data from DynamoDB
    table = dynamodb.Table('Events')
    response = table.get_item(Key={'EventID': event_id})
    event_data = response.get('Item', {})

    if not event_data:
        return {'statusCode': 404, 'body': json.dumps({'message': 'Event not found'})}

    # Parse event date and time
    event_datetime = datetime.strptime(f"{event_data['EventDate']} {event_data['EventTime']}", "%Y-%m-%d %H:%M")

    # Define reminders
    reminders = [
        {"offset": timedelta(days=-7), "description": "One week before"},
        {"offset": timedelta(days=-3), "description": "Three days before"},
        {"offset": timedelta(days=-1), "description": "One day before"},
    ]

    # Create EventBridge rules for reminders
    for reminder in reminders:
        reminder_time = event_datetime + reminder["offset"]
        rule_name = f"Reminder-{event_id}-{reminder['description'].replace(' ', '-')}"

        # Create EventBridge rule
        eventbridge.put_rule(
            Name=rule_name,
            ScheduleExpression=reminder_time.strftime("cron(%M %H %d %m ? %Y)")
        )

        # Add Lambda target for the rule
        eventbridge.put_targets(
            Rule=rule_name,
            Targets=[
                {
                    'Id': '1',
                    'Arn': '<SEND_REMINDER_FUNCTION_ARN>',  # Replace with your SendReminderFunction ARN
                    'Input': json.dumps({'EventID': event_id})
                }
            ]
        )

    return {'statusCode': 200, 'body': json.dumps({'message': 'Reminders scheduled successfully'})}
