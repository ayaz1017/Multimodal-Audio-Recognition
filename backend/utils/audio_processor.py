import librosa
import numpy as np
import torch
from pathlib import Path

class AudioProcessor:
    """Process audio files and extract features"""
    
    def __init__(self, sr=22050, n_mfcc=13, n_fft=2048, hop_length=512):
        self.sr = sr  # Sample rate
        self.n_mfcc = n_mfcc  # Number of MFCCs
        self.n_fft = n_fft  # FFT window size
        self.hop_length = hop_length  # Hop length for STFT
    
    def load_audio(self, file_path, duration=None):
        """
        Load audio file
        Args:
            file_path: path to audio file
            duration: duration in seconds (optional)
        Returns:
            audio signal and sample rate
        """
        try:
            y, sr = librosa.load(file_path, sr=self.sr, duration=duration)
            return y, sr
        except Exception as e:
            raise Exception(f"Error loading audio: {str(e)}")
    
    def extract_mfcc(self, audio):
        """Extract MFCC features"""
        mfcc = librosa.feature.mfcc(y=audio, sr=self.sr, n_mfcc=self.n_mfcc, n_fft=self.n_fft)
        mfcc = np.mean(mfcc.T, axis=0)
        return mfcc
    
    def extract_spectral_features(self, audio):
        """Extract spectral features"""
        # Zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(audio)[0]
        zcr_mean = np.mean(zcr)
        
        # Spectral centroid
        spec_cent = librosa.feature.spectral_centroid(y=audio, sr=self.sr)[0]
        spec_cent_mean = np.mean(spec_cent)
        
        # Spectral rolloff
        spec_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=self.sr)[0]
        spec_rolloff_mean = np.mean(spec_rolloff)
        
        return np.array([zcr_mean, spec_cent_mean, spec_rolloff_mean])
    
    def extract_temporal_features(self, audio):
        """Extract temporal features"""
        # Energy
        energy = np.sum(audio ** 2)
        
        # RMS energy
        rms = librosa.feature.rms(y=audio)[0]
        rms_mean = np.mean(rms)
        
        return np.array([energy, rms_mean])
    
    def extract_all_features(self, file_path):
        """Extract all features from audio file"""
        try:
            # Load audio
            audio, sr = self.load_audio(file_path)
            
            # Extract different types of features
            mfcc = self.extract_mfcc(audio)
            spectral = self.extract_spectral_features(audio)
            temporal = self.extract_temporal_features(audio)
            
            # Combine all features
            features = np.concatenate([mfcc, spectral, temporal])
            
            return {
                'mfcc': mfcc,
                'spectral': spectral,
                'temporal': temporal,
                'all_features': features,
                'sample_rate': sr,
                'duration': len(audio) / sr
            }
        except Exception as e:
            raise Exception(f"Error extracting features: {str(e)}")

    def _infer_spectrogram_shape(self, feature_count, preferred_n_mels=None):
        if preferred_n_mels is None:
            preferred_n_mels = [128, 96, 80, 64, 48, 40, 32, 24]

        for n_mels in preferred_n_mels:
            if feature_count % n_mels == 0:
                time_steps = feature_count // n_mels
                if time_steps >= 32:
                    return n_mels, time_steps

        side = int(np.sqrt(feature_count))
        for n_mels in range(side, 0, -1):
            if feature_count % n_mels == 0:
                return n_mels, feature_count // n_mels

        return 96, 319

    def _extract_model_spectrogram(self, file_path, expected_feature_count, scaler=None, n_mels_hint=None):
        audio, _ = self.load_audio(file_path)
        if len(audio) == 0:
            raise Exception("Audio file is empty")

        n_mels, time_steps = self._infer_spectrogram_shape(
            expected_feature_count,
            preferred_n_mels=[n_mels_hint] + [128, 96, 80, 64, 48, 40, 32, 24]
            if n_mels_hint
            else None,
        )

        mel = librosa.feature.melspectrogram(
            y=audio,
            sr=self.sr,
            n_fft=self.n_fft,
            hop_length=self.hop_length,
            n_mels=n_mels,
        )
        log_mel = librosa.power_to_db(mel, ref=np.max)

        if log_mel.shape[1] < time_steps:
            pad_width = time_steps - log_mel.shape[1]
            log_mel = np.pad(log_mel, ((0, 0), (0, pad_width)), mode='constant')
        else:
            log_mel = log_mel[:, :time_steps]

        flat_features = log_mel.reshape(1, -1).astype(np.float32)

        if scaler is not None and hasattr(scaler, 'transform'):
            flat_features = scaler.transform(flat_features)

        model_features = flat_features.reshape(1, n_mels, time_steps).astype(np.float32)
        return torch.from_numpy(model_features)
    
    def process_for_model(self, file_path, expected_feature_count=None, scaler=None, n_mels=None):
        """Process audio for model prediction"""
        try:
            if expected_feature_count is not None:
                return self._extract_model_spectrogram(
                    file_path=file_path,
                    expected_feature_count=int(expected_feature_count),
                    scaler=scaler,
                    n_mels_hint=n_mels,
                )

            features = self.extract_all_features(file_path)
            # Ensure we have proper shape for model input
            feature_array = features['all_features']
            # Reshape to match model input: (batch_size, features)
            if len(feature_array.shape) == 1:
                feature_array = feature_array.reshape(1, -1)
            return torch.FloatTensor(feature_array)
        except Exception as e:
            raise Exception(f"Error processing audio for model: {str(e)}")

def process_audio_file(file_path, sr=22050):
    """Utility function to process audio file"""
    processor = AudioProcessor(sr=sr)
    return processor.extract_all_features(file_path)
