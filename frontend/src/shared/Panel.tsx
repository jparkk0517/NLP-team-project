import { LuPanelRight, LuPanelBottom } from 'react-icons/lu';

import React, { useMemo, useState, type ReactNode } from 'react';

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

  const classNames = useMemo(() => {
    const classNameList = [
      'rounded-lg',
      'm-2',
      'border-1',
      'border-gray-600',
    ];
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
      {!isMinimized && <div className='p-4 h-[95%] 
      overflow-auto'>{children}</div>}
    </div>
  );
};

export default Panel;
