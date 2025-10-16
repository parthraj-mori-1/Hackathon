import json
import uuid
import boto3
from datetime import datetime

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Hackthon-agent")

def lambda_handler(event, context):
    body = json.loads(event.get("body", "{}"))
    question = body.get("question")
    session_id = body.get("session_id")
    
    if not question or not session_id:
        return {"statusCode": 400, "body": json.dumps({"error": "Missing 'question' or 'session_id'"})}

    job_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    # Store initial job
    table.put_item(
        Item={
            "job_id": job_id,
            "session_id": session_id,
            "question": question,
            "status": "pending",
            "created_at": now
        }
    )

    # Send to SQS for processing
    sqs = boto3.client("sqs")
    queue_url = "https://sqs.us-east-1.amazonaws.com/637423349442/Hackathon-agent"
    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps({"job_id": job_id, "session_id": session_id, "question": question})
    )

    return {
        "statusCode": 200,
        "body": json.dumps({"job_id": job_id, "status": "pending"})
    }
