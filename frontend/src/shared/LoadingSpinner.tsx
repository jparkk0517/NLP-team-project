import React from 'react';

function LoadingSpinner() {
  const spinnerStyle: React.CSSProperties = {
    width: '20px',
    height: '20px',
    border: '4px solid #ccc',
    borderTop: '2px solid #1d72b8',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
    margin: 'auto',
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
