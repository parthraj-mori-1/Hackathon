import json
import re
import os
import boto3
import tempfile
import time
import uuid
from typing import Dict, List, Any, Tuple
from diagrams import Diagram, Cluster, Edge
from strands import tool, Agent

# Compute
from diagrams.aws.compute import (
    EC2, Lambda, ECS, Fargate, AutoScaling, Batch, Lightsail,
    ElasticBeanstalk, Outposts
)

# Database
from diagrams.aws.database import (
    RDS, Dynamodb, ElastiCache, Aurora, Redshift, Neptune,
    DocumentDB, QLDB, Timestream
)

# Networking & Content Delivery
from diagrams.aws.network import (
    ELB, ALB, NLB, CloudFront, Route53, APIGateway, VPC,
    PrivateSubnet, PublicSubnet, TransitGateway, DirectConnect,
    GlobalAccelerator, NATGateway
)

# Storage
from diagrams.aws.storage import (
    S3, EFS, FSx, Backup, StorageGateway, Snowball, Snowmobile
)

# Integration
from diagrams.aws.integration import (
    SQS, SNS, Eventbridge, StepFunctions, MQ
)

# Analytics
from diagrams.aws.analytics import (
    Kinesis, Athena, EMR, Glue, DataPipeline
)

# Security, Identity & Compliance
from diagrams.aws.security import (
    IAM, Cognito, SecretsManager, WAF, Shield,
    Inspector, Guardduty, Macie, Detective, CertificateManager
)

# Management & Governance
from diagrams.aws.management import (
    Cloudwatch, Cloudtrail, CloudwatchAlarm, Cloudformation,
    Config, Opsworks, SystemsManager, TrustedAdvisor
)

# Developer Tools
from diagrams.aws.devtools import (
    Codepipeline, Codebuild, Codedeploy, Codecommit,
    XRay, Cloud9, ToolsAndSdks
)

# AI/ML
from diagrams.aws.ml import (
    Sagemaker, Comprehend, Forecast, Lex, Polly,
    Rekognition, Translate, Textract, Personalize
)

# Application Integration (extra grouping)
# from diagrams.aws.application import (
#     ElasticTranscoder, Workspaces, Appstream20, WorkDocs, WorkMail
# )

# Migration & Transfer
from diagrams.aws.migration import (
    DMS, SMS
)

# On-Premises
from diagrams.onprem.compute import Server
from diagrams.onprem.network import Internet
from diagrams.onprem.client import User, Users
from diagrams.onprem.monitoring import Prometheus, Grafana

# Generic placeholders
from diagrams.generic.blank import Blank
from diagrams.generic.database import SQL
from diagrams.generic.storage import Storage

import boto3
from botocore.exceptions import ClientError
import datetime
from typing import Dict, List, Any
import os
from dotenv import load_dotenv
# from Context import app_context
# from Memory import MemoryManager
from Hooks.Memory_hook import MemoryHookProvider

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

Bucket_name=os.getenv("BUCKET_NAME")
MODEL_ID=os.getenv("MODEL_ID")

