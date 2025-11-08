# MemeCraft Pro 🎨

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![React](https://img.shields.io/badge/React-19-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.1-green.svg)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-6.0-brightgreen.svg)](https://www.mongodb.com/)

> **Create viral memes with AI-powered tools** - A professional SaaS platform for meme creation, featuring advanced editing tools, AI generation, animated GIFs, and trending content discovery.

![MemeCraft Pro Dashboard](https://via.placeholder.com/1200x600/0f172a/00ff88?text=MemeCraft+Pro+Dashboard)

## 🌟 Features

### 🎨 Professional Meme Editor
- **Advanced Canvas Editor** powered by Fabric.js
- Multi-layer support with drag-and-drop
- Custom text with Impact, Arial, Comic Sans, and more
- Image upload, resize, and positioning
- Undo/Redo functionality (50-step history)
- Export to PNG, JPEG, or GIF

### 🤖 AI-Powered Tools
- **Complete Meme Generation** - Enter a topic and humor style, get a ready-made meme
- **Image Generation** - DALL-E 3 integration for custom imagery
- **Caption Suggestions** - GPT-4 Vision analyzes images and suggests viral captions
- **Viral Score Prediction** - AI predicts potential virality

### 🎬 GIF Creator
- Multi-frame timeline editor
- Add, duplicate, and reorder frames
- Per-frame duration control (100-3000ms)
- Live preview with accurate timing
- Export animated GIFs

### 📊 Trending Content
- Real-time trending memes from Twitter and Reddit
- Viral score algorithm (0-100%)
- Platform filtering and categorization
- One-click template usage

### 📚 Template Library
- Extensive collection of popular meme formats
- Category-based browsing (Reaction, Gaming, Work, etc.)
- Community template submissions
- Voting and ranking system

### 👥 User Management
- Email/password authentication
- OAuth integration (Twitter, Reddit, Google)
- User profiles with statistics
- Storage management
- Multiple plan tiers (Free, Solo, Team, Enterprise)

### 🔔 Notifications
- Real-time notifications for trending content
- Team collaboration alerts
- Template submission updates
- Viral prediction notifications

## 🛠️ Tech Stack

### Frontend
- **Framework**: React 19 with Hooks
- **Routing**: React Router 7
- **Canvas**: Fabric.js 6
- **Styling**: Tailwind CSS 3.4 + shadcn/ui
- **State Management**: Zustand
- **API Client**: Axios
- **Animation**: Framer Motion
- **GIF Export**: gif.js

### Backend
- **Framework**: FastAPI 0.110.1
- **Language**: Python 3.11+
- **Database**: MongoDB 6.0 with Motor (async)
- **Authentication**: JWT + OAuth 2.0
- **AI/ML**: OpenAI API (GPT-4, DALL-E 3)
- **File Storage**: Local file system (S3-ready)

### Infrastructure
- **Frontend Server**: React Development Server (port 3000)
- **Backend Server**: FastAPI with Uvicorn (port 8001)
- **Database**: MongoDB (port 27017)
- **Process Manager**: Supervisord

## 📋 Prerequisites

- Node.js 18+ and Yarn
- Python 3.11+
- MongoDB 6.0+
- OpenAI API key or Emergent LLM key

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/memecraft-pro.git
cd memecraft-pro
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add your configuration
```

**Required Environment Variables:**

```env
# Database
MONGO_URL=mongodb://localhost:27017
DB_NAME=memecraft

# JWT Secret
JWT_SECRET=your-secret-key-here

# OpenAI (or use Emergent LLM key)
OPENAI_API_KEY=your-openai-key
OPENAI_BASE_URL=https://api.openai.com/v1

# OAuth (Optional for testing)
TWITTER_CLIENT_ID=your-twitter-client-id
TWITTER_CLIENT_SECRET=your-twitter-client-secret
REDDIT_CLIENT_ID=your-reddit-client-id
REDDIT_CLIENT_SECRET=your-reddit-client-secret
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Frontend URL
FRONTEND_URL=http://localhost:3000
CORS_ORIGINS=http://localhost:3000
```

**Start Backend Server:**

```bash
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
yarn install

# Configure environment variables
cp .env.example .env
# Edit .env
```

**Required Frontend Environment Variables:**

```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

**Start Frontend Server:**

```bash
yarn start
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs

## 📖 Usage Guide

### Creating Your First Meme

1. **Sign Up / Login**
   - Create an account with email/password
   - Or use OAuth (Twitter, Reddit, Google)

2. **Choose Your Creation Method**
   - **Canvas Editor**: Start from scratch
   - **AI Generator**: Let AI create for you
   - **Templates**: Use popular formats
   - **GIF Creator**: Make animated memes

3. **Edit Your Meme**
   - Add text with custom fonts and colors
   - Upload and position images
   - Apply layers and effects
   - Use undo/redo as needed

4. **Export & Share**
   - Export as PNG, JPEG, or GIF
   - Save to your gallery
   - Share on social media

### Using AI Features

**Generate Complete Meme:**
```
1. Navigate to AI Generator
2. Enter topic: "Monday mornings"
3. Select humor style: "Sarcastic"
4. Click "Generate Meme"
5. Open in editor to customize
```

**Generate Custom Image:**
```
1. Go to AI Generator > Image Only
2. Enter detailed prompt: "A cat wearing sunglasses coding on a laptop, digital art"
3. Wait 30-60 seconds for generation
4. Use in editor
```

### Creating Animated GIFs

```
1. Navigate to GIF Creator
2. Design first frame in canvas
3. Click "Add Frame"
4. Design next frame
5. Adjust frame durations (100-3000ms)
6. Preview with Play button
7. Export GIF
```

## 🔌 API Documentation

### Authentication Endpoints

**Sign Up**
```http
POST /api/auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "meme_master",
  "password": "securepassword123"
}
```

**Login**
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Get Current User**
```http
GET /api/auth/me
Authorization: Bearer <token>
```

### Meme Endpoints

**Create Meme**
```http
POST /api/memes
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "My Awesome Meme",
  "canvas_data": {...},
  "thumbnail_url": "data:image/png;base64,...",
  "tags": ["funny", "relatable"]
}
```

**List User Memes**
```http
GET /api/memes?skip=0&limit=50
Authorization: Bearer <token>
```

**Update Meme**
```http
PUT /api/memes/{meme_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Updated Title",
  "status": "PUBLISHED"
}
```

### AI Endpoints

**Generate Image**
```http
POST /api/ai/generate-image
Authorization: Bearer <token>
Content-Type: application/json

