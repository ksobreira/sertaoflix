import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { getStats, getFaturamento, getRanking, getFidelidade, getOcupacao } from '../../services/api';
import styles from './Dashboard.module.css';

function fmtMoeda(v) {
  return 'R$ ' + Number(v || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 });
}

function KpiGrid({ stats }) {
  const items = [
    { label: 'Cinemas',       value: stats.total_cinemas },
    { label: 'Filmes',        value: stats.total_filmes },
    { label: 'Clientes',      value: stats.total_clientes },
    { label: 'Ingressos',     value: stats.total_ingressos },
    { label: 'Receita Total', value: fmtMoeda(stats.receita_total), small: true },
  ];
  return (
    <div className={styles.kpiGrid}>
      {items.map(k => (
        <div key={k.label} className={styles.kpi}>
          <p className={styles.kpiLabel}>{k.label}</p>
          <p className={`${styles.kpiVal} ${k.small ? styles.kpiSmall : ''}`}>{k.value}</p>
        </div>
      ))}
    </div>
  );
}

function TabelaFaturamento({ dados }) {
  const max = Math.max(...dados.map(d => d.receita), 1);
  return (
    <table className={styles.table}>
      <thead>
        <tr>
          <th>Cinema</th><th>Ingressos</th><th>Receita</th><th>Desempenho</th>
        </tr>
      </thead>
      <tbody>
        {dados.map(d => (
          <tr key={d.cinema}>
            <td>{d.cinema}</td>
            <td className={styles.mono}>{d.total_ingressos}</td>
            <td className={`${styles.mono} ${styles.green}`}>{fmtMoeda(d.receita)}</td>
            <td>
              <div className={styles.barWrap}>
                <div className={`${styles.barFill} ${styles.barGreen}`} style={{ width: `${(d.receita / max * 100).toFixed(0)}%` }} />
              </div>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function TabelaRanking({ dados }) {
  return (
    <table className={styles.table}>
      <thead>
        <tr>
          <th>#</th><th>Filme</th><th>Avaliações</th><th>Nota</th><th>Lucro</th>
        </tr>
      </thead>
      <tbody>
        {dados.map((d, i) => (
          <tr key={d.titulo}>
            <td className={`${styles.mono} ${styles.muted}`}>{i + 1}</td>
            <td>{d.titulo}</td>
            <td className={styles.mono}>{d.total_avaliacoes}</td>
            <td>
              <div className={styles.notaRow}>
                <span className={styles.nota}>{d.nota_media}</span>
                <div className={styles.barWrap} style={{ width: 80 }}>
                  <div className={styles.barFill} style={{ width: `${(d.nota_media / 10 * 100).toFixed(0)}%` }} />
                </div>
              </div>
            </td>
            <td className={`${styles.mono} ${d.lucro >= 0 ? styles.green : styles.red}`}>
              {fmtMoeda(d.lucro)}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function PizzaFidelidade({ dados }) {
  const total = dados.reduce((s, d) => s + d.total, 0) || 1;
  const CORES = { Bronze: '#cd7f32', Prata: '#aaaaaa', Ouro: '#f5c842' };
  let deg = 0;
  const segs = dados.map(d => {
    const pct = (d.total / total) * 100;
    const seg = `${CORES[d.nivel] || '#555'} ${deg.toFixed(1)}% ${(deg + pct).toFixed(1)}%`;
    deg += pct;
    return seg;
  });
  return (
    <div className={styles.pizzaRow}>
      <div className={styles.pizza} style={{ background: `conic-gradient(${segs.join(',')})` }} />
      <div className={styles.pizzaLeg}>
        {dados.map(d => (
          <div key={d.nivel} className={styles.pizzaItem}>
            <span className={styles.pizzaDot} style={{ background: CORES[d.nivel] || '#555' }} />
            <div>
              <strong>{d.nivel}</strong>
              <span className={styles.muted}> {d.total} ({(d.total / total * 100).toFixed(0)}%)</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function TabelaOcupacao({ dados }) {
  return (
    <table className={styles.table}>
      <thead>
        <tr>
          <th>Cinema</th><th>Sala</th><th>Tipo</th><th>Vendidos / Cap.</th><th>Ocupação</th>
        </tr>
      </thead>
      <tbody>
        {dados.map((d, i) => (
          <tr key={i}>
            <td>{d.cinema}</td>
            <td className={styles.mono}>Sala {d.numero_sala}</td>
            <td>{d.tipo}</td>
            <td className={styles.mono}>{d.vendidos} / {d.capacidade}</td>
            <td>
              <div className={styles.notaRow}>
                <div className={styles.barWrap}>
                  <div
                    className={`${styles.barFill} ${d.pct >= 70 ? styles.barGreen : d.pct < 40 ? styles.barRed : ''}`}
                    style={{ width: `${d.pct}%` }}
                  />
                </div>
                <span className={`${styles.mono} ${styles.muted}`} style={{ fontSize: '.72rem' }}>
                  {d.pct}%
                </span>
              </div>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default function Dashboard() {
  const { logout } = useAuth();
  const navigate   = useNavigate();

  const [stats,       setStats]       = useState(null);
  const [faturamento, setFaturamento] = useState([]);
  const [ranking,     setRanking]     = useState([]);
  const [fidelidade,  setFidelidade]  = useState([]);
  const [ocupacao,    setOcupacao]    = useState([]);

  useEffect(() => {
    getStats().then(setStats);
    getFaturamento().then(setFaturamento);
    getRanking().then(setRanking);
    getFidelidade().then(setFidelidade);
    getOcupacao().then(setOcupacao);
  }, []);

  return (
    <div className={styles.page}>

      <nav className={styles.nav}>
        <div className={styles.logo}>SERTÃO<span>FLIX</span></div>
        <div className={styles.navTabs}>
          <button className={styles.navTab} onClick={() => navigate('/home')}>🎬 Em Cartaz</button>
          <button className={`${styles.navTab} ${styles.navTabActive}`}>📊 Dashboard</button>
          <button className={styles.navTab} onClick={() => { logout(); navigate('/'); }}>Sair</button>
        </div>
      </nav>

      <div className={styles.dashHeader}>
        <h1 className={styles.dashTitle}>PAINEL <em>GERENCIAL</em></h1>
        <p className={styles.dashSub}>Visão geral do sistema SertãoFlix</p>
      </div>

      {!stats ? (
        <div className={styles.loading}>
          <div className={styles.spinner} />
          Carregando dados...
        </div>
      ) : (
        <>
          <KpiGrid stats={stats} />

          <div className={styles.section}>
            <h2 className={styles.sectionTitle}>💰 FATURAMENTO POR CINEMA</h2>
            <TabelaFaturamento dados={faturamento} />
          </div>

          <div className={styles.section}>
            <h2 className={styles.sectionTitle}>⭐ RANKING DE FILMES</h2>
            <TabelaRanking dados={ranking} />
          </div>

          <div className={styles.twoCol}>
            <div className={styles.section}>
              <h2 className={styles.sectionTitle}>🏆 PROGRAMA DE FIDELIDADE</h2>
              <PizzaFidelidade dados={fidelidade} />
            </div>
            <div className={styles.section}>
              <h2 className={styles.sectionTitle}>🪑 OCUPAÇÃO DAS SALAS</h2>
              <TabelaOcupacao dados={ocupacao} />
            </div>
          </div>
        </>
      )}
    </div>
  );
}