# Service mapping
SERVICE_MAP = {
    # Compute
    "EC2": EC2,
    "Lambda": Lambda,
    "ECS": ECS,
    "Fargate": Fargate,
    "AutoScaling": AutoScaling,
    "Batch": Batch,
    "Lightsail": Lightsail,
    "ElasticBeanstalk": ElasticBeanstalk,
    "Outposts": Outposts,
    # Database
    "RDS": RDS,
    "DynamoDB": Dynamodb,
    "ElastiCache": ElastiCache,
    "Aurora": Aurora,
    "Redshift": Redshift,
    "Neptune": Neptune,
    "DocumentDB": DocumentDB,
    "QLDB": QLDB,
    "Timestream": Timestream,

    # Network
    "ELB": ELB,
    "ALB": ALB,
    "NLB": NLB,
    "CloudFront": CloudFront,
    "Route53": Route53,
    "APIGateway": APIGateway,
    "VPC": VPC,
    "PrivateSubnet": PrivateSubnet,
    "PublicSubnet": PublicSubnet,
    "TransitGateway": TransitGateway,
    "DirectConnect": DirectConnect,
    "GlobalAccelerator": GlobalAccelerator,
    "NATGateway": NATGateway,

    # Storage
    "S3": S3,
    "EFS": EFS,
    "FSx": FSx,
    "Backup": Backup,
    "StorageGateway": StorageGateway,
    "Snowball": Snowball,
    "Snowmobile": Snowmobile,

    # Integration
    "SQS": SQS,
    "SNS": SNS,
    "EventBridge": Eventbridge,
    "StepFunctions": StepFunctions,
    "MQ": MQ,

    # Analytics
    "Kinesis": Kinesis,
    "Athena": Athena,
    "EMR": EMR,
    "Glue": Glue,
    "DataPipeline": DataPipeline,

    # Security
    "IAM": IAM,
    "Cognito": Cognito,
    "SecretsManager": SecretsManager,
    "WAF": WAF,
    "Shield": Shield,
    "Inspector": Inspector,
    "GuardDuty": Guardduty,
    "Macie": Macie,
    "Detective": Detective,
    "CertificateManager": CertificateManager,

    # Management & Governance
    "CloudWatch": Cloudwatch,
    "CloudTrail": Cloudtrail,
    "CloudWatchAlarm": CloudwatchAlarm,
    "CloudFormation": Cloudformation,
    "Config": Config,
    "OpsWorks": Opsworks,
    "SystemsManager": SystemsManager,
    "TrustedAdvisor": TrustedAdvisor,

    # Developer Tools
    "CodePipeline": Codepipeline,
    "CodeBuild": Codebuild,
    "CodeDeploy": Codedeploy,
    "CodeCommit": Codecommit,
    "XRay": XRay,
    "Cloud9": Cloud9,
    "ToolsAndSDKs": ToolsAndSdks,

    # Machine Learning
    "SageMaker": Sagemaker,
    "Comprehend": Comprehend,
    "Forecast": Forecast,
    "Lex": Lex,
    "Polly": Polly,
    "Rekognition": Rekognition,
    "Translate": Translate,
    "Textract": Textract,
    "Personalize": Personalize,

    # Migration & Transfer
    "DMS": DMS,
    "SMS": SMS,

    # On-Prem & Generic
    "Internet": Internet,
    "Server": Server,
    "User": User,
    "Users": Users,
    "Prometheus": Prometheus,
    "Grafana": Grafana,
    "SQL": SQL,
    "Storage": Storage,
    "Blank": Blank
}


