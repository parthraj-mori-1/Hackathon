import boto3
import requests
import time
import tempfile
import os
from urllib.parse import urlparse
from moviepy.video.io.VideoFileClip import VideoFileClip
from strands import tool
# from Memory import MemoryManager
# from Context import app_context
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

BUCKET_NAME = os.getenv("BUCKET_NAME")
MODEL_ID = os.getenv("MODEL_ID")


class VideoTranscriber:
    def __init__(self,client,memory_id,app_context):
        """Initialize context, clients, and memory"""
        # memoryManager= MemoryManager()
        # client= memoryManager.get_client()
        # memory_id= memoryManager.get_memory_id()
        self.client = client
        self.memory_id = memory_id
        self.session_id =app_context.session_id
        self.actor_id =app_context.actor_id

        self.s3_client = boto3.client("s3")
        self.transcribe_client = boto3.client("transcribe")

    def _download_from_s3(self, bucket_name, key, local_path):
        self.s3_client.download_file(bucket_name, key, local_path)

    def _upload_to_s3(self, local_path, bucket_name, key):
        self.s3_client.upload_file(local_path, bucket_name, key)
        return f"s3://{bucket_name}/{key}"

    @tool
    def s3_video_to_transcript(self, s3_video_url: str) -> str:
        """Convert an S3 video file to text transcript using AWS Transcribe"""
        video_path = tempfile.mktemp(suffix=".mp4")
        audio_path = tempfile.mktemp(suffix=".wav")

        parsed_url = urlparse(s3_video_url)
        if parsed_url.scheme != "s3":
            raise ValueError("Please provide a full S3 URL starting with s3://")

        bucket_name = parsed_url.netloc
        object_key = parsed_url.path.lstrip("/")
        job_name = f"transcription_job_{int(time.time())}"

        try:
            # Download video from S3
            print(f"Downloading {s3_video_url} ...")
            self._download_from_s3(bucket_name, object_key, video_path)

            # Extract audio from video
            print("Extracting audio ...")
            clip = VideoFileClip(video_path)
            clip.audio.write_audiofile(audio_path, codec="pcm_s16le")

            # Upload audio to S3
            audio_key = f"temp/{os.path.basename(audio_path)}"
            audio_s3_uri = self._upload_to_s3(audio_path, bucket_name, audio_key)
            print(f"Audio uploaded: {audio_s3_uri}")

            # Start Transcribe job
            print("Starting AWS Transcribe job ...")
            self.transcribe_client.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': audio_s3_uri},
                MediaFormat='wav',
                LanguageCode='en-US'
            )

            # Wait until job completes
            timeout = time.time() + 300  # 5 min
            while True:
                status = self.transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
                job_status = status['TranscriptionJob']['TranscriptionJobStatus']

                if job_status in ['COMPLETED', 'FAILED']:
                    break
                if time.time() > timeout:
                    raise TimeoutError("Transcription job timed out")
                time.sleep(5)

            # Get transcript text
            if job_status == 'COMPLETED':
                transcript_url = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
                transcript_response = requests.get(transcript_url)
                transcript_text = transcript_response.json()['results']['transcripts'][0]['transcript']

                print("Transcription complete.")
                print(transcript_text)
                print(f"session_id : {self.session_id}, actor_id : {self.actor_id} and memory_id : {self.memory_id}")
                # Store in memory
                self.client.create_event(
                    memory_id=self.memory_id,
                    actor_id=self.actor_id,
                    session_id=self.session_id,
                    messages=[(transcript_text, "ASSISTANT")]
                )

                return{
                "status": "success",
                "transcript_text": transcript_text           
                }
            else:
                raise Exception("Transcription job failed")

        finally:
            # Clean temporary files
            if os.path.exists(video_path):
                os.remove(video_path)
            if os.path.exists(audio_path):
                os.remove(audio_path)
