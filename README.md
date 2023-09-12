# Lambda + API Gateway (WebSocket) + RDS MySQL
This Lambda function saves data to RDS MySQL database which is accessed by websocket API. 
It creates the live connection to read and write data to RDS MySQL via Lambda. 

## Layer
pymysql - details to be added

## Example JSON payloads for testing using Postman or other tools

 JSON for sending a message:
 
 {
   "action": "sendMessage",
   "value": "name"
 }

 JSON for retrieving messages:
 
 {
   "action": "getMessage",
   "x": 3
 }
