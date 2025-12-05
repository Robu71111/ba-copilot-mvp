🤖 BA Copilot - AI Assistant for Business Analysts
An AI-powered assistant that automates the Business Analyst workflow from requirements gathering to acceptance criteria generation.

✨ Features
📄 Document Processing - Upload .txt, .docx, or .pdf files
📋 Requirements Extraction - AI-powered functional and non-functional requirement identification
📖 User Story Generation - Agile user stories in Scrum format with story points
✅ Acceptance Criteria - Given-When-Then test scenarios in Gherkin format
💾 Project Management - Save and manage multiple projects
📊 Export Options - Download as text, JIRA CSV, or Gherkin files
🌐 Cloud Deployment - Deployable to Vercel
🏗️ Architecture
React Frontend (Vercel) → FastAPI Backend (Vercel) → Google Gemini API
🚀 Quick Start
Prerequisites
Node.js 16+ and npm
Python 3.9+
Gemini API key (free from https://makersuite.google.com/app/apikey)
Installation
Clone the repository
bash
git clone https://github.com/yourusername/ba-copilot-mvp.git
cd ba-copilot-mvp
Install frontend dependencies
bash
cd frontend
npm install
Install backend dependencies
bash
cd ../backend
pip install -r requirements.txt
Add your Gemini API key
Open backend/core/config.py
Line 30: Replace 'ENTER_YOUR_GEMINI_API_KEY_HERE' with your actual key
Create frontend environment file
bash
cd ../frontend
cp .env.example .env
Running Locally
Terminal 1 - Backend:

bash
cd backend
python -m uvicorn api.main:app --reload --port 8000
Terminal 2 - Frontend:

bash
cd frontend
npm start
Open http://localhost:3000 in your browser.

🌐 Deployment to Vercel
Deploy Backend
bash
cd backend
vercel
Note the deployed URL (e.g., https://ba-copilot-backend.vercel.app)

Configure Environment Variables
Go to Vercel Dashboard → Your Backend Project
Settings → Environment Variables
Add GEMINI_API_KEY with your actual key
Redeploy: vercel --prod
Deploy Frontend
Update frontend/.env:
bash
REACT_APP_API_URL=https://your-backend-url.vercel.app
Update frontend/vercel.json with your backend URL
Deploy:
bash
cd frontend
vercel --prod
📚 API Documentation
After running the backend, visit:

Local: http://localhost:8000/docs
Production: https://your-backend-url.vercel.app/docs
🛠️ Tech Stack
Frontend
React 18
Axios (API calls)
React Markdown
React Dropzone
Lucide React (icons)
Backend
FastAPI
Uvicorn
Google Generative AI (Gemini)
python-docx, PyPDF2
SQLite
Deployment
Vercel (Frontend & Backend)
📖 Usage
Create a Project
Click "New Project" in sidebar
Enter project details
Add Input
Upload document, paste text, or use mock transcript
Minimum 50 characters required
Extract Requirements
Click "Extract Requirements"
Wait 10-30 seconds for AI processing
Review functional and non-functional requirements
Generate User Stories
Click "Generate User Stories"
Wait 15-45 seconds
Review Agile user stories with priorities and story points
Create Acceptance Criteria
Select a user story
Click "Generate Acceptance Criteria"
Review Given-When-Then scenarios
Export
Download as text, JIRA CSV, or Gherkin format
🔑 Environment Variables
Backend (backend/core/config.py)
GEMINI_API_KEY - Required for AI processing
GOOGLE_APPLICATION_CREDENTIALS - Optional, for voice transcription
Frontend (.env)
REACT_APP_API_URL - Backend API URL
📁 Project Structure
ba-copilot-mvp/
├── frontend/              # React application
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── services/     # API service layer
│   │   ├── App.jsx       # Main app
│   │   └── App.css       # Styles
│   └── package.json
│
├── backend/              # FastAPI application
│   ├── api/
│   │   ├── main.py      # FastAPI entry point
│   │   └── routes/      # API endpoints
│   ├── core/
│   │   └── config.py    # Configuration & API keys
│   ├── services/        # Business logic
│   └── requirements.txt
│
└── database/            # SQLite database
    └── ba_copilot.db
🐛 Troubleshooting
"Gemini API not configured"
Check backend/core/config.py line 30
Ensure API key is correct and no extra spaces
CORS errors
Update backend/api/main.py CORS settings
Add your frontend URL to allow_origins
Module not found
bash
pip install -r backend/requirements.txt
npm install --prefix frontend
Port already in use
bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
🎓 Academic Context
This project was developed as a Master's capstone project demonstrating:

Full-stack development (React + FastAPI)
AI/ML integration (Google Gemini API)
Requirements engineering automation
Agile/Scrum methodology
Cloud deployment (Vercel)
RESTful API design
📝 License
MIT License - Feel free to use for educational purposes

🙏 Acknowledgments
Google Gemini API for AI capabilities
FastAPI for excellent API framework
React team for frontend framework
Vercel for deployment platform
📧 Contact
For questions or feedback:

Email: your.email@example.com
GitHub: https://github.com/yourusername
LinkedIn: your-linkedin-profile
Built with ❤️ for Business Analysts