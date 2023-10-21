import json
import http.client
import os

def lambda_handler(event, context):
    # Slack webhook URL
    webhook = os.environ.get('WEBHOOK')

    print(json.dumps(event, indent=2))
    print('From SNS:', event['Records'][0]['Sns']['Message'])

    postData = {
        "text": "*" + event['Records'][0]['Sns']['Subject'] + "*",
        "attachments": [
            {
                "text": event['Records'][0]['Sns']['Message']
            }
        ]
    }

    try:
        message = json.loads(event['Records'][0]['Sns']['Message'])
        postData['attachments'][0]['text'] = message['Description']
        postData['attachments'][0]['fields'] = []

        red_fields = ['Cause']  
        blue_fields = ['Description']  
        orange_fields = ['Event']  
        for key in ['AutoScalingGroupName','Description', 'Cause', 'Event', 'StartTime']:
            field = {
                "title": key,
                "value": message[key],
                "short": False
            }

            # Add emojis and colors to specific fields
            if key in red_fields:
                field['value'] = f":red_circle: *{message[key]}*"  # Red text with red circle emoji
                field['color'] = "#FF0000"  # Red color
            elif key in blue_fields:
                field['value'] = f":large_blue_circle: *{message[key]}*"  # Orange text with orange circle emoji
                field['color'] = "#0000FF"  # blue color
            elif key in orange_fields:
                field['value'] = f":large_orange_circle: *{message[key]}*"  # Orange text with orange circle emoji
                field['color'] = "#FFA500"  # Orange color
            else:
                field['value'] = f":white_check_mark: {message[key]}"  # Default text with green checkmark emoji
                field['color'] = "#36A64F"  # Green color

            postData['attachments'][0]['fields'].append(field)

    except json.JSONDecodeError:
        print("Message body was not a JSON payload")

    conn = http.client.HTTPSConnection("hooks.slack.com")

    headers = {'Content-Type': 'application/json'}

    payload = json.dumps(postData)

    conn.request("POST", webhook, payload, headers)
    res = conn.getresponse()
    data = res.read()

    print('Response:', data.decode('utf-8'))
    context.done(None, data.decode('utf-8'))
