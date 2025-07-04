import { LuPanelRight, LuPanelBottom } from 'react-icons/lu';

import React, { useMemo, useState, type ReactNode } from 'react';
import LoadingSpinner from './LoadingSpinner';

interface PanelProps {
  title: string;
  children: ReactNode;
  className?: string;
  minimizedClassName?: string;
  minimizeDirection?: 'vertical' | 'horizontal';
  isPending?: boolean;
  defaultMinimized?: boolean;
  minimizeContent?: ReactNode;
}

const Panel: React.FC<PanelProps> = ({
  title,
  children,
  className,
  minimizedClassName,
  minimizeDirection = 'vertical',
  isPending = false,
  defaultMinimized = false,
  minimizeContent,
}) => {
  const [isMinimized, setIsMinimized] = useState(defaultMinimized);

  const toggleMinimize = () => {
    setIsMinimized(!isMinimized);
  };

  const classNames = useMemo(() => {
    const classNameList = ['rounded-lg', 'm-2', 'border-1', 'border-gray-600'];
    if (isMinimized) {
      classNameList.push(minimizedClassName);
      if (minimizeDirection === 'horizontal') {
        classNameList.push('w-15');
      }
      if (minimizeDirection === 'vertical') {
        classNameList.push('h-15');
      }
    } else {
      classNameList.push(className);
    }
    return classNameList.join(' ');
  }, [className, isMinimized, minimizeDirection, minimizedClassName]);

  return (
    <div className={classNames}>
      {/* Title Bar */}
      <div className='h-[5%] flex items-center justify-between px-4 py-2 border-b border-gray-600'>
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
      {!isMinimized ? (
        <div
          className='p-4 h-[95%] 
      overflow-auto relative'>
          {
            <>
              {isPending && (
                <div className='flex justify-center items-center h-full opacity-50 absolute top-0 left-0 w-full z-10 bg-black/50'>
                  <LoadingSpinner />
                </div>
              )}
              {children}
            </>
          }
        </div>
      ) : (
        <div className='p-4 h-[95%] overflow-auto relative flex flex-col'>
          {minimizeContent}
        </div>
      )}
    </div>
  );
};

export default Panel;