{
  "prompt": "A funny cat meme",
  "width": 1024,
  "height": 1024
}
```

**Suggest Captions**
```http
POST /api/ai/suggest-captions
Authorization: Bearer <token>
Content-Type: application/json

{
  "image_url": "https://example.com/image.jpg",
  "context": "Work-from-home humor"
}
```

**Generate Complete Meme**
```http
POST /api/ai/generate-meme?topic=monday&humor_style=sarcastic
Authorization: Bearer <token>
```

### Trending & Templates

**Get Trending Memes**
```http
GET /api/trends?platform=TWITTER&min_score=70
Authorization: Bearer <token>
```

**List Templates**
```http
GET /api/templates?category=Reaction&limit=20
Authorization: Bearer <token>
```

**Vote on Template**
```http
POST /api/templates/{template_id}/vote?vote=1
Authorization: Bearer <token>
```

For complete API documentation, visit `/docs` endpoint when running the backend server.

## 📁 Project Structure

```
memecraft-pro/
├── backend/                    # FastAPI backend
│   ├── server.py              # Main FastAPI application
│   ├── models.py              # Pydantic models
│   ├── database.py            # MongoDB operations
│   ├── auth.py                # Authentication utilities
│   ├── oauth_handlers.py      # OAuth 2.0 handlers
│   ├── ai_services.py         # AI/ML services
│   ├── trends_service.py      # Trending content service
│   ├── storage.py             # File storage service
│   ├── config.py              # Configuration
│   ├── requirements.txt       # Python dependencies
│   ├── uploads/               # Local file storage
│   └── .env                   # Environment variables
│
├── frontend/                   # React frontend
│   ├── public/
│   │   └── index.html         # HTML template
│   ├── src/
│   │   ├── App.js             # Main app component
│   │   ├── App.css            # Global styles
│   │   ├── index.js           # Entry point
│   │   ├── contexts/          # React contexts
│   │   │   └── AuthContext.js
│   │   ├── pages/             # Page components
│   │   │   ├── Login.js
│   │   │   ├── Signup.js
│   │   │   ├── Dashboard.js
│   │   │   ├── Editor.js
│   │   │   ├── MyMemes.js
│   │   │   ├── Templates.js
│   │   │   ├── AIGenerator.js
│   │   │   ├── GifCreator.js
│   │   │   └── Profile.js
│   │   ├── components/        # Reusable components
│   │   │   ├── ui/           # shadcn/ui components
│   │   │   └── NotificationsPanel.js
│   │   ├── services/          # API services
│   │   │   └── api.js
│   │   ├── lib/               # Utilities
│   │   │   ├── CanvasEditor.js
│   │   │   └── utils.js
│   │   └── .env               # Environment variables
│   ├── package.json           # NPM dependencies
│   ├── tailwind.config.js     # Tailwind configuration
│   └── postcss.config.js      # PostCSS configuration
│
├── tests/                      # Test files
├── scripts/                    # Utility scripts
├── README.md                   # This file
└── .gitignore                 # Git ignore rules
```

## 🎯 Feature Roadmap

### ✅ Completed (Phase 1-3)
- [x] Authentication system (JWT + OAuth)
- [x] Professional canvas editor
- [x] AI meme generation
- [x] Image generation (DALL-E 3)
- [x] Template library
- [x] My Memes gallery
- [x] GIF creator with timeline
- [x] User profiles & settings
- [x] Notifications system
- [x] Trending memes feed

### 🚧 In Progress (Phase 4)
- [ ] Real-time collaboration (WebSockets)
- [ ] Team workspaces
- [ ] Analytics dashboard
- [ ] Social media posting integration

### 📅 Planned (Future)
- [ ] Mobile app (React Native)
- [ ] Video meme support
- [ ] Advanced filters and effects
- [ ] Meme contests and challenges
- [ ] Monetization features
- [ ] API for third-party integrations

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Commit with clear messages**
   ```bash
   git commit -m "Add amazing feature"
   ```
5. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```
6. **Open a Pull Request**

