import { LuPanelRight, LuPanelBottom } from 'react-icons/lu';

import React, { useState, type ReactNode } from 'react';

interface PanelProps {
  title: string;
  children: ReactNode;
  className?: string;
  minimizedClassName?: string;
  minimizeDirection?: 'vertical' | 'horizontal';
}

const Panel: React.FC<PanelProps> = ({
  title,
  children,
  className,
  minimizedClassName,
  minimizeDirection = 'vertical',
}) => {
  const [isMinimized, setIsMinimized] = useState(false);

  const toggleMinimize = () => {
    setIsMinimized(!isMinimized);
  };

  return (
    <div
      className={`rounded-lg m-2 border-1 border-gray-600 ${
        isMinimized ? minimizedClassName : className
      } ${isMinimized && minimizeDirection === 'horizontal' ? 'w-15' : ''} ${
        isMinimized && minimizeDirection === 'vertical' ? 'h-15' : ''
      }`}>
      {/* Title Bar */}
      <div className='flex items-center justify-between px-4 py-2 border-b border-gray-600'>
        {!isMinimized && <h2 className='font-semibold text-base'>{title}</h2>}

        <button
          onClick={toggleMinimize}
          className='hover:opacity-80 transition-opacity cursor-pointer'>
          {isMinimized ? (
            minimizeDirection === 'vertical' ? (
              <LuPanelBottom />
            ) : (
              <LuPanelRight />
            )
          ) : minimizeDirection === 'vertical' ? (
            <LuPanelBottom />
          ) : (
            <LuPanelRight />
          )}
        </button>
      </div>

      {/* Body */}
      {!isMinimized && <div className='p-4 h-full'>{children}</div>}
    </div>
  );
};

export default Panel;
