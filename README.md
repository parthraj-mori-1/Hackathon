# 🤖 Hackathon Sales Assistant Chatbot

A powerful AI-powered sales assistant chatbot built for hackathons, featuring intelligent conversation handling, document generation, and multi-modal capabilities. This project leverages AWS Bedrock, React/Streamlit frontends, and specialized tools for sales workflow automation.

## 🌐 Live Demo

**Try the chatbot now**: [https://master.d2pfy4c9nrrn4t.amplifyapp.com/](https://master.d2pfy4c9nrrn4t.amplifyapp.com/)

*No installation required - start using the sales assistant immediately!*

## 🚀 Features

### Core Capabilities
- **Intelligent Conversation**: AI-powered chatbot using AWSsummaries with action items
- **Statement of Work (SOW)**: Create professional SOW documents from requirements
- **Architecture Diagrams**: Generate visual system architecture diagrams
- **Email Automation**: Send generated documents via Gmail integration
- **Web Search**: Research current market trends and information
- **Memory Management**: Persistent conversation context across sessions
- **Multi-Frontend Support**: React and Streamlit interfaces

## 🏗️ Architecture

```
├── main.py                 # Main application entry point
├── Context.py             # Global session/actor context
├── Memory.py              # Memory management for conversations
├── Tools/                 # Specialized AI tools
│   ├── Architecture_tool.py
│   ├── Gmail_tool.py
│   ├── Mom_tool.py
│   ├── Sow_tool.py
│   ├── Transcript_tool.py
│   └── Search_tool.py
├── Hooks/                 # Memory hooks for context persistence
├── Frontend/
│   ├── React/            # React-based UI
│   └── Streamlit/        # Streamlit-based UI
└── requirements.txt
```

## 🛠️ Tech Stack

- **Backend**: Python, AWS Bedrock, Strands Agents
- **AI/ML**: AWS Bedrock Claude models
- **Storage**: AWS S3, AWS Memory DB
- **Frontend**: React.js, Streamlit
- **APIs**: AWS Lambda, API Gateway
- **Email**: Gmail API integration
- **Search**: DuckDuckGo integration

## 📋 Prerequisites

- Python 3.8+
- AWS Account with Bedrock access
- Gmail API credentials
- Node.js 16+ (for React frontend)

## ⚙️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd sales-assistant-chatbot
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Setup
Create a `.env` file in the root directory:
```env
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-east-1
BUCKET_NAME=your_s3_bucket_name
MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0/haiku
MEMORY_NAME=your_memory_name
```

### 4. Frontend Setup (React)
```bash
cd Frontend/React
npm install
npm start
```

### 5. Frontend Setup (Streamlit)
```bash
cd Frontend/Streamlit
streamlit run streamlit_ui.py
```

### Available Commands

1. **Generate MOM**: `"Generate MOM from the meeting"`
2. **Create SOW**: `"Generate SOW for the project"`
3. **Architecture Diagram**: `"Create architecture diagram"`
4. **Transcribe Video**: `"Transcribe video from S3"`
5. **Send Email**: `"Send the document via email"`
6. **Web Search**: `"Research latest AI trends"`

### API Endpoints

- **Start Job**: `POST /dev/Hackathon-sales`
- **Get Result**: `GET /dev/Hackathon-sales-result?job_id={id}`

## 🔧 Tool Descriptions

### 📝 MOM Generator
- Extracts meeting transcripts from memory
- Generates structured minutes with action items
- Stores results in S3 with public URLs

### 📄 SOW Generator  
- Creates professional Statement of Work documents
- Uses meeting context for requirements gathering
- Outputs formatted business documents

### 🏛️ Architecture Diagram Generator
The Architecture Tool automatically generates professional system architecture diagrams from meeting transcripts or user requirements. 

**Key Features:**
- **Intelligent Analysis**: Analyzes meeting content to identify system components, services, and relationships
- **Visual Generation**: Creates clean, professional diagrams using Graphviz
- **Multiple Formats**: Supports various architectural patterns (microservices, monolithic, cloud-native)
- **Auto-Layout**: Automatically arranges components for optimal readability
- **S3 Integration**: Stores generated diagrams with public URLs for easy sharing

**Example Output:**
![Architecture Diagram Example](https://hackathon-result-1.s3.us-east-1.amazonaws.com/Hackathon_5.jpg)

**Usage Examples:**
- `"Create architecture diagram for microservices setup"`
- `"Generate system design from meeting transcript"`
- `"Design cloud architecture for the discussed solution"`

The tool intelligently extracts technical requirements from conversations and transforms them into visual representations that stakeholders can easily understand.
- **Web Search**: Real-time web search capabilities for market research
- **Memory Management**: Persistent conversation memory across sessions

### Tools & Integrations
- **Architecture Tool**: Generate system architecture diagrams
- **Gmail Tool**: Send automated emails with generated documents
- **MOM Generator**: Create structured meeting minutes with action items
- **SOW Generator**: Generate comprehensive statements of work
- **Transcript Tool**: Process and transcribe S3-hosted videos
- **Search Tool**: Web search for current market information

## 🏗️ Architecture

```
├── Frontend/
│   ├── React/          # React-based web interface
│   └── Streamlit/      # Streamlit-based UI for rapid prototyping
├── Tools/              # Specialized AI tools
├── Hooks/              # Memory and state management
├── Lambda_codes_response_part/  # AWS Lambda functions
└── awble Architecture
- Modular tool system for easy feature addition
- Hook-based memory management
- Configurable AI model selection

## 🔒 Security & Best Practices

- Environment-based configuration management
- AWS IAM role-based access control
- Secure S3 bucket policies
- Input validation and sanitization
- Error handling and logging

## 📊 Performance Features

- Asynchronous processing for long-running tasks
- Memory-efficient video processing
- Optimized S3 operations
- Caching for frequently accessed data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

**AWS Credentials Error**
```bash
# Ensure AWS credentials are properly configured
aws configure list
```

**Memory Management Issues**
```bash
# Check memory instance status
python -c "from Memory import MemoryManager; mm = MemoryManager(); print(mm.get_memory_id())"
```

**Frontend Connection Issues**
- Verify API endpoints in frontend configuration
- Check CORS settings for cross-origin requests
- Ensure proper session ID management
t changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🏆 Hackathon Achievements

- **Automated Sales Workflow**: End-to-end automation from meeting to deliverables
- **Multi-Modal AI Integration**: Video, text, and diagram generation
- **Real-time Processing**: Instant responses with persistent memory
- **Professional Output**: Business-ready documents and communications

## 📞 Support

For questions or issues:
- Create an issue in the repository
- Contact the development team
- Check the troubleshooting section

---

Built with ❤️ for the hackathon by [Your Team Name]
## 🎯 Hackathon Tips

1. **Quick Demo Setup**: Use Streamlit interface for fastest deployment
2. **Feature Showcase**: Demonstrate video transcription → MOM generation → Email workflow
3. **Scalability Story**: Highlight AWS Lambda serverless architecture
4. **AI Integration**: Showcase multiple AI tools working together seamlessly

## 📞 Support

For hackathon support and questions:
- Check the troubleshooting section above
- Review AWS