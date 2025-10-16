# Memory.py
from bedrock_agentcore.memory import MemoryClient
from bedrock_agentcore.memory.constants import StrategyType
from botocore.exceptions import ClientError
import logging
import traceback

logger = logging.getLogger(__name__)

class MemoryManager:
    def __init__(self, memory_name="Hackathon_sales_assistant"):
        self.client = MemoryClient()
        self.memory_name = memory_name
        self.memory_id = None

    def create_memory(self):
        """Create or reuse existing memory"""
        try:
            print("🧠 Creating Memory with Long-Term Strategy...")

            memory = self.client.create_memory_and_wait(
                name=self.memory_name,
                strategies=[],  # or [StrategyType.LTM]
                description="Sales agent short-term memory",
                event_expiry_days=10
            )

            self.memory_id = memory['id']
            logger.info(f"✅ Memory created with ID: {self.memory_id}")
            print(f"Memory created successfully with ID: {self.memory_id}")

        except ClientError as e:
            if e.response['Error']['Code'] == 'ValidationException' and "already exists" in str(e):
                # If memory already exists, retrieve its ID
                memories = self.client.list_memories()
                self.memory_id = next((m['id'] for m in memories if m['id'].startswith(self.memory_name)), None)
                logger.info(f"Memory already exists. Using existing memory ID: {self.memory_id}")

        except Exception as e:
            logger.error(f"❌ ERROR: {e}")
            traceback.print_exc()
            if self.memory_id:
                try:
                    self.client.delete_memory_and_wait(memory_id=self.memory_id)
                    logger.info(f"🧹 Cleaned up memory: {self.memory_id}")
                except Exception as cleanup_error:
                    logger.error(f"Failed to clean up memory: {cleanup_error}")

        return self.memory_id

    def get_client(self):
        """Return the MemoryClient instance"""
        return self.client

    def get_memory_id(self):
        """Return the memory ID"""
        return self.memory_id
