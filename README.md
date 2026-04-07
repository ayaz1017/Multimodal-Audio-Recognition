# Multimodal Audio Recognition 🎵

A complete, production-ready AI system for multimodal audio recognition using video signals and facial expressions. Built with React frontend, Flask API backend, and PyTorch deep learning model.

## ✨ Features

### 🎤 Audio Recognition
- Extract MFCC features from audio files
- Analyze spectral characteristics
- Get model predictions with confidence scores
- Support for multiple audio formats (WAV, MP3, M4A, OGG)

### 📹 Video Facial Recognition
- Detect emotions from video frames
- Analyze facial expressions over time
- Generate emotion statistics
- Support for multiple video formats (MP4, AVI, MOV, MKV)

### 🔗 Multimodal Recognition
- Combined audio and video analysis
- Correlate audio predictions with detected emotions
- Get comprehensive multi-modal results
- Best accuracy with combined analysis

## 🏗️ Project Structure

```
Multimodal-Audio-Recognition/
├── backend/                          # Flask API server
│   ├── app.py                       # Main Flask application
│   ├── models/
│   │   └── audio_model.py           # Model loading & inference
│   ├── routes/
│   │   └── api.py                   # API endpoints
│   ├── utils/
│   │   ├── audio_processor.py       # Audio feature extraction
│   │   └── video_processor.py       # Video & emotion detection
│   └── uploads/                     # Temporary file storage
├── frontend/                         # React frontend
│   ├── public/
│   ├── src/
│   │   ├── components/              # Reusable React components
│   │   ├── pages/                   # Page components
│   │   ├── services/
│   │   │   └── api.js               # API client
│   │   ├── App.js
│   │   └── index.js
│   └── package.json
├── saved_model/
│   └── audio_model.pt               # Pre-trained PyTorch model
├── backend_requirements.txt
├── SETUP_GUIDE.md                   # Installation guide
├── DOCS.md                          # Detailed documentation
├── setup.sh                         # Linux/macOS setup script
├── setup.bat                        # Windows setup script
└── LICENSE
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+
- Your trained model at `saved_model/audio_model.pt`

### Windows
```bash
setup.bat
```

### macOS/Linux
```bash
chmod +x setup.sh
./setup.sh
```

### Manual Setup

**Backend:**
```bash
pip install -r backend_requirements.txt
python backend/app.py
```
Backend runs on `http://localhost:5000`

**Frontend:**
```bash
cd frontend
npm install
npm start
```
Frontend opens at `http://localhost:3000`

## 📚 API Endpoints

### POST `/api/recognize_audio`
Analyze audio file and get predictions
- **Input:** Audio file (WAV, MP3, M4A, OGG)
- **Output:** Features + Model predictions

### POST `/api/recognize_video`
Detect facial expressions from video
- **Input:** Video file (MP4, AVI, MOV, MKV)
- **Output:** Emotion detection + statistics

### POST `/api/recognize_multimodal`
Combined audio + video analysis
- **Input:** Video file with audio
- **Output:** Comprehensive multi-modal results

### GET `/health`
Check API status

## 🎨 Frontend Pages

- **Home** - Project overview and navigation
- **Audio** - Upload and analyze audio files
- **Video** - Detect facial expressions
- **Multimodal** - Combined analysis

## 🛠️ Tech Stack

**Backend:** Flask, PyTorch, Librosa, OpenCV, FER

**Frontend:** React, Router, Axios, React Icons

## 📖 Documentation

- **Setup:** See [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **Details:** See [DOCS.md](DOCS.md)

## 📄 License

See [LICENSE](LICENSE) for details.