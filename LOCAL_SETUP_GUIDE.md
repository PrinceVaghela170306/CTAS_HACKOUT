# 🚀 Local Setup Guide - Coastal Monitor

*Quick reference for running the project locally in VS Code*

## Prerequisites

- **VS Code** installed
- **Node.js 18+** installed
- **Python 3.8+** installed
- **Git** installed

## 🔧 Quick Setup Steps

### 1. Clone & Open Project
```bash
git clone <your-repo-url>
cd HACKOUT
code .
```

### 2. Backend Setup (Terminal 1)
```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your Supabase credentials

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
**Backend will run on:** `http://localhost:8000`

### 3. Frontend Setup (Terminal 2)
```bash
# Navigate to frontend (new terminal)
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local
# Edit .env.local with your configuration

# Start frontend server
npm run dev
```
**Frontend will run on:** `http://localhost:3001`

## 🌐 Access Points

- **Main App**: http://localhost:3001
- **Dashboard**: http://localhost:3001/dashboard
- **API Docs**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/health

## 📝 Environment Variables

### Backend (.env)
```env
SUPABASE_URL=your-supabase-project-url
SUPABASE_KEY=your-supabase-service-role-key
SUPABASE_JWT_SECRET=your-supabase-jwt-secret
SECRET_KEY=your-secret-key-for-jwt
DEBUG=True
CORS_ORIGINS=http://localhost:3001,http://localhost:3000
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=your-supabase-project-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
```

## 🛠️ VS Code Extensions (Recommended)

- **Python** - Python language support
- **Pylance** - Python IntelliSense
- **ES7+ React/Redux/React-Native snippets** - React snippets
- **Tailwind CSS IntelliSense** - Tailwind autocomplete
- **Thunder Client** - API testing (alternative to Postman)

## 🔍 Quick Commands

### Backend Commands
```bash
# Activate virtual environment
venv\Scripts\activate

# Install new package
pip install package-name
pip freeze > requirements.txt

# Run tests
pytest

# Format code
black app/
```

### Frontend Commands
```bash
# Install new package
npm install package-name

# Build for production
npm run build

# Run linting
npm run lint
```

## 🚨 Troubleshooting

### Backend Issues
- **Port 8000 in use**: Change port in uvicorn command
- **Module not found**: Ensure virtual environment is activated
- **Database errors**: Check Supabase credentials in .env

### Frontend Issues
- **Port 3001 in use**: Next.js will auto-assign next available port
- **Build errors**: Check TypeScript errors with `npm run type-check`
- **API connection**: Verify backend is running on port 8000

### Common Fixes
```bash
# Clear Next.js cache
rm -rf .next

# Reinstall node modules
rm -rf node_modules package-lock.json
npm install

# Restart both servers
# Ctrl+C to stop, then restart with above commands
```

## 📱 Testing the App

1. **Backend Health Check**: Visit `http://localhost:8000/health`
2. **Frontend Load**: Visit `http://localhost:3001`
3. **Login**: Use Supabase auth or create test account
4. **Dashboard**: Navigate to `http://localhost:3001/dashboard`

## 🔄 Development Workflow

1. **Start both servers** (backend + frontend)
2. **Make changes** in VS Code
3. **Auto-reload** will refresh both servers
4. **Test changes** in browser
5. **Commit changes** when ready

---

**Quick Start Summary:**
1. `cd backend && venv\Scripts\activate && pip install -r requirements.txt`
2. `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
3. `cd frontend && npm install && npm run dev`
4. Open `http://localhost:3001`

*Happy coding! 🌊*