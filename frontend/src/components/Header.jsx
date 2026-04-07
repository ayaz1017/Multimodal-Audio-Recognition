import { Link, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { FiMenu, FiX, FiMoon, FiSun } from 'react-icons/fi';
import { FaUserCircle, FaWaveSquare } from 'react-icons/fa';
import { useTheme } from '../context/ThemeContext';
import './Header.css';

function Header({ apiStatus }) {
  const navigate = useNavigate();
  const location = useLocation();
  const { isDarkMode, toggleTheme } = useTheme();
  const [user, setUser] = useState(null);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    }
  }, []);

  useEffect(() => {
    setMobileMenuOpen(false);
    setShowUserMenu(false);
  }, [location.pathname]);

  const statusLabel =
    apiStatus === 'connected'
      ? 'API Online'
      : apiStatus === 'disconnected'
        ? 'API Offline'
        : 'Checking API';

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('selectedPatient');
    setUser(null);
    navigate('/');
  };

  return (
    <header className="header">
      <div className="header-container">
        <div className="brand-group">
          <Link to="/" className="logo">
            <span className="logo-mark" aria-hidden="true">
              <FaWaveSquare />
            </span>
            <span className="logo-text">
              <strong>Multimodal Audio</strong>
              <small>Clinical Intelligence Platform</small>
            </span>
          </Link>
          <button
            type="button"
            className="nav-toggle"
            onClick={() => setMobileMenuOpen((prev) => !prev)}
            aria-label={mobileMenuOpen ? 'Close navigation menu' : 'Open navigation menu'}
            aria-expanded={mobileMenuOpen}
          >
            {mobileMenuOpen ? <FiX /> : <FiMenu />}
          </button>
        </div>

        <nav className={`nav ${mobileMenuOpen ? 'open' : ''}`}>
          <Link to="/" className="nav-link" onClick={() => setMobileMenuOpen(false)}>Home</Link>
          <Link to="/audio" className="nav-link" onClick={() => setMobileMenuOpen(false)}>Audio</Link>
          <Link to="/video" className="nav-link" onClick={() => setMobileMenuOpen(false)}>Video</Link>
          <Link to="/multimodal" className="nav-link" onClick={() => setMobileMenuOpen(false)}>Multimodal</Link>
          {user && (
            <Link to="/dashboard" className="nav-link dashboard-link" onClick={() => setMobileMenuOpen(false)}>
              Dashboard
            </Link>
          )}
        </nav>

        <div className="header-right">
          <span className={`api-status ${apiStatus}`}>
            <span className="status-dot" aria-hidden="true" />
            {statusLabel}
          </span>

          <button 
            className="theme-toggle"
            onClick={toggleTheme}
            title={isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {isDarkMode ? <FiSun /> : <FiMoon />}
          </button>

          {user ? (
            <div className="user-menu">
              <button 
                className="user-button"
                onClick={() => setShowUserMenu(!showUserMenu)}
              >
                <FaUserCircle aria-hidden="true" />
                <span>{user.full_name || user.email}</span>
              </button>
              {showUserMenu && (
                <div className="dropdown-menu">
                  <Link to="/dashboard" className="dropdown-item">
                    My Dashboard
                  </Link>
                  <button 
                    className="dropdown-item logout"
                    onClick={handleLogout}
                  >
                    Logout
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="auth-buttons">
              <Link to="/login" className="auth-btn login">Sign In</Link>
              <Link to="/signup" className="auth-btn signup">Sign Up</Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

export default Header;
