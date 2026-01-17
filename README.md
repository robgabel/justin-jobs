# Justin Jobs - AI-Powered Job Advisor

An intelligent job search assistant designed to help college students find internships and full-time positions. The system builds deep context about job seekers and provides AI-powered assistance for job search, company research, and application materials.

## Features

- **Profile Building**: Upload resume, answer questions, and build a comprehensive profile
- **Job Tracking**: Manually add job postings and track application status
- **Company Research**: AI-powered research on companies using web search and scraping
- **Content Generation**: Generate personalized cover letters and outreach emails
- **STAR Stories**: Store and organize behavioral interview examples
- **Semi-Autonomous Agents**: AI agents suggest actions that require user approval

## Tech Stack

- **Backend**: Python FastAPI
- **Frontend**: React with TypeScript (Vite)
- **Database**: Supabase (PostgreSQL)
- **AI**: Claude (Anthropic API)
- **Styling**: Tailwind CSS

## Project Structure

```
justin-jobs/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration
│   │   ├── database.py          # Supabase client
│   │   ├── models/              # Pydantic models
│   │   ├── routes/              # API endpoints
│   │   ├── agents/              # AI agents
│   │   ├── tools/               # Agent tools
│   │   └── utils/               # Utilities
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── api/                 # API client
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   ├── App.tsx
│   │   └── main.tsx
│   └── package.json
├── supabase_schema.sql          # Database schema
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.10+
- Node.js 18+
- Supabase account
- Anthropic API key

### 1. Supabase Setup

1. Create a new Supabase project at https://supabase.com
2. In the SQL Editor, run the schema from `supabase_schema.sql`
3. Get your project URL and anon key from Settings > API

### 2. Backend Setup

```bash
# Navigate to backend directory
cd justin-jobs/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your credentials
# Required:
# - SUPABASE_URL
# - SUPABASE_KEY
# - ANTHROPIC_API_KEY
# Optional:
# - TAVILY_API_KEY (for enhanced web search)

# Run the server
python run.py
```

The backend will be available at http://localhost:8000

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd justin-jobs/frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will be available at http://localhost:5173

## Usage Guide

### 1. Create a Profile

1. Navigate to the Profile page
2. Click "New Profile"
3. Enter name and email
4. Upload your resume (PDF or TXT)
5. Use the AI Profile Builder to answer questions and build your profile

### 2. Add Jobs

1. Navigate to the Jobs page
2. Click "Add Job"
3. Enter job details (title, company, description, URL, etc.)
4. Track status as you progress through the application process

### 3. Research Companies

1. Navigate to the Companies page
2. Click "Research Company"
3. Enter company name (and optionally website and job title)
4. AI will search the web and compile research including:
   - Company overview and culture
   - Recent news
   - Key people

### 4. Generate Application Content

1. From the Jobs page, select a job
2. Click "Generate Content"
3. AI will create:
   - Personalized cover letter
   - Outreach email templates
   - Application strategy

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation.

### Main Endpoints

- **Profiles**: `/profiles`
  - Create, read, update, delete profiles
  - Upload resume
  - Build profile with AI

- **Jobs**: `/jobs`
  - Track job opportunities
  - Link to companies
  - Update application status

- **Companies**: `/companies`
  - Store company information
  - Research companies with AI

- **Content**: `/content`
  - Generate cover letters
  - Create outreach emails
  - Track applications

## Environment Variables

### Backend (.env)

```env
# Required
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Optional
TAVILY_API_KEY=your_tavily_api_key
PORT=8000
HOST=0.0.0.0
```

### Frontend (.env.local - optional)

```env
VITE_API_URL=http://localhost:8000
```

## Development

### Backend Development

```bash
cd backend
source venv/bin/activate
python run.py
```

The server will reload automatically when you make changes.

### Frontend Development

```bash
cd frontend
npm run dev
```

Vite will hot-reload when you make changes.

### Building for Production

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm run build
```

## Database Schema

The database includes the following tables:

- **profiles**: User profiles with resume and career information
- **star_answers**: Behavioral interview stories in STAR format
- **jobs**: Job postings being tracked
- **companies**: Company information and research
- **applications**: Application materials and status
- **agent_tasks**: AI agent task queue for approval workflow

See `supabase_schema.sql` for the complete schema.

## AI Agents

### Profile Builder Agent
- Extracts information from resumes
- Asks clarifying questions
- Builds comprehensive profiles

### Company Researcher Agent
- Searches the web for company information
- Scrapes company websites
- Finds recent news and key people
- Generates research summaries

### Content Generator Agent
- Analyzes job descriptions
- Matches user profile to requirements
- Generates personalized cover letters
- Creates outreach email templates
- Provides application strategy

## Future Enhancements

- Automated job board scraping
- LinkedIn integration
- Email integration for outreach tracking
- Interview preparation agent
- Application analytics
- Multi-user authentication
- Mobile app

## Contributing

This is a private project for Rob and Justin. If you have suggestions or find bugs, please create an issue.

## License

Private - All rights reserved

## Support

For questions or issues, please contact the project maintainers.
