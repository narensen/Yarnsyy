# 🚀 How to Run Yarnsy

## Step-by-Step Instructions

### **Step 1: Install Dependencies**

**First, install Node.js dependencies (frontend):**
```bash
npm install
```

**Then, install Python dependencies (backend):**
```bash
pip install -r requirements.txt
```

> **Note:** On Windows, if `pip` doesn't work, try `pip3` or `python -m pip install -r requirements.txt`

---

### **Step 2: Start the Backend Server**

Open a **Terminal/Command Prompt** window and run:

```bash
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
```

**✅ Backend is now running on http://localhost:5000**

> **Keep this terminal open!** The backend needs to stay running.

---

### **Step 3: Start the Frontend Server**

Open a **NEW Terminal/Command Prompt** window and run:

```bash
npm run dev
```

You should see:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
```

**✅ Frontend is now running on http://localhost:3000**

---

### **Step 4: Open in Browser**

Open your web browser and navigate to:

**http://localhost:3000**

🎉 **Your Yarnsy website should now be running!**

---

## 📋 Quick Reference

### Terminal Commands Summary:

**Terminal 1 (Backend):**
```bash
cd D:\Yarnsy
python app.py
```

**Terminal 2 (Frontend):**
```bash
cd D:\Yarnsy
npm run dev
```

**Browser:**
```
http://localhost:3000
```

---

## ⚠️ Common Issues & Solutions

### **Issue: "python: command not found"**
- **Windows:** Try `py app.py` or `python3 app.py`
- **Mac/Linux:** Try `python3 app.py`

### **Issue: "npm: command not found"**
- Make sure Node.js is installed: https://nodejs.org/
- Restart your terminal after installing Node.js

### **Issue: Port 5000 or 3000 already in use**
- **Port 5000 (Backend):** 
  - Close any other apps using port 5000
  - Or edit `app.py` line: `app.run(debug=True, port=5001)`
  
- **Port 3000 (Frontend):**
  - Vite will automatically try the next port (3001, 3002, etc.)
  - Or use: `npm run dev -- --port 3001`

### **Issue: "Module not found" errors**
- Make sure you ran `npm install` and `pip install -r requirements.txt`
- Try deleting `node_modules` folder and running `npm install` again

### **Issue: CORS errors in browser console**
- Make sure the backend (port 5000) is running BEFORE starting the frontend
- Check that `flask-cors` is installed: `pip install flask-cors`

---

## 🛑 Stopping the Servers

To stop the servers:
- **Terminal 1 (Backend):** Press `Ctrl + C`
- **Terminal 2 (Frontend):** Press `Ctrl + C`

---

## 📦 Alternative: Using Python Virtual Environment (Recommended)

If you want to isolate Python dependencies:

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run backend
python app.py
```

---

## ✨ You're All Set!

Once both servers are running:
- ✅ Backend: http://localhost:5000
- ✅ Frontend: http://localhost:3000

Browse to http://localhost:3000 and start exploring Yarnsy! 🧶

