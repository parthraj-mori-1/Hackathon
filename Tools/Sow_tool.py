import boto3
import uuid
from strands import tool, Agent
# from Context import app_context
# from Memory import MemoryManager
from Hooks.Memory_hook import MemoryHookProvider
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

BUCKET_NAME = os.getenv("BUCKET_NAME")
MODEL_ID = os.getenv("MODEL_ID")

class SOWGenerator:
    def __init__(self,client,memory_id,app_context):
        """
        Initialize SOW generator with session and actor context.
        If not provided, takes from global app_context.
        """
        # memoryManager= MemoryManager()
        # client= memoryManager.get_client()
        # memory_id=memoryManager.get_memory_id()
        self.session_id =app_context.session_id
        self.actor_id =app_context.actor_id
        self.s3_client = boto3.client("s3")
        self.client=client
        self.memory_id=memory_id

    def _create_agent(self):
        """Create and return the Agent instance."""
        prompt = """
        Task: Generate Statement of Work (SOW) with project scope, deliverables, and timelines.
        Return JSON in format:
        {
            "SOW": "...",
            "Deliverables": ["..."],
            "Timeline": "..."
        }
        """
        sow_memory_hook= MemoryHookProvider(self.client, self.memory_id)

        return Agent(
            hooks=[sow_memory_hook],
            model=MODEL_ID,
            system_prompt=prompt,
            state={"actor_id": self.actor_id, "session_id": self.session_id}
        )

    @tool
    def generate_sow(self, query: str):
        """Generate SOW and upload result to S3."""
        agent = self._create_agent()
        response = agent(f"Query:\n{query}")

        key = f"SOW-{uuid.uuid4()}.txt"
        self.s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=key,
            Body=str(response),
            ContentType="text/plain"
        )

        s3_url = f"https://{BUCKET_NAME}.s3.us-east-1.amazonaws.com/{key}"
        print(f"SOW stored at {s3_url}")
        return{
                "status": "success",
                "s3_url": s3_url,
                "SOW_response": str(response),
                "message": "SOW generated successfully using specialized agent"
            }
