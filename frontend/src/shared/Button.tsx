import { forwardRef } from 'react';
import LoadingSpinner from './LoadingSpinner';

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  isLoading?: boolean;
};

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ children, className, isLoading, disabled, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={`bg-blue-500 text-white px-4 py-2 rounded-md
          hover:bg-blue-600 transition-all duration-300
          cursor-pointer
          ${className ?? ''}
          ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
          `}
        disabled={disabled}
        {...props}
      >
        {isLoading && (
          <div className="relative">
            <div className="absolute inset-y-3 left-0 right-0 flex justify-center items-center z-30">
              <LoadingSpinner />
            </div>
          </div>
        )}
        {children}
      </button>
    );
  }
);

export default Button;
