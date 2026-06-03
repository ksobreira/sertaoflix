import { useState, useCallback } from 'react';

export function useToast() {
  const [toast, setToast] = useState({ msg: '', tipo: 'ok', show: false });

  const show = useCallback((msg, tipo = 'ok') => {
    setToast({ msg, tipo, show: true });
    setTimeout(() => setToast(t => ({ ...t, show: false })), 3000);
  }, []);

  return { toast, show };
}

export function Toast({ toast }) {
  return (
    <div className={`toast ${toast.tipo} ${toast.show ? 'show' : ''}`}>
      {toast.msg}
    </div>
  );
}
