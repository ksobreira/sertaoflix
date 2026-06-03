// ─────────────────────────────────────────────────────────────
//  MOCK DATA — substitua pelas chamadas reais ao backend
//  Exemplo: export const getFilmes = () => api.get('/filmes')
// ─────────────────────────────────────────────────────────────

export const FILMES = [
  {
    id: 1,
    titulo: 'O Auto da Compadecida 3',
    sinopse: 'Novas aventuras de Chicó e João Grilo no sertão nordestino.',
    duracao: 110,
    classificacao: '12',
    valor: 25,
    horario: new Date(Date.now() + 86400000).toISOString(),
    cinema: 'SertãoFlix Central',
    tipo_sala: 'IMAX',
    numero_sala: 1,
    emoji: '🤠',
    cor: '#8B1A1A',
  },
  {
    id: 2,
    titulo: 'Sertão Interestelar',
    sinopse: 'Um agricultor do sertão viaja pelo espaço em busca de um novo lar para a humanidade.',
    duracao: 145,
    classificacao: 'Livre',
    valor: 30,
    horario: new Date(Date.now() + 90000000).toISOString(),
    cinema: 'SertãoFlix Norte',
    tipo_sala: '3D',
    numero_sala: 2,
    emoji: '🌵',
    cor: '#1A4A8B',
  },
  {
    id: 3,
    titulo: 'Cangaço de Sangue',
    sinopse: 'A história dramática de um bando do cangaço que atravessa o sertão.',
    duracao: 125,
    classificacao: '16',
    valor: 22,
    horario: new Date(Date.now() + 95000000).toISOString(),
    cinema: 'SertãoFlix Sul',
    tipo_sala: 'Convencional',
    numero_sala: 1,
    emoji: '🗡️',
    cor: '#4A1A1A',
  },
  {
    id: 4,
    titulo: 'As Risadas da Seca',
    sinopse: 'Comédia romântica no interior do Nordeste.',
    duracao: 95,
    classificacao: 'Livre',
    valor: 18,
    horario: new Date(Date.now() + 100000000).toISOString(),
    cinema: 'SertãoFlix Sertão',
    tipo_sala: 'VIP',
    numero_sala: 3,
    emoji: '😂',
    cor: '#1A6B1A',
  },
  {
    id: 5,
    titulo: 'Mistério na Caatinga',
    sinopse: 'Investigadores buscam uma relíquia desaparecida na caatinga.',
    duracao: 115,
    classificacao: '14',
    valor: 20,
    horario: new Date(Date.now() + 105000000).toISOString(),
    cinema: 'SertãoFlix Praia',
    tipo_sala: '4DX',
    numero_sala: 2,
    emoji: '🔍',
    cor: '#1A3A6B',
  },
];

export const ASSENTOS_OCUPADOS = {
  1: ['A1', 'A2', 'B3', 'C5'],
  2: ['A1', 'C2', 'D4'],
  3: ['B1', 'B2'],
  4: ['A1', 'A2', 'A3', 'A4'],
  5: [],
};

export const PERFIS = [
  { id: 1, nome: 'João',    emoji: '🤠', cor: '#8B1A1A' },
  { id: 2, nome: 'Maria',   emoji: '🌵', cor: '#1A4A8B' },
  { id: 3, nome: 'Kauam',   emoji: '🎬', cor: '#1A8B3A' },
  { id: 4, nome: 'Ricardo', emoji: '⭐', cor: '#8B6B1A' },
];

// ── Dashboard ──────────────────────────────────────────────────
export const STATS = {
  total_cinemas:   5,
  total_filmes:    5,
  total_clientes: 272,
  total_ingressos: 1361,
  receita_total:   31760,
};

export const FATURAMENTO = [
  { cinema: 'SertãoFlix Praia',   total_ingressos: 421, receita: 8420 },
  { cinema: 'SertãoFlix Norte',   total_ingressos: 287, receita: 8610 },
  { cinema: 'SertãoFlix Central', total_ingressos: 312, receita: 7800 },
  { cinema: 'SertãoFlix Sul',     total_ingressos: 198, receita: 4356 },
  { cinema: 'SertãoFlix Sertão',  total_ingressos: 143, receita: 2574 },
];

export const RANKING = [
  { titulo: 'Sertão Interestelar',     nota_media: 9.2, total_avaliacoes: 48, lucro: 30000000 },
  { titulo: 'O Auto da Compadecida 3', nota_media: 8.8, total_avaliacoes: 61, lucro: 20000000 },
  { titulo: 'As Risadas da Seca',      nota_media: 8.1, total_avaliacoes: 29, lucro:  2500000 },
  { titulo: 'Cangaço de Sangue',       nota_media: 7.6, total_avaliacoes: 35, lucro:  5000000 },
  { titulo: 'Mistério na Caatinga',    nota_media: 6.4, total_avaliacoes: 18, lucro:  -500000 },
];

export const FIDELIDADE = [
  { nivel: 'Bronze', total: 187, cor: '#cd7f32' },
  { nivel: 'Prata',  total: 64,  cor: '#aaaaaa' },
  { nivel: 'Ouro',   total: 21,  cor: '#e50914' },
];

export const OCUPACAO = [
  { cinema: 'SertãoFlix Praia',   numero_sala: 1, tipo: 'IMAX',         capacidade: 200, vendidos: 168, pct: 84 },
  { cinema: 'SertãoFlix Norte',   numero_sala: 2, tipo: '3D',           capacidade: 150, vendidos: 119, pct: 79 },
  { cinema: 'SertãoFlix Central', numero_sala: 1, tipo: 'IMAX',         capacidade: 200, vendidos: 143, pct: 72 },
  { cinema: 'SertãoFlix Sertão',  numero_sala: 3, tipo: 'VIP',          capacidade: 80,  vendidos: 52,  pct: 65 },
  { cinema: 'SertãoFlix Sul',     numero_sala: 1, tipo: 'Convencional', capacidade: 120, vendidos: 61,  pct: 51 },
];
