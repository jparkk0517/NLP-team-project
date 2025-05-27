import { type ReactNode, useRef, useCallback, useEffect } from 'react';

interface ModalProps {
  open?: boolean;
  children?: ReactNode;
  onClose?: () => void;
}

const Modal = ({ open, children, onClose }: ModalProps) => {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const handleClose = useCallback(() => {
    dialogRef.current?.close();
    onClose?.();
  }, [onClose]);
  useEffect(() => {
    dialogRef.current?.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        handleClose();
      }
    });
  }, [handleClose]);
  useEffect(() => {
    if (open) {
      dialogRef.current?.showModal();
    } else {
      dialogRef.current?.close();
    }
  }, [open]);
  return (
    <dialog ref={dialogRef} className='m-auto'>
      {open ? (
        <div className='flex flex-col w-full h-full min-w-[300px] min-h-[300px]'>
          <div className='w-full flex flex-row-reverse'>
            <button className='m-4 cursor-pointer' onClick={handleClose}>
              X
            </button>
          </div>
          {children}
        </div>
      ) : null}
    </dialog>
  );
};

export { Modal };
