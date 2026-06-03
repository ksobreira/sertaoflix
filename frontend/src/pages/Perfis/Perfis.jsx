import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { PERFIS } from '../../services/mock';
import styles from './Perfis.module.css';

export default function Perfis() {
  const { setPerfil } = useAuth();
  const navigate = useNavigate();

  function escolher(perfil) {
    setPerfil(perfil);
    navigate('/home');
  }

  return (
    <div className={styles.page}>
      <div className={styles.logo}>SERTÃO<span>FLIX</span></div>
      <h1 className={styles.titulo}>Quem está assistindo?</h1>

      <div className={styles.grid}>
        {PERFIS.map(p => (
          <div key={p.id} className={styles.item} onClick={() => escolher(p)}>
            <div className={styles.avatar} style={{ background: p.cor }}>
              {p.emoji}
            </div>
            <span className={styles.nome}>{p.nome}</span>
          </div>
        ))}
      </div>

      <button className={styles.gerenciar}>Gerenciar perfis</button>
    </div>
  );
}
