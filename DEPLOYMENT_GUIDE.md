# 🚀 Vercel Deployment Guide for Multimodal Audio Recognition

## **Prerequisites**
1. GitHub account with your repo pushed
2. Vercel account (free tier works)
3. PostgreSQL database (Vercel Postgres or any cloud provider)

---

## **Database Setup (Choose ONE Option)**

### **Option A: Vercel Postgres (Recommended - Easiest)**

1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Create a new project → Connect Git repo
3. Click **Storage** → **Create Database** → **Postgres**
4. Copy the `DATABASE_URL` connection string
5. This will be automatically added to your Vercel environment

### **Option B: Neon (Free Tier - Good)**
1. Visit [neon.tech](https://neon.tech)
2. Sign up → Create a new project
3. Copy the connection string
4. You'll add this to Vercel env vars later

### **Option C: Supabase (Free Tier)**
1. Visit [supabase.com](https://supabase.com)
2. Create project → PostgreSQL
3. Go to Settings → Database → Connection String
4. Copy the string

---

## **Local Testing Before Deployment**

### **Step 1: Install PostgreSQL Locally (Optional - for testing)**

If you want to test with PostgreSQL:
```bash
# Windows with chocolatey
choco install postgresql

# Or download from postgresql.org
```

### **Step 2: Create Local PostgreSQL Connection String**

Create `.env.local` in your backend folder:
```
DATABASE_URL=postgresql://username:password@localhost:5432/multimodal_audio_db
```

### **Step 3: Update Backend to Use PostgreSQL**

Install PostgreSQL driver:
```bash
cd backend
pip install psycopg2-binary sqlalchemy
pip freeze > requirements.txt
```

Create `backend/models/database_postgres.py`:
```python
"""PostgreSQL adapter for production"""
import os
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize PostgreSQL tables"""
    with engine.connect() as conn:
        # Create tables similar to SQLite version
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # ... add other table creation statements
        conn.commit()
```

Or update `backend/models/database.py` to handle PostgreSQL:

```python
import os
import psycopg2 as db_module

DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    # PostgreSQL for production
    import psycopg2
    conn = psycopg2.connect(DATABASE_URL)
else:
    # SQLite for local development
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
```

---

## **Backend Requirements Update**

Update `backend_requirements.txt`:

```
Flask==2.3.2
Flask-CORS==4.0.0
Flask-SQLAlchemy==3.0.0
psycopg2-binary==2.9.6
python-dotenv==1.0.0
torch==2.0.0
torchvision==0.15.1
torchaudio==2.0.1
librosa==0.10.0
numpy==1.23.5
python-multipart==0.0.6
joblib==1.2.0
h5py==3.11.0
scikit-learn==1.6.1
fer==22.4.3
opencv-python==4.7.0.72
Pillow==9.5.0
gunicorn==21.2.0
```

---

## **Frontend Configuration**

Update `frontend/src/services/api.js` to use production URL:

```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});
```

---

## **Deployment Steps**

### **Step 1: Push Code to GitHub**

```bash
git add .
git commit -m "feat: prepare for Vercel deployment with PostgreSQL"
git push origin main
```

### **Step 2: Deploy Frontend + Backend**

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your GitHub repository
3. Configure project:
   - **Project Name**: multimodal-audio-recognition
   - **Root Directory**: (leave as /)
   - **Framework Preset**: Other (Manual)

4. Add **Environment Variables**:
   - `DATABASE_URL`: Your PostgreSQL connection string
   - `FLASK_ENV`: production
   - `FLASK_DEBUG`: 0

5. Click **Deploy**

### **Step 3: Configure Production Domain**

After deployment:
1. Your app has a `.vercel.app` URL
2. Update Frontend API calls to use production URL:
   ```
   REACT_APP_API_URL=https://your-app.vercel.app/api
   ```

3. Re-deploy frontend with new env var

---

## **File Upload Storage (Important)**

SQLite uses local filesystem for uploads. For production, migrate to:

- **AWS S3** (for file storage)
- **Vercel Blob** (limited but free)
- **Supabase Storage**

Update `backend/app.py`:

```python
# Use environment variable for upload folder
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/tmp/uploads')

# For S3 upload handling
import boto3
s3_client = boto3.client('s3', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                         aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))
```

---

## **Troubleshooting**

| Issue | Solution |
|-------|----------|
| `DATABASE_URL not found` | Add to Vercel env vars in dashboard |
| `Models fail to load` | Ensure saved_model/ folder is in repo |
| 413 Payload Too Large | Increase `maxDuration` in vercel.json |
| Uploads disappear | Use cloud storage (S3/Blob) instead of local /tmp |
| PostgreSQL connection fails | Check connection string format |

---

## **Production Monitoring**

- Check logs: `vercel logs <deployment-url>`
- View dashboard: [vercel.com/dashboard](https://vercel.com/dashboard)
- Health check: `https://your-app.vercel.app/health`

---

## **Next Steps**

1. ✅ Choose a PostgreSQL provider
2. ✅ Get connection string
3. ✅ Update backend database code
4. ✅ Push to GitHub
5. ✅ Deploy via Vercel dashboard
6. ✅ Add environment variables
7. ✅ Test health endpoint
8. ✅ Configure file storage (S3/Blob)

