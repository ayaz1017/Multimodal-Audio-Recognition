import './ResultsDisplay.css';
import { FaCheckCircle, FaExclamationCircle } from 'react-icons/fa';
import { useMemo, useState } from 'react';

function ResultsDisplay({ results, error, isLoading }) {
  const [showRaw, setShowRaw] = useState(false);

  const summary = useMemo(() => {
    if (!results) {
      return null;
    }

    if (results.predictions) {
      return {
        mode: 'Audio Analysis',
        emotion: results.predictions.emotion || 'Unknown',
        confidence: Number(results.predictions.probability || 0) * 100,
        detail: 'Speech feature extraction complete and classified by the emotion model.',
      };
    }

    if (results.data?.combined_analysis) {
      return {
        mode: 'Multimodal Analysis',
        emotion: results.data.combined_analysis.dominant_emotion || 'Unknown',
        confidence: Number(results.data.combined_analysis.audio_prediction_confidence || 0) * 100,
        detail: results.data.combined_analysis.recommendation || 'Audio and video signals were fused.',
      };
    }

    if (results.facial_expressions || results.video_info) {
      const dominant = results.facial_expressions?.dominant_emotion || 'Unknown';
      return {
        mode: 'Video Analysis',
        emotion: dominant,
        confidence: 0,
        detail: 'Facial expression timeline extracted from uploaded video.',
      };
    }

    return {
      mode: 'Analysis',
      emotion: 'Unknown',
      confidence: 0,
      detail: 'Result structure received from backend.',
    };
  }, [results]);

  const handleCopyRaw = async () => {
    if (!results) {
      return;
    }

    try {
      await navigator.clipboard.writeText(JSON.stringify(results, null, 2));
    } catch (copyError) {
      // Non-blocking fallback for browsers where clipboard is unavailable.
      console.error('Unable to copy raw result', copyError);
    }
  };

  if (isLoading) {
    return (
      <div className="results-container loading">
        <div className="spinner"></div>
        <p>Processing your file...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="results-container error">
        <FaExclamationCircle className="result-icon" />
        <h3>Error</h3>
        <p>{error}</p>
      </div>
    );
  }

  if (!results) {
    return null;
  }

  return (
    <div className="results-container success">
      <FaCheckCircle className="result-icon" />
      <h3>Analysis Complete</h3>

      {summary && (
        <div className="result-summary-grid">
          <article className="summary-card">
            <span>Mode</span>
            <strong>{summary.mode}</strong>
          </article>
          <article className="summary-card">
            <span>Detected Emotion</span>
            <strong>{summary.emotion}</strong>
          </article>
          <article className="summary-card">
            <span>Confidence</span>
            <strong>{summary.confidence ? `${summary.confidence.toFixed(1)}%` : 'N/A'}</strong>
          </article>
          <article className="summary-card">
            <span>Report Status</span>
            <strong>
              {results.report_generated ? 'Generated' : results.saved ? 'Saved (No report)' : 'Not linked'}
            </strong>
          </article>
        </div>
      )}

      {summary?.detail && <p className="summary-detail">{summary.detail}</p>}

      {results.report_id && (
        <div className="report-chip-row">
          <span className="report-chip">Report ID: {results.report_id}</span>
          <a href="/dashboard" className="report-link-btn">
            Open in Dashboard
          </a>
        </div>
      )}

      <div className="results-actions">
        <button type="button" onClick={() => setShowRaw((value) => !value)}>
          {showRaw ? 'Hide Raw JSON' : 'Show Raw JSON'}
        </button>
        <button type="button" onClick={handleCopyRaw}>
          Copy JSON
        </button>
      </div>

      {showRaw && <pre className="results-output">{JSON.stringify(results, null, 2)}</pre>}
    </div>
  );
}

export default ResultsDisplay;
