import boto3
import uuid
import os
from dotenv import load_dotenv
from strands import Agent, tool
from Hooks.Memory_hook import MemoryHookProvider
# from Context import app_context
# from Memory import MemoryManager

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

BUCKET_NAME = os.getenv("BUCKET_NAME")
MODEL_ID = os.getenv("MODEL_ID")

class MomGenerator:
    """Generates and uploads Minutes of Meeting (MOM) summaries with action items."""

    def __init__(self,client,memory_id,app_context):
        # memoryManager= MemoryManager()
        # client= memoryManager.get_client()
        # memory_id=memoryManager.get_memory_id()
        self.client = client
        self.memory_id = memory_id
        self.session_id = app_context.session_id
        self.actor_id = app_context.actor_id
        self.s3_client = boto3.client("s3")

    def _create_prompt(self, query: str) -> str:
        """Create structured MOM generation prompt"""
        return f"""
Task: Generate Minutes of Meeting (MOM) with speaker labels and action items.

Return JSON:
{{
    "MOM": "...",
    "ActionItems": [
        {{"task": "...", "owner": "...", "deadline": "..."}}
    ]
}}

Meeting Content:
{query}
"""

    @tool
    def generate_mom(self, query: str):
        """
        Generates MOM and stores it in S3.
        Returns a JSON with the MOM S3 link.
        """
        try:
            # Prepare memory hooks
            mom_memory_hooks = MemoryHookProvider(self.client, self.memory_id)

            # Initialize the MOM generation agent
            mom_agent = Agent(
                hooks=[mom_memory_hooks],
                model=MODEL_ID,
                system_prompt=self._create_prompt(query),
                state={
                    "actor_id": self.actor_id,
                    "session_id": self.session_id
                }
            )

            # Generate MOM
            response = mom_agent(f"Meeting Notes:\n{query}")
            response_text = str(response).strip()

            # Upload to S3
            key = f"MOM-{uuid.uuid4()}.txt"
            self.s3_client.put_object(
                Bucket=BUCKET_NAME,
                Key=key,
                Body=response_text,
                ContentType="text/plain"
            )

            s3_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{key}"
            print(f"✅ MOM stored at {s3_url}")

            return {
                "status": "success",
                "s3_url": s3_url,
                "Mom_response": response_text,
                "message": "MOM generated successfully using specialized agent"
            }

        except Exception as e:
            print(f"❌ MOM generation failed: {e}")
            return str(e)
