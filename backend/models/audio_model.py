import os
from collections import OrderedDict

import h5py
import joblib
import numpy as np
import torch
import torch.nn as nn

MODEL_DIR = os.path.join(os.path.dirname(__file__), '../../saved_model')
MODEL_CANDIDATES = [
    os.path.join(MODEL_DIR, 'audio_model.h5'),
    os.path.join(MODEL_DIR, 'audio_model_full.h5'),
    os.path.join(MODEL_DIR, 'audio_model.pt'),
]
SCALER_PATH = os.path.join(MODEL_DIR, 'scaler.pkl')
LABEL_ENCODER_PATH = os.path.join(MODEL_DIR, 'label_encoder.pkl')


class TemporalAttention(nn.Module):
    """Temporal attention over BiLSTM outputs."""

    def __init__(self, input_dim=512):
        super(TemporalAttention, self).__init__()
        self.attn = nn.Linear(input_dim, 1)

    def forward(self, lstm_out):
        scores = self.attn(lstm_out).squeeze(-1)
        weights = torch.softmax(scores, dim=1)
        return torch.sum(lstm_out * weights.unsqueeze(-1), dim=1)


class AudioModelCNNLSTM(nn.Module):
    """Architecture that matches the saved model weights in saved_model/."""

    def __init__(self, input_channels=1, num_emotions=6):
        super(AudioModelCNNLSTM, self).__init__()

        self.cnn = nn.Sequential(
            nn.Conv2d(input_channels, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Dropout2d(0.3),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Dropout2d(0.3),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )

        self.lstm = nn.LSTM(
            input_size=128,
            hidden_size=256,
            num_layers=2,
            bidirectional=True,
            batch_first=True,
            dropout=0.3,
        )
        self.attention = TemporalAttention(input_dim=512)

        self.classifier = nn.Sequential(
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, num_emotions),
        )

    def forward(self, x):
        if len(x.shape) == 3:
            x = x.unsqueeze(1)

        x = self.cnn(x)
        batch_size, channels, height, width = x.shape
        x = x.permute(0, 2, 3, 1).contiguous().view(batch_size, height * width, channels)
        x, _ = self.lstm(x)
        x = self.attention(x)
        return self.classifier(x)


class AudioRecognitionModel:
    """Wrapper for model loading and inference."""

    def __init__(self, model_path):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.scaler = self._load_joblib(SCALER_PATH)
        self.label_encoder = self._load_joblib(LABEL_ENCODER_PATH)
        self.class_names = self._get_class_names()
        self.expected_feature_count = self._get_expected_feature_count()
        self.n_mels, self.time_steps = self._infer_spectrogram_shape(self.expected_feature_count)

        if str(model_path).lower().endswith('.h5'):
            self.model = self._load_from_h5(model_path)
        else:
            self.model = self._load_from_pt(model_path)

        self.model = self.model.to(self.device)
        self.model.eval()
        print(f'Model ready on device: {self.device}')

    def _load_joblib(self, path):
        if not os.path.exists(path):
            return None
        try:
            return joblib.load(path)
        except Exception as error:
            print(f'Warning: failed to load {path}: {str(error)}')
            return None

    def _get_class_names(self):
        if self.label_encoder is not None and hasattr(self.label_encoder, 'classes_'):
            return [str(c) for c in self.label_encoder.classes_]
        return ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad']

    def _get_expected_feature_count(self):
        if self.scaler is not None and hasattr(self.scaler, 'n_features_in_'):
            return int(self.scaler.n_features_in_)
        return 30624

    def _infer_spectrogram_shape(self, feature_count):
        preferred_mels = [128, 96, 80, 64, 48, 40, 32, 24]
        for n_mels in preferred_mels:
            if feature_count % n_mels == 0:
                time_steps = feature_count // n_mels
                if time_steps >= 32:
                    return n_mels, time_steps

        side = int(np.sqrt(feature_count))
        for n_mels in range(side, 0, -1):
            if feature_count % n_mels == 0:
                return n_mels, feature_count // n_mels

        return 96, 319

    def _load_from_h5(self, model_path):
        model = AudioModelCNNLSTM(num_emotions=len(self.class_names))
        state_dict = model.state_dict()
        updated = {}

        with h5py.File(model_path, 'r') as h5_file:
            if 'weights' not in h5_file:
                raise Exception(f"No 'weights' group found in {model_path}")

            weights_group = h5_file['weights']
            for key, target_tensor in state_dict.items():
                if key not in weights_group:
                    continue
                tensor = torch.from_numpy(np.array(weights_group[key])).to(dtype=target_tensor.dtype)
                if tuple(tensor.shape) == tuple(target_tensor.shape):
                    updated[key] = tensor

            h5_classes = h5_file.attrs.get('classes')
            if h5_classes is not None:
                classes = [c.decode('utf-8') if isinstance(c, bytes) else str(c) for c in h5_classes]
                if classes:
                    self.class_names = classes

        state_dict.update(updated)
        model.load_state_dict(state_dict)
        print(f'Loaded {len(updated)} tensors from H5 weights')
        return model

    def _load_from_pt(self, model_path):
        loaded = torch.load(model_path, map_location=self.device)

        if isinstance(loaded, (dict, OrderedDict)):
            state_dict = loaded.get('model_state_dict', loaded) if isinstance(loaded, dict) else loaded
            model = AudioModelCNNLSTM(num_emotions=len(self.class_names))
            model.load_state_dict(state_dict)
            print('Loaded CNN-LSTM model from PT weights')
            return model

        print('Loaded full model object from PT')
        return loaded

    def predict(self, audio_features):
        """Predict class and probabilities for model-ready features."""
        with torch.no_grad():
            if not isinstance(audio_features, torch.Tensor):
                audio_features = torch.tensor(audio_features, dtype=torch.float32)

            if len(audio_features.shape) == 2:
                audio_features = audio_features.unsqueeze(0)

            audio_features = audio_features.to(self.device)
            output = self.model(audio_features)

            probabilities = torch.softmax(output, dim=1)
            predictions = torch.argmax(probabilities, dim=1)
            pred_indices = predictions.cpu().numpy().tolist()
            pred_labels = [
                self.class_names[i] if 0 <= i < len(self.class_names) else 'unknown'
                for i in pred_indices
            ]

            return {
                'predictions': pred_indices,
                'labels': pred_labels,
                'probabilities': probabilities.cpu().numpy().tolist(),
                'raw_output': output.cpu().numpy().tolist(),
            }


def load_model(model_path=None):
    """Load the trained model from H5/PT assets in saved_model/."""
    if model_path and os.path.exists(model_path):
        resolved_path = model_path
    else:
        resolved_path = next((path for path in MODEL_CANDIDATES if os.path.exists(path)), None)

    if not resolved_path:
        raise Exception('No model file found. Expected one of: ' + ', '.join(MODEL_CANDIDATES))

    try:
        return AudioRecognitionModel(resolved_path)
    except Exception as error:
        raise Exception(f'Failed to load model from {resolved_path}: {str(error)}')
