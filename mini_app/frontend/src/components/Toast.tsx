import { createContext, useContext, useState, useCallback, useRef, type ReactNode } from 'react';

interface ToastContextType {
  showToast: (message: string) => void;
}

const ToastContext = createContext<ToastContextType>({ showToast: () => {} });

export function useToast() {
  return useContext(ToastContext);
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toast, setToast] = useState<string | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout>>();

  const showToast = useCallback((msg: string) => {
    if (timerRef.current) clearTimeout(timerRef.current);
    setToast(msg);
    timerRef.current = setTimeout(() => setToast(null), 2000);
  }, []);

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      {toast && (
        <div style={{
          position: 'fixed', bottom: 32, left: '50%', transform: 'translateX(-50%)',
          background: 'var(--toast-bg)', color: 'var(--toast-text)',
          padding: '10px 20px', borderRadius: 20,
          fontSize: 14, fontWeight: 500, whiteSpace: 'nowrap',
          animation: 'fadeInUp 0.2s ease',
          zIndex: 1000,
          pointerEvents: 'none',
        }}>
          {toast}
        </div>
      )}
    </ToastContext.Provider>
  );
}
