import json
import pymysql
import os
import boto3

"""
JSONs for testing using postman

{
  "action": "sendMessage",
  "value": "name"
}

{
  "action": "getMessage",
  "x": 3
}
"""

def lambda_handler(event, context):
    
    action = json.loads(event.get('body', {})).get('action', '')
    
    connection_id = event["requestContext"].get("connectionId")
    
    print("connection_id",connection_id)
    
    domain_name = event["requestContext"]["domainName"]
    stage = event["requestContext"]["stage"]
    endpoint_url = f"https://{domain_name}/{stage}"

    print(endpoint_url)
    
    client = boto3.client("apigatewaymanagementapi", 
                          endpoint_url=endpoint_url)
    
    
    
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
    record_value = json.loads(event.get('body', {})).get('value', 'default_value')

    connection = get_db_connection()
    
    print('sendMessage invoked');

    try:
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
        message = {"message": "Message sent", "last_inserted_id": last_id}
        client.post_to_connection(Data=json.dumps(message), 
                                  ConnectionId=connection_id)
    except Exception as e:
        # Handle exceptions
        print(f"Error: {str(e)}")  

def get_message(event, context):
    num_records = int(json.loads(event.get('body', {})).get('x', 1))

    connection = get_db_connection()
    
    print('getMessage invoked')

    try:
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
        message = {"message": "Message retrieved", "records": records}
        client.post_to_connection(Data=json.dumps(message), 
                                  ConnectionId=connection_id)
    except Exception as e:
        # Handle exceptions
        print(f"Error: {str(e)}")

def get_db_connection():
    return pymysql.connect(
        host=os.environ['DB_HOST'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        database=os.environ['DB_NAME']
    )
