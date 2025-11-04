# Yarnsy - Quick Setup Guide

## Prerequisites
- Node.js 16+ and npm
- Python 3.8+

## Quick Start

### 1. Install Dependencies

**Frontend:**
```bash
npm install
```

**Backend:**
```bash
pip install -r requirements.txt
```

### 2. Start Development Servers

**Terminal 1 - Backend (Flask):**
```bash
python app.py
```
Backend runs on: http://localhost:5000

**Terminal 2 - Frontend (React + Vite):**
```bash
npm run dev
```
Frontend runs on: http://localhost:3000

### 3. Open in Browser
Navigate to: http://localhost:3000

## Troubleshooting

### Port Already in Use
If port 5000 or 3000 is taken:
- **Backend**: Edit `app.py` and change `port=5000` to another port
- **Frontend**: Edit `vite.config.js` or use `npm run dev -- --port 3001`

### CORS Issues
If you see CORS errors, ensure:
- Backend is running before frontend
- Flask-CORS is installed (`pip install flask-cors`)

### Module Not Found
- Ensure all dependencies are installed
- Try deleting `node_modules` and `package-lock.json`, then run `npm install` again

## Production Build

```bash
npm run build
```

The built files will be in the `dist` folder.

## Project Structure

```
Yarnsy/
├── src/              # React frontend source
├── public/           # Static assets
├── app.py            # Flask backend
├── requirements.txt  # Python dependencies
└── package.json      # Node dependencies
```

Enjoy crafting! 🧶

