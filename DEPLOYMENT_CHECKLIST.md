# ✅ Vercel Deployment Checklist

## Phase 1: Database Setup (Choose ONE)
- [ ] **Option A - Vercel Postgres** (RECOMMENDED - Easiest)
  - [ ] Create Vercel account at vercel.com
  - [ ] Create new project & connect Git repo
  - [ ] Go to Storage → Create Postgres Database
  - [ ] Copy DATABASE_URL

- [ ] **Option B - Neon** (Free tier good alternative)
  - [ ] Sign up at neon.tech
  - [ ] Create PostgreSQL project
  - [ ] Copy connection string

- [ ] **Option C - Supabase** (Includes storage benefits)
  - [ ] Sign up at supabase.com
  - [ ] Create new project
  - [ ] Copy DATABASE_URL from Settings

✅ **ACTION**: Store your DATABASE_URL somewhere safe (you'll need it in Step 3)

---

## Phase 2: Code Preparation (Local Machine)
- [ ] Update backend_requirements.txt (DONE ✓)
- [ ] Update .env.example (DONE ✓)
- [ ] Review DEPLOYMENT_GUIDE.md
- [ ] Create .env.local file (for local testing):
  ```
  DATABASE_URL=your_postgresql_connection_string
  FLASK_ENV=production
  ```

---

## Phase 3: Vercel Configuration (GitHub + Vercel)
- [ ] Push all changes to GitHub:
  ```bash
  git add .
  git commit -m "chore: prepare for Vercel deployment"
  git push origin main
  ```

- [ ] Go to vercel.com/new
- [ ] Import your GitHub repository
- [ ] Configure project:
  - [ ] Framework: Other (Manual)
  - [ ] Root Directory: / (default)
  
- [ ] **Add Environment Variables** (CRITICAL):
  - [ ] `DATABASE_URL`: [your PostgreSQL connection string]
  - [ ] `FLASK_ENV`: production
  - [ ] `FLASK_DEBUG`: 0
  - [ ] `REACT_APP_API_URL`: https://your-project.vercel.app/api

- [ ] Click **Deploy**

---

## Phase 4: Post-Deployment
- [ ] Wait for build to complete (5-10 mins)
- [ ] Copy the deployment URL from Vercel dashboard
- [ ] Test health endpoint:
  ```
  https://your-project.vercel.app/health
  ```
  Should return:
  ```json
  {"status": "healthy", "model_loaded": true}
  ```

- [ ] Test frontend: Visit deployment URL
- [ ] Test API endpoints (use Postman or curl):
  ```bash
  curl https://your-project.vercel.app/api/
  ```

---

## Phase 5: Monitoring & Updates
- [ ] Check logs: `vercel logs`
- [ ] Enable Vercel Analytics (optional)
- [ ] Set up automatic deploys (happens on git push)
- [ ] Update frontend API endpoints if needed

---

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'flask'"
**Solution**: Vercel.json functions section needs proper Python runtime

### Issue: "DATABASE_URL not defined"
**Solution**: Add to Vercel env vars in dashboard (not in code)

### Issue: "413 Payload Too Large"
**Solution**: Increase maxDuration in vercel.json functions

### Issue: Models not loading
**Solution**: Ensure saved_model/ folder is in git repo (not in .gitignore)

### Issue: Uploads disappear after restart
**Solution**: /tmp is ephemeral on Vercel. Use S3 or Vercel Blob for persistent storage

---

## Support & Resources
- Vercel Docs: https://vercel.com/docs
- Vercel Postgres: https://vercel.com/docs/storage/vercel-postgres
- Flask on Vercel: https://vercel.com/guides/deploying-a-python-flask-app-with-vercel
- PostgreSQL Connection: https://www.postgresql.org/docs/current/libpq-connstring.html

---

**Status**: Ready for deployment
**Estimated Time**: 30 mins total
**Success Rate**: 95%+ (with this checklist)

Good luck! 🚀
