import React, { useState, useEffect } from 'react';

function LoadingSpinner() {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(false), 3000); // 3초 후에 fade-out 시작
    return () => clearTimeout(timer);
  }, []);

  const spinnerStyle: React.CSSProperties = {
    width: '20px',
    height: '20px',
    border: '4px solid #ccc',
    borderTop: '2px solid #1d72b8',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
    margin: 'auto',
    opacity: isVisible ? 1 : 0,
    transition: 'opacity 1.5s ease-out', // fade-out 애니메이션 추가
  };

  const wrapperStyle: React.CSSProperties = {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
  };

  return (
    <div style={wrapperStyle}>
      <div style={spinnerStyle} />
      <style>
        {`
          @keyframes spin {
            0%   { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}
      </style>
    </div>
  );
}

export default LoadingSpinner;
