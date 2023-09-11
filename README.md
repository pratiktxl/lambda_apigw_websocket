# Lambda + API Gateway (WebSocket)

## Layer
pymysql - details to be added

## Example JSON payloads for testing using Postman.

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
