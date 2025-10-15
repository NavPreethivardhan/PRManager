# PR Copilot - AI-Powered PR Management System

An intelligent GitHub App that automates PR triage, prioritization, and workflow optimization to prevent maintainer burnout.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- OpenAI API key
- GitHub account (for creating GitHub App)

### 1. Clone and Setup

```bash
git clone <your-repo>
cd PRManager
cp env.example .env
```

### 2. Configure Environment

Edit `.env` file:

```bash
# OpenAI API Key (required)
OPENAI_API_KEY=your_openai_api_key_here

# GitHub App Configuration (you'll get these after creating the app)
GITHUB_APP_ID=your_github_app_id_here
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here

# Database URLs (defaults work for Docker)
DATABASE_URL=postgresql://prcopilot:password@db:5432/prcopilot
REDIS_URL=redis://redis:6379/0

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### 3. Create GitHub App

1. Go to [GitHub Settings → Developer Settings → GitHub Apps](https://github.com/settings/apps)
2. Click "New GitHub App"
3. Fill in the details:
   - **GitHub App name**: `PR Copilot`
   - **Homepage URL**: `https://your-domain.com`
   - **Webhook URL**: `https://your-domain.com/webhooks/github`
   - **Webhook secret**: Generate a random secret and add to `.env`
4. Set permissions:
   - **Contents**: Read
   - **Metadata**: Read  
   - **Pull requests**: Write
   - **Issues**: Write
5. Subscribe to events:
   - `pull_request`
   - `issue_comment`
6. Click "Create GitHub App"
7. Copy the **App ID** to your `.env` file
8. Generate and download the **Private Key** - save as `github_private_key.pem`

### 4. Run with Docker

```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### 5. Install on Test Repository

1. Go to your GitHub App settings
2. Click "Install App" 
3. Select a test repository
4. Install the app

### 6. Test the Bot

1. Create a test PR in your repository
2. The bot should automatically analyze and comment
3. Try the command: `@PRCoPilot /triage`

## 🏗️ Architecture

### Tech Stack

- **Backend**: Python 3.11 + FastAPI
- **Database**: PostgreSQL 15 + Redis
- **Task Queue**: Celery + Redis
- **LLM**: OpenAI GPT-4o Mini
- **GitHub Integration**: PyGithub + GitHub App
- **Deployment**: Docker + Docker Compose

### Project Structure

```
PRManager/
├── api/                    # FastAPI application
│   ├── main.py            # App entry point
│   ├── routes/            # API routes
│   │   ├── webhooks.py    # GitHub webhook handlers
│   │   └── health.py      # Health checks
│   ├── services/          # Business logic
│   │   ├── classifier.py  # PR classification
│   │   └── github_client.py # GitHub API client
│   └── database.py        # Database models
├── workers/               # Background tasks
│   ├── celery_app.py     # Celery configuration
│   └── process_pr.py     # PR processing tasks
├── docker-compose.yml     # Local development
├── requirements.txt       # Python dependencies
└── README.md
```

## 🤖 Features

### MVP (Phase 1)

- ✅ **PR Classification** - 6 categories (Ready to Merge, Needs Discussion, etc.)
- ✅ **Priority Scoring** - 0-100 based on impact and urgency
- ✅ **GitHub Bot Commands** - `@PRCoPilot /triage`, `@PRCoPilot /help`
- ✅ **Basic Context Analysis** - PR metadata and diff analysis
- ✅ **Webhook Integration** - Real-time PR event processing

### Planned Features

- 🔄 **Smart Reviewer Routing** - Route PRs to right reviewers
- 📊 **Analytics Dashboard** - PR metrics and maintainer insights
- 🚨 **Burnout Detection** - Monitor maintainer workload
- 🔍 **Full-Repo RAG** - Vector search for better context
- 📧 **Daily Digests** - Summarized PR reports

## 📊 PR Classification Categories

| Category | Description | Emoji |
|----------|-------------|-------|
| **Ready to Merge** | All checks pass, trusted contributor, no issues | ✅ |
| **Needs Architecture Discussion** | Large/breaking changes requiring design review | 🏗️ |
| **Needs Minor Fixes** | Small issues (tests, style, docs, minor bugs) | 🔧 |
| **Needs Mentor Support** | First-time contributor or needs guidance | 👥 |
| **Needs Maintainer Decision** | Policy questions or roadmap decisions | 🤔 |
| **Blocked/Stale** | Conflicts, failing CI, or inactive >14 days | ⏸️ |

## 🛠️ Development

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start database
docker-compose up -d db redis

# Run API server
uvicorn api.main:app --reload

# Run Celery worker
celery -A workers.celery_app worker --loglevel=info
```

### Testing

```bash
# Run tests
pytest

# Test webhook locally (using ngrok)
ngrok http 8000
# Update GitHub App webhook URL to your ngrok URL
```

### Database Migrations

```bash
# Generate migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

## 🚀 Deployment

### Option 1: Railway (Recommended for MVP)

1. Connect your GitHub repo to [Railway](https://railway.app)
2. Add environment variables in Railway dashboard
3. Deploy automatically on push

### Option 2: Render

1. Connect repo to [Render](https://render.com)
2. Create Web Service with Docker
3. Add environment variables
4. Deploy

### Option 3: Fly.io

1. Install Fly CLI
2. Run `fly launch`
3. Configure secrets: `fly secrets set OPENAI_API_KEY=...`
4. Deploy: `fly deploy`

## 📈 Monitoring

### Health Checks

- `GET /health/` - Basic health check
- `GET /health/ready` - Readiness with database connectivity

### Logs

```bash
# View API logs
docker-compose logs -f api

# View worker logs  
docker-compose logs -f worker

# View all logs
docker-compose logs -f
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for LLM | Required |
| `GITHUB_APP_ID` | GitHub App ID | Required |
| `GITHUB_WEBHOOK_SECRET` | Webhook verification secret | Required |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://prcopilot:password@db:5432/prcopilot` |
| `REDIS_URL` | Redis connection string | `redis://redis:6379/0` |
| `ENVIRONMENT` | Environment (development/production) | `development` |
| `LOG_LEVEL` | Logging level | `INFO` |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/your-org/pr-copilot/issues)
- **Documentation**: [Wiki](https://github.com/your-org/pr-copilot/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/pr-copilot/discussions)

---

**Built with ❤️ for the open source community**
