import json
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Hackthon-agent")

def lambda_handler(event, context):
    job_id = event.get("queryStringParameters", {}).get("job_id")
    if not job_id:
        return {"statusCode": 400, "body": json.dumps({"error": "Missing job_id"})}

    resp = table.get_item(Key={"job_id": job_id})
    item = resp.get("Item")
    if not item:
        return {"statusCode": 404, "body": json.dumps({"error": "Job not found"})}

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "status": item.get("status"),
            "response": item.get("response", "")
        })
    }
