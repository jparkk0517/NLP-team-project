import { forwardRef } from 'react';

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement>;

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ children, className, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={`bg-blue-500 text-white px-4 py-2 rounded-md
          hover:bg-blue-600 transition-all duration-300
          cursor-pointer
          ${className ?? ''}`}
        {...props}>
        {children}
      </button>
    );
  }
);

export default Button;
