import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import styles from './Login.module.css';

export default function Login() {
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [erro,  setErro]  = useState('');
  const { login } = useAuth();
  const navigate  = useNavigate();

  function handleSubmit(e) {
    e.preventDefault();
    if (!email || !senha) { setErro('Preencha todos os campos.'); return; }
    setErro('');
    const destino = login(email, senha);
    navigate(destino === 'admin' ? '/dashboard' : '/perfis');
  }

  return (
    <div className={styles.page}>
      {/* grade decorativa */}
      <div className={styles.bg}>
        {Array.from({ length: 15 }, (_, i) => (
          <div key={i} className={styles.tile}>
            {['🌵','🤠','🎬','⭐','🔥','🎭','🎞️','🪗','🌾','🦅','🎠','🏜️','🎯','🎪','🌟'][i]}
          </div>
        ))}
      </div>

      <form className={styles.box} onSubmit={handleSubmit}>
        <div className={styles.logo}>SERTÃO<span>FLIX</span></div>
        <h2 className={styles.heading}>Entrar</h2>

        <div className={styles.field}>
          <label>E-mail</label>
          <input
            type="text" placeholder="nome@exemplo.com"
            value={email} onChange={e => setEmail(e.target.value)}
          />
        </div>

        <div className={styles.field}>
          <label>Senha</label>
          <input
            type="password" placeholder="••••••••"
            value={senha} onChange={e => setSenha(e.target.value)}
          />
        </div>

        {erro && <p className={styles.erro}>{erro}</p>}

        <button type="submit" className={styles.btn}>Entrar</button>

        <p className={styles.dica}>
          Admin: <code>admin@sertaoflix.com</code> / qualquer senha
        </p>
      </form>
    </div>
  );
}
