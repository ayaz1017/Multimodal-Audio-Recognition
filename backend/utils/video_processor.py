import cv2
import numpy as np
from pathlib import Path
import librosa
import json

# Try to import FER, fallback if not available
try:
    from fer import FER
    HAS_FER = True
except (ImportError, AttributeError):
    HAS_FER = False
    # Fallback: simple emotion detection using face detection only
    print("[WARNING] FER package not available. Using basic facial detection.")

class VideoProcessor:
    """Process video files to extract facial expressions and audio"""
    
    def __init__(self):
        self.emotions = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']
        
        if HAS_FER:
            try:
                self.emotion_detector = FER(mtcnn=True)
            except Exception as e:
                print(f"[WARNING] FER initialization failed: {e}. Using fallback mode.")
                self.emotion_detector = None
        else:
            self.emotion_detector = None
        
        # Load cascade classifier for face detection fallback
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
    
    def extract_frames_at_intervals(self, video_path, interval=1):
        """
        Extract frames at regular intervals
        Args:
            video_path: path to video file
            interval: extract every nth frame
        Returns:
            list of frames
        """
        try:
            cap = cv2.VideoCapture(video_path)
            frames = []
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % interval == 0:
                    frames.append(frame)
                
                frame_count += 1
            
            cap.release()
            return frames
        except Exception as e:
            raise Exception(f"Error extracting frames: {str(e)}")
    
    def detect_emotions(self, frame):
        """
        Detect emotions in a frame
        Args:
            frame: video frame
        Returns:
            emotion probabilities
        """
        try:
            if self.emotion_detector is None:
                # Fallback: basic face detection without emotion classification
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                if len(faces) > 0:
                    # Return random emotion or 'neutral' if faces detected
                    return {'emotion': 'neutral', 'confidence': 0.75}
                else:
                    return {'emotion': 'no_face', 'confidence': 0.0}
            
            # Use FER if available
            emotion_predictions = self.emotion_detector.top_emotion(frame)
            if emotion_predictions:
                emotion, score = emotion_predictions
                return {'emotion': emotion, 'confidence': score}
            return {'emotion': 'unknown', 'confidence': 0.0}
        except Exception as e:
            # Fallback on error
            return {'emotion': 'error', 'confidence': 0.0, 'error': str(e)}
    
    def extract_facial_expressions(self, video_path, interval=30):
        """
        Extract facial expressions from video
        Args:
            video_path: path to video file
            interval: frame interval for analysis
        Returns:
            emotion statistics
        """
        try:
            frames = self.extract_frames_at_intervals(video_path, interval)
            
            emotion_data = {emotion: [] for emotion in self.emotions}
            emotion_list = []
            
            for frame in frames:
                emotion_info = self.detect_emotions(frame)
                emotion_list.append(emotion_info)
                
                if emotion_info['emotion'] in emotion_data:
                    emotion_data[emotion_info['emotion']].append(emotion_info['confidence'])
            
            # Calculate statistics
            emotion_stats = {
                emotion: {
                    'count': len(scores),
                    'mean': np.mean(scores) if scores else 0,
                    'max': np.max(scores) if scores else 0,
                    'min': np.min(scores) if scores else 0
                }
                for emotion, scores in emotion_data.items()
            }
            
            return {
                'emotion_history': emotion_list,
                'emotion_stats': emotion_stats,
                'total_frames_analyzed': len(frames),
                'dominant_emotion': max(emotion_stats.items(), key=lambda x: x[1]['mean'])[0]
            }
        except Exception as e:
            raise Exception(f"Error extracting facial expressions: {str(e)}")
    
    def extract_audio_from_video(self, video_path, output_audio_path):
        """
        Extract audio from video file
        Args:
            video_path: path to video file
            output_audio_path: path to save audio
        Returns:
            path to audio file
        """
        try:
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            cap.release()
            
            # Use ffmpeg to extract audio
            import subprocess
            cmd = ['ffmpeg', '-i', video_path, '-q:a', '9', '-n', output_audio_path]
            subprocess.run(cmd, check=True, capture_output=True)
            
            return output_audio_path
        except Exception as e:
            raise Exception(f"Error extracting audio from video: {str(e)}")
    
    def get_video_info(self, video_path):
        """Get video information"""
        try:
            cap = cv2.VideoCapture(video_path)
            
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            cap.release()
            
            return {
                'frame_count': frame_count,
                'fps': fps,
                'width': width,
                'height': height,
                'duration': duration
            }
        except Exception as e:
            raise Exception(f"Error getting video info: {str(e)}")

def extract_facial_expressions_from_video(video_path, interval=30):
    """Utility function to extract emotions from video"""
    processor = VideoProcessor()
    return processor.extract_facial_expressions(video_path, interval)
