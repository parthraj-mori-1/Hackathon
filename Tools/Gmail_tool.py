import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from strands import tool, Agent
from Hooks.Memory_hook import MemoryHookProvider
# from Context import app_context
# from Memory import MemoryManager
import json
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

# Corrected env access (it's `os.getenv`, not `os.get_env`)
BUCKET_NAME = os.getenv("BUCKET_NAME")
MODEL_ID = os.getenv("MODEL_ID")

class GmailSender:
    """Handles sending emails and generating subjects using Bedrock Agent"""

    def __init__(self,client,memory_id,app_context):
        # memoryManager=MemoryManager()
        # client= memoryManager.get_client()
        # memory_id=memoryManager.get_memory_id()
        self.client = client
        self.memory_id = memory_id
        self.session_id = app_context.session_id
        self.actor_id = app_context.actor_id
        self.smtp_server = "smtp.gmail.com"
        self.port = 587
        self.sender_email = "salesassistantbot123@gmail.com"
        self.password = "wefygyuwkagpamma"  # ⚠️ use env var for security later

    def _generate_subject(self, message_body: str) -> str:
        """Use Bedrock Agent to generate a professional subject line"""
        try:
            gmail_memory_hooks = MemoryHookProvider(self.client, self.memory_id)

            subject_agent = Agent(
                hooks=[gmail_memory_hooks],
                model=MODEL_ID,
                system_prompt="""You are a subject line generator. Create concise, 
                professional email subjects based on the message content and user context. 
                Keep it under 60 characters.""",
                state={"actor_id": self.actor_id, "session_id": self.session_id}
            )

            subject_prompt = f"""
            Generate a professional email subject line for the following message:

            Message: {message_body}

            Return ONLY the subject line without any additional text.
            """

            subject_response = subject_agent(subject_prompt)
            subject = str(subject_response).strip()

            if not subject or subject.lower() == "none":
                subject = "Important Message"

            return subject

        except Exception as e:
            logger.error(f"❌ Subject generation failed: {e}")
            return "Important Message"

    @tool
    def send_gmail(self, recipient_email: str, message_body: str, subject: str = None) -> dict:
        """
    Sends an email to the specified recipient using Gmail.
    If no subject is provided, generates one based on user data and message content.
    
    Args:
        recipient_email: Email address of the recipient
        message_body: Main content of the email
        subject: Subject line of the email (optional - will be generated if not provided)
    
    Returns:
        dict: Status of the email sending operation
    """
        try:
            # Generate subject if not provided
            if not subject:
                subject = self._generate_subject(message_body)

            # Create email message
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = recipient_email
            message["Subject"] = subject
            message.attach(MIMEText(message_body, "plain"))

            # Send email
            with smtplib.SMTP(self.smtp_server, self.port) as server:
                server.starttls()
                server.login(self.sender_email, self.password)
                server.send_message(message)

            logger.info(f"✅ Email sent to {recipient_email} with subject '{subject}'")
            return {"status": "sent", "subject": subject}

        except Exception as e:
            logger.error(f"❌ Email sending failed: {e}")
            return {"status": "error", "message": f"Failed to send email: {str(e)}"}
