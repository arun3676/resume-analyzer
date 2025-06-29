# Resume Analyzer

A powerful AI-powered resume analysis tool that helps recruiters and job seekers by providing detailed insights into resumes and job descriptions.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## Features

- 🔍 **Smart Resume Analysis**: Extract key information from resumes including skills, experience, and education
- 🤖 **AI-Powered Matching**: Compare resumes with job descriptions using advanced AI models
- 📊 **Detailed Insights**: Get comprehensive analysis and recommendations
- 🚀 **Fast and Efficient**: Built with FastAPI for high performance
- 🐳 **Docker Support**: Easy deployment with Docker
- 🌐 **Web Interface**: Easy-to-use web interface for uploading and analyzing resumes

## Live Demo

Try the live version at: [https://resume-analyzer.onrender.com](https://resume-analyzer.onrender.com)

## Tech Stack

- **Backend**: FastAPI, Python
- **AI/ML**: OpenAI, Gemini, LangChain
- **Database**: ChromaDB
- **Frontend**: HTML, CSS, JavaScript
- **Deployment**: Docker, Render.com

## Prerequisites

- Python 3.8+
- Docker (optional)
- OpenAI API Key
- Gemini API Key
- PromptLayer API Key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/arun3676/resume-analyzer.git
cd resume-analyzer
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

## Running the Application

### Using Docker (Recommended)

```bash
docker-compose up
```

### Local Development

```bash
uvicorn app.main:app --reload
```

The application will be available at `http://localhost:8000`

## API Documentation

Once the application is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
resume-analyzer/
├── app/
│   ├── agents/         # AI agent implementations
│   ├── services/       # Core business logic
│   ├── templates/      # HTML templates
│   ├── utils/          # Utility functions
│   ├── config.py       # Configuration
│   └── main.py         # FastAPI application
├── data/               # Data storage
├── tests/              # Test files
├── notebooks/          # Jupyter notebooks
├── requirements.txt    # Python dependencies
└── docker-compose.yml  # Docker configuration
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

Arun Kiran - [@arun3676](https://github.com/arun3676)

Project Link: [https://github.com/arun3676/resume-analyzer](https://github.com/arun3676/resume-analyzer)

## Deployment

This application can be easily deployed to Render.com:

1. Sign up for a free account at [Render.com](https://render.com)
2. Click "New +" and select "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - Name: `resume-analyzer`
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add the following environment variables:
   - `OPENAI_API_KEY`
   - `GEMINI_API_KEY`
   - `PROMPTLAYER_API_KEY`
6. Click "Create Web Service"

The application will be automatically deployed and available at `https://resume-analyzer.onrender.com`