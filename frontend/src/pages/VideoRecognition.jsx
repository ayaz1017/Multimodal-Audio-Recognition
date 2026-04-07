import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import FileUpload from '../components/FileUpload';
import ResultsDisplay from '../components/ResultsDisplay';
import { recognizeVideo } from '../services/api';
import './Recognition.css';

function VideoRecognition() {
  const [file, setFile] = useState(null);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [notes, setNotes] = useState('');
  const isAuthenticated = Boolean(localStorage.getItem('token'));
  const selectedPatient = useMemo(() => {
    if (!isAuthenticated) {
      return null;
    }

    try {
      return JSON.parse(localStorage.getItem('selectedPatient') || 'null');
    } catch {
      return null;
    }
  }, [isAuthenticated]);

  const handleFileSelect = async (selectedFile) => {
    setFile(selectedFile);
    setError(null);
    setResults(null);
    setIsLoading(true);

    try {
      const response = await recognizeVideo(
        selectedFile,
        isAuthenticated ? selectedPatient?.patient_id || null : null,
        notes.trim()
      );
      setResults(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Error processing video file');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="recognition-page">
      <div className="recognition-container">
        <h1>Video Recognition</h1>
        <p>Upload a video file to detect and analyze facial expressions</p>

        {selectedPatient ? (
          <div className="patient-context-banner">
            <span className="context-label">Active Patient</span>
            <strong>{selectedPatient.name}</strong>
            <span>{selectedPatient.patient_id}</span>
          </div>
        ) : (
          <div className="patient-context-banner warning">
            <span className="context-label">No Patient Selected</span>
            <span>
              Analysis will run, but reports will not be tied to a patient.{' '}
              <Link to="/dashboard">Select patient in dashboard</Link>.
            </span>
          </div>
        )}

        <FileUpload
          onFileSelect={handleFileSelect}
          acceptedFiles={{
            'video/*': ['.mp4', '.avi', '.mov', '.mkv', '.webm'],
          }}
          isLoading={isLoading}
        />

        {file && (
          <div className="file-info">
            <p>
              <strong>Selected File:</strong> {file.name}
            </p>
            <p>
              <strong>Size:</strong> {(file.size / 1024 / 1024).toFixed(2)} MB
            </p>
          </div>
        )}

        <div className="analysis-note-box">
          <label htmlFor="video-notes">Clinical Note (optional)</label>
          <textarea
            id="video-notes"
            placeholder="Add context for this analysis (session behavior, observed signals, follow-up)..."
            value={notes}
            onChange={(event) => setNotes(event.target.value)}
            rows="3"
          />
        </div>

        <ResultsDisplay results={results} error={error} isLoading={isLoading} />
      </div>
    </div>
  );
}

export default VideoRecognition;
