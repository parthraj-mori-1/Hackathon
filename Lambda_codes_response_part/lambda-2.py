import json
import boto3

AGENT_ARN = "arn:aws:bedrock-agentcore:us-east-1:637423349442:runtime/hackathon_strands_agent_workflow-66XZsW3yDm"
QUALIFIER = "DEFAULT"
ACTOR_ID = "abc23324"

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Hackthon-agent")

def lambda_handler(event, context):
    agent_client = boto3.client("bedrock-agentcore", region_name="us-east-1")

    for record in event['Records']:
        body = json.loads(record['body'])
        job_id = body['job_id']
        session_id = body['session_id']
        question = body['question']

        # Call Bedrock AgentCore
        response = agent_client.invoke_agent_runtime(
            agentRuntimeArn=AGENT_ARN,
            qualifier=QUALIFIER,
            payload=json.dumps({
                "prompt": question,
                "session_id": session_id,
                "actor_id": ACTOR_ID
            })
        )

        resp_body = response["response"].read()
        try:
            resp_data = json.loads(resp_body)
        except:
            resp_data = resp_body.decode("utf-8") if isinstance(resp_body, bytes) else str(resp_body)

        # Update DynamoDB with response safely
        table.update_item(
            Key={"job_id": job_id},
            UpdateExpression="SET #resp = :r, #st = :s",
            ExpressionAttributeNames={
                "#resp": "response",
                "#st": "status"
            },
            ExpressionAttributeValues={
                ":r": resp_data,
                ":s": "completed"
            }
        )
