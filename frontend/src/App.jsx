import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Dashboard from './pages/Dashboard';
import UploadCSV from './pages/UploadCSV';
import ManageGestures from './pages/ManageGestures';
import TrainingResults from './pages/TrainingResults';
import Predict from './pages/Predict';
import LivePredict from './pages/LivePredict';
import AdminTools from './pages/AdminTools';
import UploadTrainingCSV from './pages/UploadTrainingCSV';
import PredictionHistory from './pages/PredictionHistory';
import AudioManager from './pages/AudioManager';
import TTSManager from './pages/TTSManager';
import CSVManager from './pages/CSVManager';
import { MdDarkMode, MdMenu, MdClose } from 'react-icons/md';
import Login from './pages/Login';
import { apiRequest } from './api';

function useDarkMode() {
  const [dark, setDark] = useState(() => {
    if (typeof window !== 'undefined') {
      return document.body.classList.contains('dark');
    }
    return false;
  });
  useEffect(() => {
    if (dark) {
      document.body.classList.add('dark');
    } else {
      document.body.classList.remove('dark');
    }
  }, [dark]);
  return [dark, setDark];
}

const App = () => {
  const [dark, setDark] = useDarkMode();
  const [navOpen, setNavOpen] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Try to fetch current user
    const checkAuth = async () => {
      if (import.meta.env.DEV) console.debug('checkAuth started');
      try {
        const token = localStorage.getItem('access_token');
        if (import.meta.env.DEV) console.debug('Token from localStorage:', token ? 'exists' : 'not found');
        if (token) {
          const userData = await apiRequest('get', '/auth/me');
          if (import.meta.env.DEV) console.debug('User data received:', userData);
          setUser(userData);
        } else {
          if (import.meta.env.DEV) console.debug('No token found, setting user to null');
          setUser(null);
        }
      } catch (error) {
        if (import.meta.env.DEV) console.error('Auth error:', error);
        // Token is invalid, remove it
        localStorage.removeItem('access_token');
        setUser(null);
      } finally {
        if (import.meta.env.DEV) console.debug('Setting loading to false');
        setLoading(false);
      }
    };
    
    checkAuth();
  }, []);

  const signOut = async () => {
    try {
      await apiRequest('post', '/auth/logout');
      localStorage.removeItem('access_token');
      setUser(null);
      toast.success('Signed out');
    } catch (e) {
      toast.error('Failed to sign out');
    }
  };

  const isEditor = user?.role === 'editor' || user?.role === 'admin';

  const navLinks = [
    { to: '/', label: 'Dashboard' },
    { to: '/gestures', label: 'Manage Gestures' },
    { to: '/training-results', label: 'Training Results' },
    { to: '/predict', label: 'Manual Prediction' },
    { to: '/live-predict', label: 'Live Predict' },
    // editor-only routes
    ...(isEditor ? [
      { to: '/csv-manager', label: 'CSV & Training Manager' },
      { to: '/admin', label: 'Admin Tools' },
      { to: '/audio-manager', label: 'Audio Manager' },
      { to: '/tts-manager', label: 'TTS Manager' },
    ] : []),
  ];

  // Show loading spinner while checking authentication
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="spinner" style={{ margin: '0 auto 1rem' }}></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <header className="main-header">
          <div className="header-row header-top">
            <div className="header-title">Sign Glove</div>
            <div className="header-actions">
              {user ? (
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <span style={{ fontSize: 14 }}>Signed in as {user.email} ({user.role})</span>
                  <button className="btn btn-secondary" onClick={signOut}>Sign Out</button>
                </div>
              ) : (
                <Link to="/login" className="btn btn-secondary">Sign In</Link>
              )}
              {/* Hamburger menu for mobile */}
              <button
                className="header-hamburger"
                aria-label={navOpen ? 'Close menu' : 'Open menu'}
                onClick={() => setNavOpen(o => !o)}
              >
                {navOpen ? <MdClose size={28} /> : <MdMenu size={28} />}
              </button>
              <button
                className="btn btn-secondary header-darkmode-btn"
                aria-label={dark ? 'Switch to light mode' : 'Switch to dark mode'}
                onClick={() => setDark(d => !d)}
                style={{ display: 'flex', alignItems: 'center' }}
              >
                <MdDarkMode style={{ fontSize: 22, marginRight: 6 }} />
                {dark ? 'Light' : 'Dark'} Mode
              </button>
            </div>
          </div>
          {/* Nav links: show row on desktop, vertical menu on mobile if open */}
          <nav className={`header-nav${navOpen ? ' nav-open' : ''}`}>
            {navLinks.map(link => (
              <Link
                key={link.to}
                to={link.to}
                className="hover:underline"
                onClick={() => setNavOpen(false)}
              >
                {link.label}
              </Link>
            ))}
          </nav>
        </header>

        <main className="p-4" style={{ position: 'relative', zIndex: 1 }}>
          <Routes>
            <Route path="/" element={<Dashboard user={user} />} />
            <Route path="/upload-csv" element={isEditor ? <UploadCSV user={user} /> : <Dashboard user={user} />} />
            <Route path="/upload-training-csv" element={isEditor ? <UploadTrainingCSV user={user} /> : <Dashboard user={user} />} />
            <Route path="/csv-manager" element={isEditor ? <CSVManager user={user} /> : <Dashboard user={user} />} />
            <Route path="/gestures" element={<ManageGestures user={user} />} />
            <Route path="/training-results" element={<TrainingResults user={user} />} />
            <Route path="/predict" element={<Predict user={user} />} />
            <Route path="/live-predict" element={<LivePredict user={user} />} />
            <Route path="/history" element={<PredictionHistory user={user} />} />
            <Route path="/admin" element={isEditor ? <AdminTools user={user} /> : <Dashboard user={user} />} />
            <Route path="/audio-manager" element={isEditor ? <AudioManager user={user} /> : <Dashboard user={user} />} />
            <Route path="/tts-manager" element={isEditor ? <TTSManager user={user} /> : <Dashboard user={user} />} />
            <Route path="/login" element={<Login onLogin={setUser} />} />
          </Routes>
        </main>

        <ToastContainer />

        <footer className="text-center text-sm text-gray-500 py-4">
          &copy; 2025 Sign Glove AI
        </footer>
      </div>
    </Router>
  );
};

export default App;
