// ─────────────────────────────────────────────────────────────
//  API SERVICE
//  Quando o backend estiver pronto, troque cada função por:
//    const res = await fetch(`${BASE_URL}/rota`)
//    return res.json()
// ─────────────────────────────────────────────────────────────

import {
  FILMES, ASSENTOS_OCUPADOS, STATS,
  FATURAMENTO, RANKING, FIDELIDADE, OCUPACAO,
} from './mock';

// Simula latência de rede durante desenvolvimento
const delay = (ms = 300) => new Promise(r => setTimeout(r, ms));

// ── Usuário ────────────────────────────────────────────────────
export async function getFilmes() {
  await delay();
  return FILMES;
  // BACKEND: return fetch('/api/filmes').then(r => r.json())
}

export async function getAssentos(sessaoId) {
  await delay(150);
  return ASSENTOS_OCUPADOS[sessaoId] || [];
  // BACKEND: return fetch(`/api/assentos/${sessaoId}`).then(r => r.json())
}

export async function comprarIngresso({ valor, assento, id_sessao, tipo_desconto }) {
  await delay(500);
  return { success: true, id_ingresso: Math.floor(Math.random() * 9000) + 1000 };
  // BACKEND:
  // return fetch('/api/ingresso', {
  //   method: 'POST',
  //   headers: { 'Content-Type': 'application/json' },
  //   body: JSON.stringify({ valor, assento, id_sessao, tipo_desconto }),
  // }).then(r => r.json())
}

// ── Admin / Dashboard ──────────────────────────────────────────
export async function getStats() {
  await delay();
  return STATS;
  // BACKEND: return fetch('/api/dashboard/stats').then(r => r.json())
}

export async function getFaturamento() {
  await delay();
  return FATURAMENTO;
  // BACKEND: return fetch('/api/dashboard/faturamento').then(r => r.json())
}

export async function getRanking() {
  await delay();
  return RANKING;
  // BACKEND: return fetch('/api/dashboard/ranking').then(r => r.json())
}

export async function getFidelidade() {
  await delay();
  return FIDELIDADE;
  // BACKEND: return fetch('/api/dashboard/clientes').then(r => r.json())
}

export async function getOcupacao() {
  await delay();
  return OCUPACAO;
  // BACKEND: return fetch('/api/dashboard/ocupacao').then(r => r.json())
}
