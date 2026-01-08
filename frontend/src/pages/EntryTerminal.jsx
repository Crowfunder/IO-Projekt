import React, { useState, useRef, useEffect } from 'react';
import Webcam from 'react-webcam';
import './EntryTerminal.css';

const EntryTerminal = () => {
  const webcamRef = useRef(null);
  const [status, setStatus] = useState('idle'); // 'idle' | 'processing' | 'granted' | 'denied'
  const [currentTime, setCurrentTime] = useState(new Date());

  // Update timestamp clock every second
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // Format date like the mockup: 12:03-24.12.25-WED
  const formatTime = (date) => {
    const pad = (n) => n.toString().padStart(2, '0');
    const time = `${pad(date.getHours())}:${pad(date.getMinutes())}`;
    const day = pad(date.getDate());
    const month = pad(date.getMonth() + 1);
    const year = date.getFullYear().toString().slice(-2);
    const weekDay = date.toLocaleDateString('en-US', { weekday: 'short' }).toUpperCase();
    return `${time}-${day}.${month}.${year}-${weekDay}`;
  };

  useEffect(() => {
    let interval;
    if (status === 'idle') {
      interval = setInterval(() => {
        handleScan();
      }, 3000);
    }
    return () => clearInterval(interval);
  }, [status]);
  // CONFIGURATION: Change this to your actual backend endpoint
  const API_ENDPOINT = "/api/skan";

  const handleScan = async () => {
    if (!webcamRef.current || !webcamRef.current.video || webcamRef.current.video.readyState !== 4) {
        return;
    }

    if (status !== 'idle') return;

    setStatus('processing');
    // Prevent double-scanning while waiting
    if (status !== 'idle') return;

    setStatus('processing');
    
    // 1. Capture the image from webcam
    const imageSrc = webcamRef.current.getScreenshot();

    try {
      // 2. Send to Backend
      const response = await fetch(API_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        // We send the image as a base64 string
        body: JSON.stringify({ 
          image: imageSrc, 
          timestamp: new Date().toISOString() 
        }),
      });

      const data = await response.json();

      // 3. Handle Backend Response
      // We assume your backend returns { granted: true/false }
      if (data.granted === true) {
        setStatus('granted');
      } else {
        setStatus('denied');
      }

    } catch (error) {
      console.error("Backend Error:", error);
      setStatus('denied'); // Default to denied on network error
    }

    // 4. Reset to 'idle' after 3 seconds so the next person can scan
    setTimeout(() => {
      setStatus('idle');
    }, 3000);
  };

  return (
    <div className="terminal-container">
      {/* 1. Camera Feed */}
      <Webcam
        audio={false}
        ref={webcamRef}
        screenshotFormat="image/jpeg"
        className="webcam-video"
      />

      {/* 2. Visual Effects */}
      <div className="scanlines"></div>

      {/* 3. Header (REC & Time) */}
      <div className="header-bar">
        <div className="rec-badge">
          <div className="red-dot"></div> REC
        </div>
        <div className="timestamp">
          {formatTime(currentTime)}
        </div>
      </div>

      {/* 4. Scanning Zone Indicator */}
      {status === 'idle' && <div className="scan-zone"></div>}

      {/* 5. Status Messages */}
      <div className="status-box">
        {status === 'idle' && (
          <p>Hello, please<br/>verify Your QR<br/>code above</p>
        )}
        {status === 'processing' && (
          <p>Verifying...<br/>Please wait</p>
        )}
        {status === 'granted' && (
          <p style={{ color: '#4ade80' }}>Access<br/>Granted</p>
        )}
        {status === 'denied' && (
          <p style={{ color: '#f87171' }}>Access<br/>Denied</p>
        )}
      </div>
    </div>
  );
};

export default EntryTerminal;