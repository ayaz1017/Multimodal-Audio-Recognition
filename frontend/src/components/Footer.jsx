import './Footer.css';
import { Link } from 'react-router-dom';
import { FaHeartbeat, FaLock, FaRegFileAlt } from 'react-icons/fa';

function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="footer-content">
        <div className="footer-brand">
          <h4>Multimodal Audio Recognition</h4>
          <p>Emotion intelligence workflows for structured clinical and behavioral review.</p>
        </div>

        <div className="footer-pillars">
          <span><FaHeartbeat /> Signal Fusion</span>
          <span><FaRegFileAlt /> Report-Ready Output</span>
          <span><FaLock /> Protected Patient Scope</span>
        </div>

        <div className="footer-links">
          <Link to="/audio">Audio</Link>
          <Link to="/video">Video</Link>
          <Link to="/multimodal">Multimodal</Link>
          <Link to="/dashboard">Dashboard</Link>
        </div>

        <small className="footer-note">&copy; {year} Multimodal Audio Recognition. All rights reserved.</small>
      </div>
    </footer>
  );
}

export default Footer;
