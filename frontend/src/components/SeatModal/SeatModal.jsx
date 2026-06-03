import { useState, useEffect } from 'react';
import { getAssentos, comprarIngresso } from '../../services/api';
import styles from './SeatModal.module.css';

const LETRAS = ['A','B','C','D','E','F'];
const COLS   = 8;

function fmtMoeda(v) {
  return 'R$ ' + Number(v || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 });
}

export default function SeatModal({ filme, onClose, onSuccess }) {
  const [ocupados,    setOcupados]    = useState([]);
  const [selecionado, setSelecionado] = useState(null);
  const [loading,     setLoading]     = useState(true);
  const [comprando,   setComprando]   = useState(false);

  useEffect(() => {
    setSelecionado(null);
    setLoading(true)
    getAssentos(filme.id).then(d => { setOcupados(d); setLoading(false); });
  }, [filme.id]);

  async function confirmar() {
    if (!selecionado) return;
    setComprando(true);
    const res = await comprarIngresso({
      valor: filme.valor, assento: selecionado,
      id_sessao: filme.id, tipo_desconto: 'Inteira',
    });
    setComprando(false);
    if (res.success) {
      onSuccess(`✅ Ingresso #${res.id_ingresso} confirmado! Assento ${selecionado}`);
      onClose();
    }
  }

  return (
    <div className={styles.overlay} onClick={e => e.target === e.currentTarget && onClose()}>
      <div className={styles.modal}>
        <div className={styles.header}>
          <div>
            <h2 className={styles.title}>{filme.titulo}</h2>
            <p className={styles.sub}>
              {filme.cinema} · Sala {filme.numero_sala} ({filme.tipo_sala})
            </p>
          </div>
          <button className={styles.close} onClick={onClose}>✕</button>
        </div>

        <p className={styles.sinopse}>{filme.sinopse}</p>

        <div className={styles.telaLabel}>TELA</div>
        <div className={styles.tela} />

        {loading ? (
          <div className="loader"><div className="spinner" /></div>
        ) : (
          <div className={styles.grid}>
            {LETRAS.flatMap(l =>
              Array.from({ length: COLS }, (_, i) => {
                const cod = `${l}${i + 1}`;
                const oc  = ocupados.includes(cod);
                const sel = selecionado === cod;
                return (
                  <button
                    key={cod}
                    disabled={oc}
                    onClick={() => setSelecionado(cod)}
                    className={`${styles.seat} ${oc ? styles.ocupado : sel ? styles.sel : styles.livre}`}
                  >
                    {cod}
                  </button>
                );
              })
            )}
          </div>
        )}

        <div className={styles.legenda}>
          <span><i className={`${styles.dot} ${styles.livre}`} /> Livre</span>
          <span><i className={`${styles.dot} ${styles.sel}`}   /> Selecionado</span>
          <span><i className={`${styles.dot} ${styles.ocupado}`}/> Ocupado</span>
        </div>

        <div className={styles.footer}>
          <div className={styles.info}>
            Assento: <strong>{selecionado || '—'}</strong>
            <br />
            Valor: <strong style={{ color: 'var(--green)' }}>
              {selecionado ? fmtMoeda(filme.valor) : '—'}
            </strong>
          </div>
          <button
            className={styles.btn}
            disabled={!selecionado || comprando}
            onClick={confirmar}
          >
            {comprando ? '...' : 'Confirmar'}
          </button>
        </div>
      </div>
    </div>
  );
}
