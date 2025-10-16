import os
import json
from dotenv import load_dotenv
import boto3
import time
from Context import app_context
from Memory import MemoryManager
from Tools.Architecture_tool import ArchitectureToolRunner
from Tools.Gmail_tool import GmailSender
from Tools.Mom_tool import MomGenerator
from Tools.Sow_tool import SOWGenerator
from Tools.Transcript_tool import VideoTranscriber
from Tools.Search_tool import WebSearchTool
from Hooks.Memory_hook import MemoryHookProvider
import logging
from strands import Agent,tool
from bedrock_agentcore.runtime import BedrockAgentCoreApp
os.system("apt-get update && apt-get install -y graphviz")

app= BedrockAgentCoreApp()

logger = logging.getLogger(__name__)

load_dotenv(dotenv_path=".env")

os.environ["AWS_ACCESS_KEY_ID"]=os.getenv("AWS_ACCESS_KEY_ID")
os.environ["AWS_SECRET_ACCESS_KEY"]=os.getenv("AWS_SECRET_ACCESS_KEY")
os.environ["AWS_DEFAULT_REGION"]=os.getenv("AWS_DEFAULT_REGION")
# Load environment variables

memoryManager= MemoryManager()

# Corrected env access (it's `os.getenv`, not `os.get_env`)
BUCKET_NAME = os.getenv("BUCKET_NAME")
MODEL_ID = os.getenv("MODEL_ID")
Memory_name=os.getenv("MEMORY_NAME")

SALES_ARCH_SYSTEM_PROMPT = """
You are a task-execution assistant. Execute ONE tool per request and persist until success.

TOOL EXECUTION RULES:
1. **ONE TOOL PER REQUEST** - Choose the correct tool and use it once
2. **PERSIST ON FAILURE** - If tool fails, retry with same tool, don't switch randomly  
3. **NO TOOL HOPPING** - Don't jump between unrelated tools
4. **USE TOOL ERRORS** - If tool returns error, fix the input and retry
5. **STOP AFTER SUCCESS** - When task completes, end conversation

TOOL-SPECIFIC BEHAVIOR:
- **generate_mom**: ALWAYS uses transcript from memory (s3_video_to_transcript)
- **generate_sow**: Uses requirements from memory transcript if no specific instructions given
- **architecture_tool**: Uses context from memory transcript if no specific architecture requirements given
- **s3_video_to_transcript**: Extracts transcript and stores it in memory for other tools
- **websearch**: Searches for current information when external research is needed

MEMORY TRANSCRIPT USAGE:
- For MOM, SOW, and Architecture tasks: If user doesn't provide specific instructions/requirements, automatically use the transcript from memory
- If no transcript in memory → Run s3_video_to_transcript first to create transcript
- Transcript in memory is the default data source for these tools

WEBSEARCH USAGE:
- Use websearch when current/updated external information is needed
- Use for market research, technology trends, competitor analysis
- Don't use websearch for tasks that can be completed with existing memory/transcript

WORKFLOW EXAMPLES:
User: "Generate MOM"
→ Check memory for transcript
→ If no transcript → Run s3_video_to_transcript → Run generate_mom
→ "Task completed: MOM generated from transcript"

User: "Create architecture diagram"  
→ Check memory for transcript context
→ If no transcript → Run s3_video_to_transcript → Run architecture_tool
→ "Task completed: Architecture diagram generated from transcript"

User: "Generate SOW"
→ Check memory for transcript requirements  
→ If no transcript → Run s3_video_to_transcript → Run generate_sow
→ "Task completed: SOW generated from transcript"

User: "Research latest AI trends for our project"
→ Run websearch with query "latest AI trends 2024"
→ "Task completed: Search results provided"

ERROR RECOVERY:
- Tool error → Read error message → Fix issue → Retry same tool
- "No transcript" error → Run s3_video_to_transcript → Retry original tool
- Don't guess or try random alternatives
- NEVER jump to send_gmail for MOM/SOW/Architecture tasks

CONVERSATION BEHAVIOR:
- After task completion → "Task completed"
- No unnecessary follow-up questions
- No polite loops or extended conversations

Never Ask Follow-up question automatically.
"""

memoryManager.create_memory()
client=memoryManager.get_client()
memory_id=memoryManager.get_memory_id()
print("Memory_id : ",memory_id)

sales_agent_hook= MemoryHookProvider(client,memory_id)
session_id=app_context.session_id
actor_id= app_context.actor_id
# app_context.session_id=session_id
# app_context.actor_id=actor_id
architectureToolRunner = ArchitectureToolRunner(client,memory_id,app_context)
gmailSender= GmailSender(client,memory_id,app_context)
momGenerator = MomGenerator(client,memory_id,app_context)
sowGenerator= SOWGenerator(client,memory_id,app_context)
videoTranscriber = VideoTranscriber(client,memory_id,app_context)
webSearchTool = WebSearchTool(client,memory_id,app_context)

sales_agent = Agent(
    system_prompt=SALES_ARCH_SYSTEM_PROMPT,
    model=MODEL_ID,
    hooks=[sales_agent_hook],
    tools=[architectureToolRunner.Architecture_diagram, videoTranscriber.s3_video_to_transcript, gmailSender.send_gmail, sowGenerator.generate_sow,momGenerator.generate_mom,webSearchTool.websearch],
    state={"actor_id": actor_id, "session_id": session_id}
)

@app.entrypoint
def strands_agent_bedrock(payload):
    global sales_agent
    user_input = payload["prompt"]
    session_id=payload["session_id"]
    actor_id= payload["actor_id"]
    if session_id != app_context.session_id or actor_id !=app_context.actor_id :
        app_context.session_id=session_id
        app_context.actor_id=actor_id
        architectureToolRunner = ArchitectureToolRunner(client,memory_id,app_context)
        gmailSender= GmailSender(client,memory_id,app_context)
        momGenerator = MomGenerator(client,memory_id,app_context)
        sowGenerator= SOWGenerator(client,memory_id,app_context)
        videoTranscriber = VideoTranscriber(client,memory_id,app_context)
        webSearchTool = WebSearchTool(client,memory_id,app_context)
        sales_agent=Agent(
    system_prompt=SALES_ARCH_SYSTEM_PROMPT,
    model=MODEL_ID,
    hooks=[sales_agent_hook],
    tools=[architectureToolRunner.Architecture_diagram, videoTranscriber.s3_video_to_transcript, gmailSender.send_gmail, sowGenerator.generate_sow,momGenerator.generate_mom,webSearchTool.websearch],
    state={"actor_id": actor_id, "session_id": session_id}
)

    print("User Input:", user_input)
    response= sales_agent(user_input)
    return response.message['content'][0]['text']

if __name__ == "__main__":
    app.run()
