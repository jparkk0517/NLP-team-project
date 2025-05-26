import { forwardRef } from 'react';

type TextAreaProps = React.TextareaHTMLAttributes<HTMLTextAreaElement>;

const TextArea = forwardRef<HTMLTextAreaElement, TextAreaProps>(
  ({ className, disabled = false, ...props }, ref) => {
    return (
      <textarea
        className={`border-2 rounded-md p-2 ${className} ${
          disabled ? 'opacity-50' : ''
        } ${disabled ? 'border-gray-300' : 'border-gray-500'}
        ${disabled ? 'bg-gray-300' : ''}
        `}
        disabled={disabled}
        {...props}
        ref={ref}
      />
    );
  }
);

export default TextArea;