### Code Style Guidelines

**Python (Backend):**
- Follow PEP 8
- Use type hints
- Document functions with docstrings
- Keep functions focused and small

**JavaScript (Frontend):**
- Use ES6+ features
- Functional components with hooks
- PropTypes or TypeScript for type checking
- Follow Airbnb style guide

**Git Commit Messages:**
- Use present tense ("Add feature" not "Added feature")
- Start with capital letter
- Limit first line to 72 characters
- Reference issues and PRs

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v
```

### Frontend Tests

```bash
cd frontend
yarn test
```

### E2E Tests

```bash
yarn test:e2e
```

## 🐛 Troubleshooting

### Common Issues

**Issue: MongoDB Connection Failed**
```bash
# Check if MongoDB is running
sudo systemctl status mongod

# Start MongoDB
sudo systemctl start mongod
```

**Issue: Port Already in Use**
```bash
# Find process using port 8001
lsof -ti:8001

# Kill the process
kill -9 <PID>
```

**Issue: OpenAI API Rate Limit**
- Check your API usage at platform.openai.com
- Consider using caching for repeated requests
- Implement exponential backoff

**Issue: Frontend Not Loading**
```bash
# Clear cache and reinstall
rm -rf node_modules yarn.lock
yarn install
yarn start
```

## 📊 Performance Optimization

### Frontend
- Lazy load routes with React.lazy()
- Optimize images (use WebP format)
- Implement virtual scrolling for long lists
- Use React.memo for expensive components
- Code splitting at route level

### Backend
- Use MongoDB indexes for frequent queries
- Implement Redis caching for trending data
- Use async/await for all I/O operations
- Optimize image processing with thumbnails
- Implement rate limiting

## 🔒 Security Best Practices

- ✅ JWT tokens with short expiration
- ✅ Password hashing with bcrypt
- ✅ HTTPS in production
- ✅ CORS configuration
- ✅ Input validation and sanitization
- ✅ SQL/NoSQL injection prevention
- ✅ XSS protection
- ✅ CSRF tokens
- ✅ Rate limiting on API endpoints
- ✅ Secure file upload validation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Fabric.js** - Canvas manipulation library
- **OpenAI** - AI image and text generation
- **shadcn/ui** - Beautiful component library
- **Tailwind CSS** - Utility-first CSS framework
- **FastAPI** - Modern Python web framework
- **MongoDB** - NoSQL database

## 📞 Support

- **Documentation**: [docs.memecraft.pro](https://docs.memecraft.pro)
- **Issues**: [GitHub Issues](https://github.com/yourusername/memecraft-pro/issues)
- **Email**: support@memecraft.pro
- **Discord**: [Join our community](https://discord.gg/memecraft)
- **Twitter**: [@MemeCraftPro](https://twitter.com/memecraftpro)

## 🌐 Deployment

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Access at http://localhost:3000
```

### Manual Deployment

**Backend (Railway, Heroku, AWS):**
```bash
# Install dependencies
pip install -r requirements.txt

# Run with gunicorn
gunicorn server:app -w 4 -k uvicorn.workers.UvicornWorker
```

**Frontend (Vercel, Netlify):**
```bash
# Build for production
yarn build

# Serve build folder
serve -s build
```

### Environment Variables for Production

```env
# Production settings
NODE_ENV=production
JWT_SECRET=<strong-secret-key>
MONGO_URL=<production-mongodb-url>
OPENAI_API_KEY=<production-api-key>
FRONTEND_URL=https://your-domain.com
```

---

<div align="center">

**Built with ❤️ for the meme community**

[Website](https://memecraft.pro) • [Demo](https://demo.memecraft.pro) • [Documentation](https://docs.memecraft.pro)

⭐ **Star us on GitHub** if you find this useful!

</div>
