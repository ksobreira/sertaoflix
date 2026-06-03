import { useState, useEffect, useMemo } from 'react';
import Navbar from '../../components/Navbar/Navbar';
import SeatModal from '../../components/SeatModal/SeatModal';
import { Toast, useToast } from '../../components/Toast';
import { getFilmes } from '../../services/api';
import styles from './Home.module.css';

const ROWS = [
  '🔥 Em Alta no Nordeste',
  '🌵 Clássicos do Sertão',
  '⭐ Mais Bem Avaliados',
  '🎬 Lançamentos',
];

function fmtHora(dt) {
  if (!dt) return '—';
  return new Date(dt).toLocaleString('pt-BR', {
    day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit',
  });
}

function fmtDur(m) {
  if (!m) return '—';
  return `${Math.floor(m / 60)}h ${String(m % 60).padStart(2, '0')}m`;
}

export default function Home() {
  const [filmes,     setFilmes]     = useState([]);
  const [loading,    setLoading]    = useState(true);
  const [filmeModal, setFilmeModal] = useState(null);
  const [hoverId,    setHoverId]    = useState(null);
  const { toast, show } = useToast();

  useEffect(() => {
    getFilmes().then(d => { setFilmes(d); setLoading(false); });
  }, []);

  const rows = useMemo(() => {
    return ROWS.map(label => ({
      label,
      filmes: [...filmes].sort(() => Math.random() - 0.5),
    }));
  }, [filmes]);

  const matchPct = useMemo(() => {
    const map = {};
    filmes.forEach(f => { map[f.id] = Math.floor(Math.random() * 15 + 82); });
    return map;
  }, [filmes]);

  const hero = filmes[0];

  if (loading) return (
    <div className="loader" style={{ minHeight: '100vh' }}>
      <div className="spinner" />Carregando catálogo...
    </div>
  );

  return (
    <div className={styles.page}>
      <Navbar />

      {hero && (
        <section className={styles.hero}>
          <div className={styles.heroEmoji}>{hero.emoji}</div>
          <div className={styles.heroContent}>
            <span className={styles.heroBadge}>EM DESTAQUE</span>
            <h1 className={styles.heroTitle}>{hero.titulo}</h1>
            <div className={styles.heroMeta}>
              <span className={styles.heroMatch}>97% relevante</span>
              <span className={styles.heroClassif}>{hero.classificacao}</span>
              <span>{fmtDur(hero.duracao)}</span>
            </div>
            <p className={styles.heroDesc}>{hero.sinopse}</p>
            <div className={styles.heroBtns}>
              <button
                className={styles.btnPlay}
                onClick={() => setFilmeModal(hero)}
              >
                ▶ Comprar Ingresso
              </button>
              <button
                className={styles.btnInfo}
                onClick={() => setFilmeModal(hero)}
              >
                ℹ Mais informações
              </button>
            </div>
          </div>
        </section>
      )}

      <div className={styles.rows}>
        {rows.map(({ label, filmes: rowFilmes }) => (
          <div key={label} className={styles.row}>
            <h2 className={styles.rowTitle}>{label}</h2>
            <div className={styles.carousel}>
              {rowFilmes.map(f => {
                const hoverKey = `${label}-${f.id}`;
                return (
                  <div
                    key={f.id}
                    className={`${styles.card} ${hoverId === hoverKey ? styles.hovered : ''}`}
                    onMouseEnter={() => setHoverId(hoverKey)}
                    onMouseLeave={() => setHoverId(null)}
                    onClick={() => setFilmeModal(f)}
                  >
                    <div className={styles.thumb} style={{ background: f.cor }}>
                      <span className={styles.thumbEmoji}>{f.emoji}</span>
                      <div className={styles.thumbOverlay}>▶</div>
                      <span className={styles.classifBadge}>{f.classificacao}</span>
                    </div>
                    <div className={styles.cardInfo}>
                      <p className={styles.cardTitle}>{f.titulo}</p>
                      <div className={styles.cardMeta}>
                        <span className={styles.match}>{matchPct[f.id]}%</span>
                        <span>{fmtDur(f.duracao)}</span>
                      </div>
                      <p className={styles.cardHora}>🕐 {fmtHora(f.horario)}</p>
                      <div className={styles.cardBtns}>
                        <button
                          className={`${styles.mic} ${styles.micRed}`}
                          onClick={e => { e.stopPropagation(); setFilmeModal(f); }}
                          title="Comprar"
                        >▶</button>
                        <button className={styles.mic} title="Lista">+</button>
                        <button className={styles.mic} title="Avaliar">👍</button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {filmeModal && (
        <SeatModal
          filme={filmeModal}
          onClose={() => setFilmeModal(null)}
          onSuccess={msg => show(msg, 'ok')}
        />
      )}

      <Toast toast={toast} />
    </div>
  );
}