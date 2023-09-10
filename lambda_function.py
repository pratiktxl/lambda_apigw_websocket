import json
import pymysql
import os
import boto3

# Example JSON payloads for testing using Postman.

# JSON for sending a message:
# {
#   "action": "sendMessage",
#   "value": "name"
# }

# JSON for retrieving messages:
# {
#   "action": "getMessage",
#   "x": 3
# }

def lambda_handler(event, context):
    """Main Lambda function handler."""
    
    # Parse the 'action' from the event body.
    action = json.loads(event.get('body', {})).get('action', '')
    
    # Extract connection_id from the event.
    connection_id = event["requestContext"].get("connectionId")
    print("connection_id", connection_id)
    
    # Construct the endpoint URL for API Gateway.
    domain_name = event["requestContext"]["domainName"]
    stage = event["requestContext"]["stage"]
    endpoint_url = f"https://{domain_name}/{stage}"
    print(endpoint_url)
    
    # Initialize boto3 client for API Gateway Management API.
    client = boto3.client("apigatewaymanagementapi", endpoint_url=endpoint_url)
    
    # Process request based on the action type.
    if action == 'sendMessage':
        return send_message(event, context)
    elif action == 'getMessage':
        return get_message(event, context)
    else:
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid action')
        }

def send_message(event, context):
    """Handles the sendMessage action."""
    
    # Extract message value from the event.
    record_value = json.loads(event.get('body', {})).get('value', 'default_value')

    # Get a database connection.
    connection = get_db_connection()
    print('sendMessage invoked')

    try:
        # Insert the message into the database.
        with connection.cursor() as cursor:
            insert_sql = "INSERT INTO sample_table (name) VALUES (%s);"
            cursor.execute(insert_sql, (record_value,))
            connection.commit()
            last_id = cursor.lastrowid
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Message sent', 'last_inserted_id': last_id})
        }
    finally:
        connection.close()
    
    try:
        # Notify the connected client about the message status.
        message = {"message": "Message sent", "last_inserted_id": last_id}
        client.post_to_connection(Data=json.dumps(message), ConnectionId=connection_id)
    except Exception as e:
        # Handle exceptions.
        print(f"Error: {str(e)}")  

def get_message(event, context):
    """Handles the getMessage action."""
    
    # Extract the number of messages to retrieve.
    num_records = int(json.loads(event.get('body', {})).get('x', 1))

    # Get a database connection.
    connection = get_db_connection()
    print('getMessage invoked')

    try:
        # Retrieve messages from the database.
        with connection.cursor() as cursor:
            select_sql = "SELECT * FROM sample_table ORDER BY id DESC LIMIT %s;"
            cursor.execute(select_sql, (num_records,))
            records = cursor.fetchall()
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Messages retrieved', 'records': records})
        }
    finally:
        connection.close()
    
    try:
        # Notify the connected client about the retrieved messages.
        message = {"message": "Message retrieved", "records": records}
        client.post_to_connection(Data=json.dumps(message), ConnectionId=connection_id)
    except Exception as e:
        # Handle exceptions.
        print(f"Error: {str(e)}")

def get_db_connection():
    """Returns a database connection using environment variables."""
    return pymysql.connect(
        host=os.environ['DB_HOST'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        database=os.environ['DB_NAME']
    )