class LLMServiceExtractor:
    """Tool 1: LLM-powered service extraction with intelligent numbering"""
    
    def __init__(self):
        self.prompt_template = """You are an AWS Solutions Architect. Analyze the architecture description and extract ALL AWS services with proper sequencing.

ARCHITECTURE DESCRIPTION:
{description}

INSTRUCTIONS:
1. Identify ALL AWS services mentioned
2. Determine the logical flow sequence (number services 1, 2, 3...)
3. Note relationships and dependencies
4. Categorize services appropriately

RETURN JSON with this EXACT structure:
{{
    "services": [
        {{
            "name": "exact service name",
            "type": "AWS service type",
            "step": number,
            "description": "what this service does in context",
            "category": "Networking|Compute|Database|Storage|Security|Integration|Monitoring|External"
        }}
    ],
    "relationships": [
        {{
            "from": "service name",
            "to": "service name", 
            "interaction": "how they interact",
            "priority": "high|medium|low"
        }}
    ],
    "flow_summary": "brief overview of data flow"
}}

AVAILABLE SERVICE TYPES: {service_types}

IMPORTANT: Use exact service names from available types. Return ONLY valid JSON.
"""
    
    def extract_with_llm(self, description: str) -> Dict[str, Any]:
        """Use AWS Bedrock Claude to extract services intelligently"""
        try:
            bedrock_runtime = boto3.client(
                service_name='bedrock-runtime',
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
            )
            
            prompt = self.prompt_template.format(
                description=description,
                service_types=", ".join(SERVICE_MAP.keys())
            )
            
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1
            }
            
            response = bedrock_runtime.invoke_model(
                modelId=MODEL_ID,
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            response_text = response_body['content'][0]['text']
            
            # Extract JSON from response
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            json_str = response_text[start:end]
            
            return json.loads(json_str)
            
        except Exception as e:
            print(f"❌ LLM extraction failed: {e}")
            # Fallback to rule-based extraction
            return self._fallback_extraction(description)
    
    def _fallback_extraction(self, description: str) -> Dict[str, Any]:
        """Rule-based fallback when LLM fails"""
        service_patterns = {
            "EC2": r"\b(EC2|instance|server|virtual machine|VM)\b",
            "Lambda": r"\b(Lambda|serverless|function)\b", 
            "S3": r"\b(S3|bucket|storage|object storage)\b",
            "RDS": r"\b(RDS|database|SQL|PostgreSQL|MySQL)\b",
            "DynamoDB": r"\b(DynamoDB|NoSQL|key-value)\b",
            "CloudFront": r"\b(CloudFront|CDN|content delivery)\b",
            "APIGateway": r"\b(API Gateway|API|endpoint)\b",
            "SQS": r"\b(SQS|queue|message queue)\b",
            "SNS": r"\b(SNS|notification|pubsub)\b",
            "CloudWatch": r"\b(CloudWatch|monitoring|logs|metrics)\b",
            "Cognito": r"\b(Cognito|authentication|auth|user pool)\b",
            "VPC": r"\b(VPC|virtual private cloud|network)\b",
            "ElastiCache": r"\b(ElastiCache|Redis|Memcached|cache)\b",
            "ELB": r"\b(load balancer|ALB|ELB|Application Load Balancer)\b"
        }
        
        services_found = []
        step = 1
        
        for service_type, pattern in service_patterns.items():
            if re.search(pattern, description, re.IGNORECASE):
                services_found.append({
                    "name": service_type,
                    "type": service_type,
                    "step": step,
                    "description": f"AWS {service_type} service",
                    "category": self._infer_category(service_type)
                })
                step += 1
        
        return {
            "services": services_found,
            "relationships": [],
            "flow_summary": "Automatically extracted architecture"
        }
    
    def _infer_category(self, service: str) -> str:
        """Infer service category"""
        categories = {
            "Networking": ["CloudFront", "Route53", "APIGateway", "ELB", "VPC"],
            "Compute": ["EC2", "Lambda", "ECS", "Fargate"],
            "Database": ["RDS", "DynamoDB", "ElastiCache", "Aurora"],
            "Storage": ["S3"],
            "Security": ["IAM", "Cognito", "WAF", "Shield"],
            "Integration": ["SQS", "SNS", "EventBridge", "StepFunctions"],
            "Monitoring": ["CloudWatch", "CloudTrail"]
        }
        
        for category, services in categories.items():
            if service in services:
                return category
        return "Compute"

class LLMArchitectureOrganizer:
    """Tool 2: LLM-powered service organization with optimal layout"""
    
    def __init__(self):
        self.layout_prompt = """You are an AWS Architecture Designer. Organize these services into logical clusters with optimal vertical + horizontal layout.

SERVICES:
{services}

RELATIONSHIPS:
{relationships}

INSTRUCTIONS:
1. Group services into logical clusters (max 4-5 services per cluster)
2. Determine optimal layout: vertical flow for main sequence, horizontal for parallel services
3. Assign each service to a cluster with position (row, column)
4. Ensure logical data flow from top to bottom, left to right

RETURN JSON with this structure:
{{
    "clusters": [
        {{
            "name": "cluster name",
            "description": "cluster purpose",
            "position": "top|middle|bottom",
            "flow_direction": "vertical|horizontal",
            "services": [
                {{
                    "name": "service name",
                    "type": "service type", 
                    "step": number,
                    "position": {{"row": 1, "col": 1}},
                    "description": "service role"
                }}
            ]
        }}
    ],
    "layout_strategy": "description of layout approach",
    "main_flow": ["service1", "service2", "service3"]
}}

Return ONLY valid JSON.
"""
    
    def organize_with_llm(self, extracted_data: Dict) -> Dict[str, Any]:
        """Use LLM to organize services with optimal layout"""
        try:
            bedrock_runtime = boto3.client(
                service_name='bedrock-runtime',
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
            )
            
            prompt = self.layout_prompt.format(
                services=json.dumps(extracted_data["services"], indent=2),
                relationships=json.dumps(extracted_data["relationships"], indent=2)
            )
            
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1
            }
            
            response = bedrock_runtime.invoke_model(
                modelId=MODEL_ID,
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            response_text = response_body['content'][0]['text']
            
            # Extract JSON
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            json_str = response_text[start:end]
            
            return json.loads(json_str)
            
        except Exception as e:
            print(f"❌ LLM organization failed: {e}")
            return self._fallback_organization(extracted_data)
    
    def _fallback_organization(self, extracted_data: Dict) -> Dict[str, Any]:
        """Fallback organization logic"""
        services = extracted_data["services"]
        
        # Sort by step number
        services_sorted = sorted(services, key=lambda x: x.get('step', 0))
        
        # Create basic vertical layout
        clusters = []
        current_cluster = []
        
        for i, service in enumerate(services_sorted):
            current_cluster.append({
                "name": service["name"],
                "type": service["type"],
                "step": service["step"],
                "position": {"row": i % 4 + 1, "col": 1},
                "description": service["description"]
            })
            
            # Create new cluster every 4 services
            if len(current_cluster) >= 4 or i == len(services_sorted) - 1:
                cluster_num = len(clusters) + 1
                clusters.append({
                    "name": f"Layer {cluster_num}",
                    "description": f"Architecture layer {cluster_num}",
                    "position": "top" if cluster_num == 1 else "middle" if cluster_num < len(services_sorted)//4 else "bottom",
                    "flow_direction": "vertical",
                    "services": current_cluster.copy()
                })
                current_cluster = []
        
        return {
            "clusters": clusters,
            "layout_strategy": "Vertical flow with sequential grouping",
            "main_flow": [s["name"] for s in services_sorted]
        }

class LLMConnectionBuilder:
    """Tool 3: LLM-powered connection building"""
    
    def __init__(self):
        self.connection_prompt = """You are an AWS Data Flow Designer. Create intelligent connections between services.

SERVICES:
{services}

CLUSTER ORGANIZATION:
{clusters}

EXISTING RELATIONSHIPS:
{relationships}

INSTRUCTIONS:
1. Create logical connections between services based on AWS best practices
2. Consider both vertical (sequential) and horizontal (parallel) flows
3. Add monitoring connections to CloudWatch where appropriate
4. Use proper connection labels and styles

RETURN JSON:
{{
    "connections": [
        {{
            "from": "source service",
            "to": "target service",
            "label": "connection purpose",
            "style": "solid|dashed|dotted",
            "direction": "forward|bidirectional",
            "weight": 1-5
        }}
    ],
    "flow_description": "overall data flow explanation"
}}

Return ONLY valid JSON.
"""
    
    def build_connections_with_llm(self, extracted_data: Dict, organized_data: Dict) -> List[Dict]:
        """Use LLM to build intelligent connections"""
        try:
            bedrock_runtime = boto3.client(
                service_name='bedrock-runtime',
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
            )
            
            prompt = self.connection_prompt.format(
                services=json.dumps(extracted_data["services"], indent=2),
                clusters=json.dumps(organized_data["clusters"], indent=2),
                relationships=json.dumps(extracted_data["relationships"], indent=2)
            )
            
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1
            }
            
            response = bedrock_runtime.invoke_model(
                modelId=MODEL_ID,
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            response_text = response_body['content'][0]['text']
            print(response_text)
            # Extract JSON
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            json_str = response_text[start:end]
            
            result = json.loads(json_str)
            return result.get("connections", [])
            
        except Exception as e:
            print(f"❌ LLM connection building failed: {e}")
            return self._fallback_connections(extracted_data, organized_data)
    
    def _fallback_connections(self, extracted_data: Dict, organized_data: Dict) -> List[Dict]:
        """Fallback connection logic"""
        connections = []
        services = [s["name"] for s in extracted_data["services"]]
        
        # Create sequential connections
        for i in range(len(services) - 1):
            connections.append({
                "from": services[i],
                "to": services[i + 1],
                "label": "data flow",
                "style": "solid",
                "direction": "forward",
                "weight": 3
            })
        
        # Add monitoring connections
        if "CloudWatch" in services:
            for service in services:
                if service != "CloudWatch":
                    connections.append({
                        "from": service,
                        "to": "CloudWatch",
                        "label": "metrics & logs",
                        "style": "dashed",
                        "direction": "forward",
                        "weight": 1
                    })
        
        return connections

class AdvancedDiagramGenerator:
    """Tool 4: Advanced diagram generation with mixed layout"""
    
    def __init__(self):
        self.color_schemes = {
            "Compute": {"fill": "#E8F5E8", "border": "#388E3C", "text": "#1B5E20"},
            "Database": {"fill": "#F3E5F5", "border": "#7B1FA2", "text": "#4A148C"},
            "Networking": {"fill": "#E3F2FD", "border": "#1976D2", "text": "#0D47A1"},
            "Storage": {"fill": "#FFF3E0", "border": "#F57C00", "text": "#E65100"},
            "Integration": {"fill": "#E0F2F1", "border": "#00796B", "text": "#004D40"},
            "Analytics": {"fill": "#EDE7F6", "border": "#5E35B1", "text": "#311B92"},
            "Security": {"fill": "#FFEBEE", "border": "#D32F2F", "text": "#B71C1C"},
            "Management": {"fill": "#FFF8E1", "border": "#FFA000", "text": "#FF6F00"},
            "DevTools": {"fill": "#E1F5FE", "border": "#0288D1", "text": "#01579B"},
            "MachineLearning": {"fill": "#F1F8E9", "border": "#7CB342", "text": "#33691E"},
            "Migration": {"fill": "#FFF3E0", "border": "#FB8C00", "text": "#E65100"},
            "OnPrem": {"fill": "#F5F5F5", "border": "#616161", "text": "#212121"},
            "External": {"fill": "#ECEFF1", "border": "#546E7A", "text": "#263238"},
            "Generic": {"fill": "#FAFAFA", "border": "#9E9E9E", "text": "#424242"}
        }

    
    def generate_mixed_layout_diagram(self, organized_data: Dict, connections: List[Dict], output_filename: str):
        """Generate diagram with vertical + horizontal layout"""
        
        graph_attr = {
            "fontsize": "12",
            "fontname": "Helvetica",
            "bgcolor": "white",
            "pad": "1.0",
            "splines": "ortho",  # Straight lines for clean layout
            "nodesep": "0.8",
            "ranksep": "1.2",
            "dpi": "200",
            "compound": "true",
            "rankdir": "TB"  # Top to Bottom main flow
        }
        
        node_attr = {
            "fontsize": "10",
            "fontname": "Helvetica",
            "style": "filled,rounded",
            "fixedsize": "true",
            "width": "2.0",
            "height": "1.4",
            "penwidth": "1.5"
        }
        
        edge_attr = {
            "fontsize": "9",
            "fontname": "Helvetica",
            "penwidth": "2.0",
            "arrowsize": "0.9"
        }
        
        with Diagram(
            "AWS Architecture",
            show=False,
            direction="TB",  # Main vertical flow
            filename=output_filename,
            graph_attr=graph_attr,
            node_attr=node_attr,
            edge_attr=edge_attr,
            outformat="png"
        ):
            services = {}
            
            # Create clusters with mixed layout
            for cluster in organized_data["clusters"]:
                cluster_style = {
                    "style": "rounded,filled",
                    "fillcolor": self._get_cluster_color(cluster),
                    "color": self._get_cluster_border(cluster),
                    "fontcolor": self._get_cluster_text(cluster),
                    "labeljust": "l",
                    "labelloc": "t"
                }
                
                # Determine cluster direction based on organization
                cluster_direction = "TB" if cluster.get("flow_direction") == "vertical" else "LR"
                
                with Cluster(cluster["name"], graph_attr=cluster_style, direction=cluster_direction):
                    for service_config in cluster["services"]:
                        service_type = SERVICE_MAP.get(service_config["type"])
                        if service_type:
                            # Create service with step number
                            label = f"[{service_config.get('step', '')}]\n{service_config['name']}"
                            service_node = service_type(label)
                            services[service_config["name"]] = service_node
            
            # Create connections with proper styling
            for conn in connections:
                from_service = services.get(conn["from"])
                to_service = services.get(conn["to"])
                
                if from_service and to_service:
                    edge_config = self._get_edge_config(conn)
                    
                    if conn.get("label"):
                        from_service >> Edge(**edge_config) >> to_service
                    else:
                        from_service >> Edge(**edge_config) >> to_service
    
    def _get_cluster_color(self, cluster: Dict) -> str:
        """Get color for cluster based on content"""
        # Infer category from cluster name or services
        cluster_name = cluster["name"].lower()
        if any(word in cluster_name for word in ["network", "cdn", "gateway"]):
            return self.color_schemes["Networking"]["fill"]
        elif any(word in cluster_name for word in ["compute", "application", "server"]):
            return self.color_schemes["Compute"]["fill"]
        elif any(word in cluster_name for word in ["data", "database", "storage"]):
            return self.color_schemes["Database"]["fill"]
        else:
            return self.color_schemes["External"]["fill"]
    
    def _get_cluster_border(self, cluster: Dict) -> str:
        """Get border color for cluster"""
        cluster_name = cluster["name"].lower()
        if any(word in cluster_name for word in ["network", "cdn", "gateway"]):
            return self.color_schemes["Networking"]["border"]
        elif any(word in cluster_name for word in ["compute", "application", "server"]):
            return self.color_schemes["Compute"]["border"]
        elif any(word in cluster_name for word in ["data", "database", "storage"]):
            return self.color_schemes["Database"]["border"]
        else:
            return self.color_schemes["External"]["border"]
    
    def _get_cluster_text(self, cluster: Dict) -> str:
        """Get text color for cluster"""
        cluster_name = cluster["name"].lower()
        if any(word in cluster_name for word in ["network", "cdn", "gateway"]):
            return self.color_schemes["Networking"]["text"]
        elif any(word in cluster_name for word in ["compute", "application", "server"]):
            return self.color_schemes["Compute"]["text"]
        elif any(word in cluster_name for word in ["data", "database", "storage"]):
            return self.color_schemes["Database"]["text"]
        else:
            return self.color_schemes["External"]["text"]
    
    def _get_edge_config(self, connection: Dict) -> Dict:
        """Get edge configuration based on connection type"""
        base_config = {
            "penwidth": str(connection.get("weight", 2)),
            "color": "#2E86AB"
        }
        
        if connection.get("style") == "dashed":
            base_config["style"] = "dashed"
            base_config["color"] = "#666666"
        elif connection.get("style") == "dotted":
            base_config["style"] = "dotted"
            base_config["color"] = "#888888"
        
        if connection.get("label"):
            base_config["label"] = connection["label"]
            base_config["fontcolor"] = "#333333"
        
        return base_config


class AWSArchitectureWorkflow:
    """Main orchestrator with LLM-powered agentic workflow"""
    
    def __init__(self):
        self.extractor = LLMServiceExtractor()
        self.organizer = LLMArchitectureOrganizer()
        self.connector = LLMConnectionBuilder()
        self.generator = EnhancedDiagramGenerator()
    
    def generate_architecture(self, description: str, output_filename: str = "aws_architecture"):
        """Complete LLM-powered architecture generation"""
        
        print("🚀 Starting LLM-Powered AWS Architecture Generation...")
        print("=" * 60)
        
        # Step 1: LLM Service Extraction
        print("🔧 Step 1: LLM Service Extraction...")
        extracted_data = self.extractor.extract_with_llm(description)
        print(f"   ✅ Extracted {len(extracted_data['services'])} services")
        
        # Step 2: LLM Architecture Organization
        print("📊 Step 2: LLM Architecture Organization...")
        organized_data = self.organizer.organize_with_llm(extracted_data)
        print(f"   ✅ Organized into {len(organized_data['clusters'])} clusters")
        print(f"   📐 Layout: {organized_data.get('layout_strategy', 'Mixed layout')}")
        
        # Step 3: LLM Connection Building
        print("🔗 Step 3: LLM Connection Building...")
        connections = self.connector.build_connections_with_llm(extracted_data, organized_data)
        print(f"   ✅ Built {len(connections)} connections")
        
        # Step 4: Generate Diagram
        print("🎨 Step 4: Generating Professional Diagram...")
        self.generator.generate_enhanced_mixed_layout(organized_data, connections, output_filename)
        
        # Save configuration and report
        self._save_artifacts(extracted_data, organized_data, connections, description, output_filename)
        
        print("=" * 60)
        print("✅ Architecture Generation Complete!")
        print(f"   📁 Generated Files:")
        print(f"   - {output_filename}.png (Professional Diagram)")
        print(f"   - {output_filename}_config.json (Full Configuration)")
        print(f"   - {output_filename}_report.md (Architecture Report)")
        
        return {
            "extracted_data": extracted_data,
            "organized_data": organized_data,
            "connections": connections
        }
    
    def _save_artifacts(self, extracted_data: Dict, organized_data: Dict, connections: List[Dict], description: str, output_filename: str):
        """Save all artifacts"""
        
        # Save full configuration
        config = {
            "description": description,
            "extracted_services": extracted_data,
            "organized_architecture": organized_data,
            "connections": connections,
            "timestamp": str(datetime.datetime.now()),
            "version": "1.0"
        }
        
        with open(f"{output_filename}_config.json", 'w') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        # Generate comprehensive report
        self._generate_detailed_report(config, output_filename)
    
    def _generate_detailed_report(self, config: Dict, output_filename: str):
        """Generate detailed architecture report"""
        
        report = f"""# AWS Architecture Report

## Overview
**Generated**: {config['timestamp']}
**Description**: {config['description']}

## Architecture Summary

### Extracted Services
Total Services Found: {len(config['extracted_services']['services'])}

| Service | Type | Step | Category | Description |
|---------|------|------|----------|-------------|
"""
        
        # Services table
        for service in config['extracted_services']['services']:
            report += f"| {service['name']} | {service['type']} | {service.get('step', 'N/A')} | {service.get('category', 'N/A')} | {service.get('description', '')} |\n"
        
        # Architecture Organization
        report += f"""
## Architecture Organization

**Layout Strategy**: {config['organized_architecture'].get('layout_strategy', 'Mixed vertical + horizontal')}

### Clusters
"""
        
        for i, cluster in enumerate(config['organized_architecture']['clusters']):
            report += f"""
#### {i+1}. {cluster['name']}
**Position**: {cluster.get('position', 'N/A')}  
**Flow Direction**: {cluster.get('flow_direction', 'vertical')}  
**Description**: {cluster.get('description', '')}

**Services in this cluster:**
"""
            for service in cluster['services']:
                report += f"- **{service['name']}** (Step {service.get('step', 'N/A')}): {service.get('description', '')}\n"
        
        # Data Flow
        report += """
## Data Flow Connections

| From | To | Label | Style | Direction |
|------|----|-------|-------|-----------|
"""
        for conn in config['connections']:
            report += f"| {conn['from']} | {conn['to']} | {conn.get('label', 'N/A')} | {conn.get('style', 'solid')} | {conn.get('direction', 'forward')} |\n"
        
        # Flow Summary
        if 'flow_summary' in config['extracted_services']:
            report += f"""
## Flow Summary
{config['extracted_services']['flow_summary']}
"""
        
        # Relationships
        if config['extracted_services'].get('relationships'):
            report += """
## Service Relationships
"""
            for rel in config['extracted_services']['relationships']:
                report += f"- **{rel['from']}** → **{rel['to']}**: {rel.get('interaction', 'N/A')} (Priority: {rel.get('priority', 'medium')})\n"
        
        # Main Flow Sequence
        if 'main_flow' in config['organized_architecture']:
            report += """
## Main Flow Sequence
"""
            for i, service in enumerate(config['organized_architecture']['main_flow']):
                report += f"{i+1}. {service}\n"
        
        # AWS Best Practices
        report += """
## AWS Best Practices Checklist

- [ ] Services are properly categorized
- [ ] Logical data flow from top to bottom
- [ ] Monitoring connections to CloudWatch
- [ ] Security services properly positioned
- [ ] Clear separation of concerns between clusters
- [ ] Appropriate use of vertical and horizontal layouts

## Recommendations

1. **Security**: Ensure all services have proper IAM roles and security groups
2. **Monitoring**: Set up CloudWatch alarms for critical services
3. **Scalability**: Consider Auto Scaling for compute-intensive services
4. **Cost Optimization**: Review service sizing and storage classes
"""

        with open(f"{output_filename}_report.md", 'w') as f:
            f.write(report)

# Enhanced AdvancedDiagramGenerator with better mixed layout
class EnhancedDiagramGenerator(AdvancedDiagramGenerator):
    """Enhanced generator with better mixed layout support"""
    
    def generate_enhanced_mixed_layout(self, organized_data: Dict, connections: List[Dict], output_filename: str):
        """Generate diagram with improved vertical + horizontal layout"""
        
        graph_attr = {
            "fontsize": "14",
            "fontname": "Helvetica",
            "bgcolor": "white",
            "pad": "1.5",
            "splines": "ortho",
            "nodesep": "1.0",
            "ranksep": "1.5",
            "dpi": "300",
            "compound": "true",
            "rankdir": "TB",
            "concentrate": "true"  # Cleaner edge routing
        }
        
        node_attr = {
            "fontsize": "11",
            "fontname": "Helvetica",
            "style": "filled,rounded",
            "fixedsize": "true",
            "width": "2.2",
            "height": "1.6",
            "penwidth": "2.0",
            "margin": "0.3"
        }
        
        edge_attr = {
            "fontsize": "10",
            "fontname": "Helvetica",
            "penwidth": "2.5",
            "arrowsize": "1.0",
            "fontcolor": "#333333"
        }
        
        with Diagram(
            "AWS Architecture Diagram",
            show=False,
            direction="TB",
            filename=output_filename,
            graph_attr=graph_attr,
            node_attr=node_attr,
            edge_attr=edge_attr,
            outformat="png"
        ):
            services = {}
            clusters_dict = {}
            
            # First pass: Create all clusters and services
            for cluster in organized_data["clusters"]:
                cluster_style = {
                    "style": "rounded,filled,bold",
                    "fillcolor": self._get_cluster_color(cluster),
                    "color": self._get_cluster_border(cluster),
                    "fontcolor": self._get_cluster_text(cluster),
                    "fontsize": "12",
                    "labeljust": "l",
                    "labelloc": "t",
                    "penwidth": "3.0"
                }
                
                # Determine cluster direction
                cluster_direction = "TB" if cluster.get("flow_direction") == "vertical" else "LR"
                
                with Cluster(cluster["name"], graph_attr=cluster_style, direction=cluster_direction) as cluster_obj:
                    cluster_services = {}
                    for service_config in cluster["services"]:
                        service_type = SERVICE_MAP.get(service_config["type"])
                        if service_type:
                            # Enhanced label with step number and type
                            # step = service_config.get('step', '')
                            # label = f"{service_config['name']}\n[{service_config['type']}]"
                            # if step:
                            #     label = f"[{step}] {label}"
                            label = service_config['name']

                            
                            service_node = service_type(label)
                            cluster_services[service_config["name"]] = service_node
                    
                    clusters_dict[cluster["name"]] = cluster_services
                    services.update(cluster_services)
            
            # Second pass: Create intelligent connections
            for conn in connections:
                from_service = services.get(conn["from"])
                to_service = services.get(conn["to"])
                
                if from_service and to_service:
                    edge_config = self._get_enhanced_edge_config(conn)
                    
                    # Add the connection
                    if conn.get("label"):
                        from_service >> Edge(**edge_config) >> to_service
                    else:
                        from_service >> Edge(**edge_config) >> to_service
    
    def _get_enhanced_edge_config(self, connection: Dict) -> Dict:
        """Get enhanced edge configuration with better styling"""
        
        # Base configuration
        base_config = {
            "penwidth": str(connection.get("weight", 3)),
            "arrowsize": "1.2"
        }
        
        # Style-based configurations
        style = connection.get("style", "solid")
        if style == "dashed":
            base_config.update({
                "style": "dashed",
                "color": "#666666",
                "penwidth": "2.0"
            })
        elif style == "dotted":
            base_config.update({
                "style": "dotted", 
                "color": "#888888",
                "penwidth": "1.5"
            })
        else:  # solid
            base_config.update({
                "style": "solid",
                "color": "#2E86AB"
            })
        
        # Add label if present
        if connection.get("label"):
            base_config.update({
                "label": connection["label"],
                "fontcolor": "#333333"
            })
        
        elif style == "dotted":
            base_config.update({
                "style": "dotted", 
                "color": "#888888",
                "penwidth": "1.5"
            })
        else:  # solid
            base_config.update({
                "style": "solid",
                "color": "#2E86AB"
            })
        
        # Direction-based configurations
        direction = connection.get("direction", "forward")
        if direction == "bidirectional":
            base_config["dir"] = "both"
            base_config["color"] = "#7B1FA2"  # Purple for bidirectional
        
        # Priority-based styling
        priority = connection.get("priority", "medium")
        if priority == "high":
            base_config["penwidth"] = "4.0"
            base_config["color"] = "#D32F2F"  # Red for high priority
        elif priority == "low":
            base_config["penwidth"] = "1.5"
            base_config["color"] = "#757575"  # Gray for low priority
        
        # Add label if present
        if connection.get("label"):
            base_config.update({
                "label": connection["label"],
                "fontcolor": "#1A237E",
                "fontsize": "9",
                "fontname": "Helvetica-Bold"
            })
        
        return base_config

class ArchitectureToolRunner:
    """Encapsulates the AWS architecture generation workflow."""

    def __init__(self,client,memory_id,app_context):
        # memoryManager = MemoryManager()
        # client=memoryManager.get_client()
        # memory_id=memoryManager.get_memory_id()

        self.memory_id = memory_id
        self.workflow = AWSArchitectureWorkflow()
        self.client= client
        self.session_id=app_context.session_id
        self.actor_id=app_context.actor_id


    @tool
    def Architecture_diagram(self,transcript) -> dict:
        """
        Generate AWS architecture diagram from transcript.

        Args:
            transcript (str): Input architecture description. If None, attempts to load from memory.

        Returns:
            dict: Output paths and extracted data.
        """
        # Load from memory if transcript not provided
        transcript_hook = MemoryHookProvider(self.client, self.memory_id)
   
        # Create temporary directory for outputs
        with tempfile.TemporaryDirectory() as temp_dir:
            output_prefix = os.path.join(temp_dir, f"architecture_diagram-{uuid.uuid4()}")
            
            # Generate architecture to temp directory
            result = self.workflow.generate_architecture(
                description=transcript,
                output_filename=output_prefix  # Write to temp location
            )
            
            s3_client = boto3.client("s3")
            bucket_name = "hackathon-result-1"
            timestamp = str(int(time.time()))
            
            s3_urls = {}
            
            # Upload generated files from temp directory
            expected_files = {
                "diagram": f"{output_prefix}.png",
                "report": f"{output_prefix}_report.md", 
                "config": f"{output_prefix}_config.json"
            }
            
            for file_type, file_path in expected_files.items():
                if os.path.exists(file_path):
                    s3_key = f"architecture_{file_type}_{timestamp}.{file_path.split('.')[-1]}"
                    
                    with open(file_path, 'rb') as file:
                        s3_client.upload_fileobj(
                            file,
                            bucket_name,
                            s3_key,
                            ExtraArgs={
                                'ContentType': {
                                    'png': 'image/png',
                                    'md': 'text/markdown', 
                                    'json': 'application/json'
                                }.get(file_path.split('.')[-1], 'application/octet-stream')
                            }
                        )
                    
                    s3_urls[file_type] = f"https://hackathon-result-1.s3.us-east-1.amazonaws.com/{s3_key}"
            self.client.create_event(
                    memory_id=self.memory_id,
                    actor_id=self.actor_id,
                    session_id=self.session_id,
                    messages=[(json.dumps(s3_urls), "ASSISTANT")]
                )

        return {
            "status": "success",
            "message": "Architecture generated and uploaded to S3",
            "s3_urls": s3_urls
        }
        
