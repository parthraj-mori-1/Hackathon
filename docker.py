from bedrock_agentcore_starter_toolkit import Runtime
from boto3.session import Session
from dotenv import load_dotenv
import os
load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
boto_session = Session(aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=AWS_REGION)
region = boto_session.region_name

agentcore_runtime = Runtime()
agent_name = "hackathon_strands_agent_workflow"
response = agentcore_runtime.configure(
    entrypoint="main.py",
    auto_create_execution_role=True,
    auto_create_ecr=True,
    requirements_file="requirements.txt",
    region=region,
    agent_name=agent_name
)
print(response)
launch_response = agentcore_runtime.launch()