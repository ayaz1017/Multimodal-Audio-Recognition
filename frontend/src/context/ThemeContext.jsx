import React, { createContext, useState, useEffect } from 'react';

export const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    // Check localStorage first, then system preference
    const saved = localStorage.getItem('theme');
    if (saved) {
      return saved === 'dark';
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  useEffect(() => {
    // Save theme preference
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
    
    // Update document class
    if (isDarkMode) {
      document.documentElement.classList.add('dark-mode');
      document.documentElement.classList.remove('light-mode');
    } else {
      document.documentElement.classList.add('light-mode');
      document.documentElement.classList.remove('dark-mode');
    }
  }, [isDarkMode]);

  const toggleTheme = () => {
    setIsDarkMode(prev => !prev);
  };

  const theme = {
    isDarkMode,
    // Light mode colors
    light: {
      bg: '#ffffff',
      bgSecondary: '#f8f9fa',
      bgTertiary: '#f0f2f5',
      text: '#1a1a1a',
      textSecondary: '#666666',
      textTertiary: '#999999',
      border: '#e0e0e0',
      borderLight: '#f0f0f0',
    },
    // Dark mode colors
    dark: {
      bg: '#0f1419',
      bgSecondary: '#1a1f2e',
      bgTertiary: '#242d3d',
      text: '#ffffff',
      textSecondary: '#e0e0e0',
      textTertiary: '#b0b0b0',
      border: '#3a4a5e',
      borderLight: '#2a3a4e',
    },
  };

  const colors = isDarkMode ? theme.dark : theme.light;

  return (
    <ThemeContext.Provider value={{ isDarkMode, toggleTheme, theme, colors }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = React.useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};
