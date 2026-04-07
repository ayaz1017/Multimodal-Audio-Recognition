import React from 'react';
import { Link } from 'react-router-dom';
import {
  FaArrowRight,
  FaBrain,
  FaChartLine,
  FaFileMedical,
  FaHeadphones,
  FaRegEye,
  FaShieldAlt,
  FaSlidersH,
  FaUserMd,
  FaWaveSquare,
} from 'react-icons/fa';
import './Home.css';

function Home() {
  return (
    <div className="home">
      <section className="hero-section">
        <div className="hero-copy">
          <span className="hero-eyebrow">Clinical AI Suite</span>
          <h1>Multimodal Intelligence for Real-World Emotional Signal Analysis</h1>
          <p>
            Analyze voice and facial cues in one workflow, link every run to a patient profile,
            and generate report-ready insights in minutes.
          </p>
          <div className="hero-actions">
            <Link to="/multimodal" className="hero-btn primary">
              Start Multimodal Session
              <FaArrowRight aria-hidden="true" />
            </Link>
            <Link to="/dashboard" className="hero-btn secondary">
              Open Patient Dashboard
            </Link>
          </div>
        </div>

        <div className="hero-panel">
          {/* Fix 1: both sibling panel-cards now use <h3> for consistent heading level */}
          <article className="panel-card">
            <h3>Live Pipeline</h3>
            <ul>
              <li><FaHeadphones aria-hidden="true" /> Audio feature extraction</li>
              <li><FaRegEye aria-hidden="true" /> Facial expression timeline</li>
              <li><FaBrain aria-hidden="true" /> Emotion fusion + confidence scoring</li>
              <li><FaFileMedical aria-hidden="true" /> Auto-generated clinical report</li>
            </ul>
          </article>

          <article className="panel-card metrics">
            <h3>Platform Focus</h3> {/* was <h4>, now matches sibling <h3> */}
            <div className="metric-grid">
              <div>
                <strong>Audio + Video</strong>
                <span>Unified signal interpretation</span>
              </div>
              <div>
                <strong>Patient Context</strong>
                <span>History-aware analysis records</span>
              </div>
              <div>
                <strong>Structured Reports</strong>
                <span>Actionable recommendation output</span>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section className="signal-strip">
        <div>
          <span>Workflow</span>
          <strong>Upload → Analyze → Report</strong> {/* Fix 2: use proper arrow character */}
        </div>
        <div>
          <span>Built For</span>
          <strong>Clinical review and behavioral assessments</strong>
        </div>
        <div>
          <span>Output</span>
          <strong>Confidence-backed emotion intelligence</strong>
        </div>
      </section>

      <section className="features-grid">
        {/* Fix 3: add aria-label to icon-accompanied Links so screen readers get a useful label */}
        <Link
          to="/audio"
          className="feature-card large"
          aria-label="Audio Intelligence – go to audio analysis"
        >
          <FaWaveSquare className="feature-icon" aria-hidden="true" />
          <h3>Audio Intelligence</h3>
          <p>Detect emotional patterns from uploaded speech with calibrated confidence output.</p>
        </Link>

        <Link
          to="/video"
          className="feature-card"
          aria-label="Video Emotion Trace – go to video analysis"
        >
          <FaRegEye className="feature-icon" aria-hidden="true" />
          <h3>Video Emotion Trace</h3>
          <p>Analyze frame-level expression dynamics and identify dominant cues over time.</p>
        </Link>

        <Link
          to="/multimodal"
          className="feature-card"
          aria-label="Fusion Analysis – go to multimodal session"
        >
          <FaSlidersH className="feature-icon" aria-hidden="true" />
          <h3>Fusion Analysis</h3>
          <p>Correlate audio and facial signals in one pass for richer interpretation quality.</p>
        </Link>

        <Link
          to="/dashboard"
          className="feature-card wide"
          aria-label="Patient Intelligence Hub – open dashboard"
        >
          <FaChartLine className="feature-icon" aria-hidden="true" />
          <h3>Patient Intelligence Hub</h3>
          <p>Track sessions, filter reports, and review emotional trends from a single dashboard.</p>
        </Link>
      </section>

      <section className="process-section">
        <h2>How the Workflow Moves</h2>
        <div className="steps">
          <article className="step">
            <span className="step-number">01</span>
            <h4>Select Mode</h4>
            <p>Choose audio, video, or multimodal mode based on your session objective.</p>
          </article>
          <article className="step">
            <span className="step-number">02</span>
            <h4>Run Analysis</h4>
            <p>Upload files, enrich with notes, and process signals through the trained model stack.</p>
          </article>
          <article className="step">
            <span className="step-number">03</span>
            <h4>Review Results</h4>
            <p>Inspect confidence, detected emotions, and recommendations inside patient records.</p>
          </article>
        </div>
      </section>

      <section className="advanced-section">
        <div className="advanced-header">
          <h2>Care-Oriented Platform Modules</h2>
          <p>
            Designed for practitioners who need interpretability, consistency, and patient-safe workflows.
          </p>
        </div>

        <div className="advanced-grid">
          <article className="advanced-card">
            <FaUserMd className="advanced-icon" aria-hidden="true" />
            <h4>Session Context Capture</h4>
            <p>Attach clinical notes during analysis to preserve context and improve later review.</p>
          </article>
          <article className="advanced-card">
            <FaFileMedical className="advanced-icon" aria-hidden="true" />
            <h4>Report-Ready Output</h4>
            <p>Summaries include confidence, dominant cues, and recommendation blocks for follow-up.</p>
          </article>
          <article className="advanced-card">
            <FaShieldAlt className="advanced-icon" aria-hidden="true" />
            <h4>Protected Patient Scope</h4>
            <p>Authenticated access keeps analysis and reports scoped to the authorized user account.</p>
          </article>
        </div>

        <div className="advanced-actions">
          <Link to="/dashboard" className="advanced-action primary">
            Open Intelligence Dashboard
          </Link>
          <Link to="/audio" className="advanced-action secondary">
            Start Audio Session
          </Link>
        </div>
      </section>
    </div>
  );
}

export default Home;