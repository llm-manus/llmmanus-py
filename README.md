# MoocManus: Commercial-Grade Multi-Agent Full-Stack Application
[![Course Rating](https://img.shields.io/badge/Rating-10.0/10-brightgreen)](https://coding.imooc.com/class/955.html)
[![Learning Count](https://img.shields.io/badge/Learners-168+-blue)](https://coding.imooc.com/class/955.html)
[![Difficulty](https://img.shields.io/badge/Difficulty-Intermediate-orange)](https://coding.imooc.com/class/955.html)
[![Duration](https://img.shields.io/badge/Duration-45H-red)](https://coding.imooc.com/class/955.html)

## Overview
MoocManus is a commercial-grade general AI agent system built from scratch, benchmarked against core modules of Manus. Unlike passive Q&A or content-generation tools, it acts as an active executor that can independently think, plan, and accomplish complex real-world tasks end-to-end.

This project is developed through the course **"From 0 to 1: Build Commercial Multi-Agent Full-Stack Applications with MCP+A2A"**, covering the complete workflow from single/multi-agent design, distributed architecture to full-stack engineering. It equips developers with the core capabilities needed to become in-demand AI multi-agent full-stack engineers.

## Core Features
- **Autonomous Task Processing**: Breaks down instructions into subtasks, assigns to role-specific agents, and delivers integrated results.
- **MCP+A2A Protocol Integration**: Enables efficient communication and collaboration between distributed agents.
- **Multi-Modal Support**: Seamlessly integrates with OpenAI/DeepSeek models to handle files, images, videos, and web search.
- **Full-Stack Engineering**: Combines FastAPI backend, Next.js frontend, and Docker deployment for production-ready delivery.
- **Enterprise-Grade Practical Cases**: Includes research report generation, price comparison, document conversion, and web scraping.
- **Distributed Architecture**: Scalable agent network with task auto-planning and high availability.

## Tech Stack
### Frontend
- Next.js (React Framework)
- TailwindCSS (Styling)
- Fetch.js (API Communication)
- novnc (Browser VNC Client)
- TailwindCSS & Monaco Editor

### Backend
- FastAPI (API Development)
- Python & AsyncIO (Coroutine)
- Pydantic (Data Validation)
- Redis (Caching & Task Queue)
- PostgreSQL (Business Database)

### AI & Agent Core
- MCP/A2A Protocols (Agent Collaboration)
- ReACT Framework & CoT (Chain of Thought)
- LLM Integration (OpenAI SDK, DeepSeek API)
- Prompt Engineering
- Multi-Modal Processing

### DevOps & Tools
- Docker & Docker Compose (Containerization)
- Playwright/BrowserUse (Browser Automation)
- Docker Sandbox (Isolated Execution Environment)
- Supervisor (Process Management)
- Bing Search API & Jina.ai (Search Integration)

## Learning Objectives
1. Master core capabilities of building enterprise-level multi-agent systems.
2. Proficient in cutting-edge agent tech stacks (ReACT, CoT, MCP/A2A).
3. Acquire full-stack engineering skills from API design to deployment.
4. Transform from "programming thinking" to "system thinking".

## Installation & Deployment
1. Clone the repository
   ```bash
   git clone <repository-url>
   cd MoocManus
   ```
2. Install dependencies
   ```bash
   # Backend dependencies
   cd backend
   pip install -r requirements.txt
   
   # Frontend dependencies
   cd frontend
   npm install
   ```
3. Configure environment variables
   - Set up LLM API keys (OpenAI/DeepSeek)
   - Configure MCP server settings (Qiniu, etc.)
4. One-click deployment with Docker Compose
   ```bash
   docker-compose up -d
   ```

## Project Structure
```
MoocManus/
├── backend/                # FastAPI Backend
│   ├── api/                # API Routes
│   ├── agents/             # Agent Logic & Protocols (MCP/A2A)
│   ├── services/           # Business Services
│   ├── models/             # Data Models (Pydantic)
│   ├── utils/              # Utility Functions
│   └── Dockerfile
├── frontend/               # Next.js Frontend
│   ├── components/         # UI Components
│   ├── pages/              # Route Pages
│   ├── styles/             # TailwindCSS Styles
│   └── Dockerfile
├── docker-compose.yaml     # Deployment Configuration
└── README.md
```

## License
This project is for educational purposes only. Please refer to the course terms for commercial use authorization.
