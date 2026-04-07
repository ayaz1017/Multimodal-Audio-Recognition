# Multimodal Audio Recognition - Detailed Documentation

## 🎯 Project Overview

This is a complete multimodal audio recognition system that combines three powerful AI capabilities:

1. **Audio Recognition** - Analyzes audio files using your trained PyTorch model
2. **Video Facial Recognition** - Detects emotions and facial expressions from video
3. **Multimodal Analysis** - Combines both audio and video analysis for comprehensive results

## 🏗️ Architecture

```
Frontend (React)          Backend (Flask)           Models
    ↓                          ↓                       ↓
  Port 3000              Port 5000          [Trained Audio Model]
                              ↓
                        [Audio Processor]
                        [Video Processor]
                        [Model Inference]
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+
- GPU (optional, but recommended for faster processing)

### Windows Users
```bash
setup.bat
```

### macOS/Linux Users
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

**Frontend:**
```bash
cd frontend
npm install
npm start
```

## 📋 API Documentation

### 1. Audio Recognition

**Endpoint:** `POST /api/recognize_audio`

**Request:**
```
Content-Type: multipart/form-data
file: <audio_file>
```

**Response:**
```json
{
  "success": true,
  "audio_features": {
    "mfcc": [...],
    "spectral": [...],
    "temporal": [...],
    "duration": 10.5,
    "sample_rate": 22050
  },
  "predictions": {
    "prediction": 1,
    "probability": 0.95
  }
}
```

**Supported Formats:** WAV, MP3, M4A, OGG, FLAC

### 2. Video Recognition

**Endpoint:** `POST /api/recognize_video`

**Request:**
```
Content-Type: multipart/form-data
file: <video_file>
```

**Response:**
```json
{
  "success": true,
  "video_info": {
    "frame_count": 1500,
    "fps": 30,
    "width": 1920,
    "height": 1080,
    "duration": 50.0
  },
  "facial_expressions": {
    "emotion_history": [...],
    "emotion_stats": {...},
    "total_frames_analyzed": 50,
    "dominant_emotion": "happy"
  }
}
```

**Supported Formats:** MP4, AVI, MOV, MKV, WEBM

### 3. Multimodal Recognition

**Endpoint:** `POST /api/recognize_multimodal`

**Request:**
```
Content-Type: multipart/form-data
file: <video_file>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "audio": {...},
    "video": {...},
    "combined_analysis": {
      "dominant_emotion": "happy",
      "audio_prediction_confidence": 0.95,
      "recommendation": "Use combined results for better accuracy"
    }
  }
}
```

## 🎨 Frontend Features

### Pages

1. **Home Page**
   - Project overview
   - Feature introduction
   - How it works guide

2. **Audio Recognition Page**
   - Drag-and-drop file upload
   - Real-time processing
   - Feature visualization
   - Model predictions

3. **Video Recognition Page**
   - Video upload
   - Facial expression analysis
   - Emotion timeline
   - Statistics display

4. **Multimodal Page**
   - Combined analysis
   - Correlation between audio and facial expressions
   - Comprehensive results

### Components

- **Header:** Navigation and API status indicator
- **Footer:** Links and information
- **FileUpload:** Drag-and-drop file upload component
- **ResultsDisplay:** JSON results viewer
- **Status Indicator:** Real-time backend connectivity

## 🔧 Backend Components

### Audio Processor (`audio_processor.py`)

Features extracted:
- **MFCC** (Mel-Frequency Cepstral Coefficients) - 13 features
- **Spectral Features** - Zero Crossing Rate, Spectral Centroid, Spectral Rolloff
- **Temporal Features** - Energy, RMS Energy

### Video Processor (`video_processor.py`)

Capabilities:
- Frame extraction at intervals
- Emotion detection using FER library
- Audio extraction from video
- Video information retrieval
- Emotion statistics calculation

### Model Loader (`audio_model.py`)

- Loads PyTorch model
- Handles CUDA/CPU detection
- Provides inference interface
- Returns predictions and probabilities

## 📁 File Upload

- **Maximum File Size:** 50MB
- **Upload Folder:** `backend/uploads/` (temporary)
- **Files are cleaned up** after processing

## ⚙️ Configuration

### Backend Configuration (`backend/app.py`)

```python
UPLOAD_FOLDER = 'backend/uploads'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'mp4', 'avi', 'mov', 'jpg', 'jpeg', 'png'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
```

### CORS Settings

CORS is enabled for development:
```python
CORS(app)
```

### Environment Variables

Create `.env` file (optional):
```
FLASK_ENV=development
API_PORT=5000
```

## 🐛 Troubleshooting

### Backend Won't Start
```
Error: Model not found at saved_model/audio_model.pt
```
**Solution:** Place your trained model at the specified path

### Frontend Can't Connect to Backend
```
Error: Network Error - Cannot reach API
```
**Solution:** 
- Ensure backend is running on port 5000
- Check firewall settings
- Verify CORS is enabled

### Model Loading Fails
```
Error: Failed to load model
```
**Solution:**
- Verify model file format (should be .pt for PyTorch)
- Check PyTorch version compatibility
- Ensure model was saved with `torch.save()`

### CUDA/GPU Issues
```
Error: CUDA out of memory
```
**Solution:**
- Model will automatically fallback to CPU
- Reduce batch size if applicable
- Clear GPU memory before processing

## 📊 Performance Tips

1. **Audio Processing:** Typically 5-15 seconds per file
2. **Video Processing:** 10-30 seconds per file (depends on duration and resolution)
3. **Multimodal:** 20-60 seconds for combined analysis

To improve performance:
- Use GPU if available
- Process shorter files first
- Optimize feature extraction settings
- Use video compression

## 🚀 Production Deployment

### Before Deploying

1. Set `FLASK_ENV=production` in `.env`
2. Set `debug=False` in Flask app
3. Use a production WSGI server (Gunicorn, uWSGI)
4. Implement authentication
5. Use environment variables for sensitive data
6. Add rate limiting
7. Implement logging

### Deploy Backend
```bash
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
```

### Deploy Frontend
```bash
npm run build
# Deploy build/ folder to Vercel, Netlify, or your hosting
```

## 🔐 Security Considerations

- File upload validation (size and type)
- CORS configuration for production
- Input sanitization
- Model file integrity
- API rate limiting (recommended)
- Authentication (recommended for production)

## 📚 Dependencies

### Backend
- Flask 2.3.2
- PyTorch 2.0.0
- Librosa 0.10.0
- OpenCV 4.7.0
- FER 22.4.3

### Frontend
- React 18.2.0
- React Router 6.8.0
- Axios 1.3.0
- React Icons 4.7.1

## 📈 Future Enhancements

- [ ] WebSocket for real-time streaming
- [ ] Batch processing API
- [ ] Results database/storage
- [ ] User authentication
- [ ] Advanced analytics dashboard
- [ ] Model versioning
- [ ] A/B testing framework
- [ ] Performance metrics
- [ ] Export results to PDF/CSV

## 📄 License

See LICENSE file for details.

## 💬 Support

For issues:
1. Check logs in browser console (frontend)
2. Check Flask output (backend)
3. Verify file paths and permissions
4. Ensure all dependencies are installed
5. Check API connectivity
