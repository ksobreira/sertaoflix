import pandas as pd
import re
import random
import mysql.connector

# ==============================================================================
# 1. CONFIGURAÇÃO DA CONEXÃO E PARÂMETROS EXPLICITOS DE CORTE
# ==============================================================================
CONFIG_BANCO = {
    "host": "localhost",          
    "user": "root",               
    "password": "SUA_SENHA_AQUI", # COLOQUE A SUA SENHA DO WORKBENCH AQUI
    "database": "sertaoflix"      
}

# --- MODIFIQUE O ANO AQUI SE DESEJAR ---
ANO_FILMES = 2020  

# Se True, traz APENAS o ano acima. 
# Como pediu para trazer os outros anos por causa das views, deixamos False.
FILTRAR_POR_ANO_ESTRITO = False  

# Regra de corte para popular as Views com relevância
MINIMO_VOTOS_RELEVANCIA = 50  

# Semente aleatória para consistência de testes
random.seed(42)

ARQUIVO_TMDB = "TMDB_movie.csv"
ARQUIVO_NETFLIX = "netflix_titles.csv"
ARQUIVO_MOVIES_CSV = "movies.csv"
ARQUIVO_AMAZON = "amazon_prime_titles.csv"
ARQUIVO_DISNEY = "disney_plus_titles.csv"
ARQUIVO_HULU = "hulu_titles.csv"

# Dicionário global de enriquecimento
lookup_filmes = {}

def adicionar_ao_lookup(caminho_ficheiro, separador, col_titulo, col_diretor, col_elenco, col_classificacao):
    print(f"A processar e indexar: {caminho_ficheiro}...")
    try:
        df_fonte = pd.read_csv(caminho_ficheiro, sep=separador)
        df_fonte = df_fonte.astype(object).fillna('')
        for _, row in df_fonte.iterrows():
            t_busca = str(row.get(col_titulo, '')).lower().strip()
            if not t_busca: continue
            
            director = str(row.get(col_diretor, '')).strip()
            elenco = str(row.get(col_elenco, '')).strip()
            classificacao = str(row.get(col_classificacao, '')).strip()
            
            if t_busca in lookup_filmes:
                if not lookup_filmes[t_busca]['director'] and director:
                    lookup_filmes[t_busca]['director'] = director
                if not lookup_filmes[t_busca]['rating'] and classificacao:
                    lookup_filmes[t_busca]['rating'] = classificacao
                if elenco:
                    elenco_existente = lookup_filmes[t_busca]['cast']
                    if elenco not in elenco_existente:
                        lookup_filmes[t_busca]['cast'] = f"{elenco_existente}, {elenco}" if elenco_existente else elenco
            else:
                lookup_filmes[t_busca] = {
                    'director': director,
                    'cast': elenco,
                    'rating': classificacao if classificacao else 'Livre'
                }
    except FileNotFoundError:
        print(f"Aviso: O ficheiro '{caminho_ficheiro}' não foi encontrado. A ignorar...")

# Executa o mapeamento de metadados das plataformas
adicionar_ao_lookup(ARQUIVO_NETFLIX, "\t", "Titulo", "director", "cast", "Classificacao_indicativa")
adicionar_ao_lookup(ARQUIVO_MOVIES_CSV, ",", "name", "director", "star", "rating")
adicionar_ao_lookup(ARQUIVO_AMAZON, ",", "title", "director", "cast", "rating")
adicionar_ao_lookup(ARQUIVO_DISNEY, ",", "title", "director", "cast", "rating")
adicionar_ao_lookup(ARQUIVO_HULU, ",", "title", "director", "cast", "rating")

# 2. Carregar estruturalmente o TMDB de 600MB
print("\nA carregar colunas estruturais do TMDB...")
colunas_tmdb = ['id', 'title', 'overview', 'runtime', 'release_date', 'budget', 'revenue', 'poster_path', 'vote_average', 'vote_count', 'genres']

try:
    df_tmdb = pd.read_csv(ARQUIVO_TMDB, usecols=colunas_tmdb)
except FileNotFoundError:
    print(f"Erro Critico: O ficheiro '{ARQUIVO_TMDB}' não foi encontrado.")
    exit()

df_tmdb['titulo_busca'] = df_tmdb['title'].astype(str).str.lower().str.strip()
df_tmdb = df_tmdb.drop_duplicates(subset=['titulo_busca'])
df_tmdb['id'] = pd.to_numeric(df_tmdb['id'], errors='coerce')
df_tmdb['budget'] = pd.to_numeric(df_tmdb['budget'], errors='coerce')
df_tmdb['revenue'] = pd.to_numeric(df_tmdb['revenue'], errors='coerce')
df_tmdb['runtime'] = pd.to_numeric(df_tmdb['runtime'], errors='coerce')
df_tmdb['vote_average'] = pd.to_numeric(df_tmdb['vote_average'], errors='coerce')
df_tmdb['vote_count'] = pd.to_numeric(df_tmdb['vote_count'], errors='coerce')
df_tmdb = df_tmdb.dropna(subset=['id', 'vote_count'])

# --- MÁGICA DA FILTRAGEM DE RELEVÂNCIA ADAPTADA ---
print(f"Quantidade original do TMDB: {len(df_tmdb)} filmes.")
df_tmdb['release_date_str'] = df_tmdb['release_date'].astype(str)

if FILTRAR_POR_ANO_ESTRITO:
    df_tmdb = df_tmdb[df_tmdb['release_date_str'].str.contains(str(ANO_FILMES), na=False)]
    df_tmdb = df_tmdb[df_tmdb['vote_count'] >= MINIMO_VOTOS_RELEVANCIA]
else:
    # REGRA: Mantém o ano alvo OU qualquer outro filme com mais de 50 votos para popular as views
    df_tmdb = df_tmdb[(df_tmdb['release_date_str'].str.contains(str(ANO_FILMES), na=False)) | (df_tmdb['vote_count'] >= MINIMO_VOTOS_RELEVANCIA)]

# Ordena por relevância e extrai a fatia dos top 30% resultantes
df_tmdb = df_tmdb.sort_values(by='vote_count', ascending=False)
df_tmdb = df_tmdb.head(int(len(df_tmdb) * 0.30))
print(f"Quantidade de filmes finais que subiram para o Banco: {len(df_tmdb)}")

# Pools de suporte para geração de textos aleatórios
comentarios_pool = [
    "Excelente filme! Roteiro incrivel e final surpreendente.",
    "Bons efeitos visuais e atuacao solida do elenco principal.",
    "Um classico obrigatorio, vale muito a pena assistir.",
    "Prende a atencao do inicio ao fim, recomendo fortemente.",
    "Muito bem produzido, superou bastante as minhas expectativas.",
    "Uma obra-prima cinematografica com excelente trilha sonora."
]

def gerar_lista_assentos(quantidade):
    assentos = set()
    while len(assentos) < quantidade:
        fila = random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'])
        num = random.randint(1, 12)
        assentos.add(f"{fila}{num}")
    return list(assentos)

# Dicionários e contadores únicos relacionais
map_generos = {}
map_elenco = {}
gen_id_counter = 100
elenco_id_counter = 100

# ==============================================================================
# 3. LIGAÇÃO DIRETA E OPERAÇÕES DINÂMICAS NO BANCO DE DADOS
# ==============================================================================
print("\nA tentar estabelecer conexao direta com o servidor MySQL...")
try:
    conexao = mysql.connector.connect(**CONFIG_BANCO)
    cursor = conexao.cursor()
    print("Conexao direta estabelecida com sucesso!")
    
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    
    # [RESET] Limpeza completa das tabelas afetadas para evitar duplicações
    print("\n[RESET] Limpando tabelas para a nova carga dinamica...")
    tabelas_limpar = ['genero_filme', 'elenco_filme', 'Avalia_filme', 'ingresso_cliente', 'ingresso', 'avalia', 'funcionarios', 'salas', 'sessao', 'filme', 'cliente', 'cinema', 'Telefone', 'Endereço']
    for t in tabelas_limpar:
        cursor.execute(f"DELETE FROM `{t}`;")
    conexao.commit()
    
    # --- ETAPA A: INSERÇÃO DE CLIENTES BASE (20 Clientes Simulados) ---
    query_cliente = "INSERT INTO `cliente` (`id_Cliente`, `Nome`, `Nacimento`, `Nivel_fidelidade`, `Email`, `Total_ingresso`) VALUES (%s, %s, %s, %s, %s, %s);"
    lista_clientes = []
    nomes_pool = ["Joao Silva", "Maria Oliveira", "Pedro Santos", "Ana Costa", "Carlos Souza", "Beatriz Lima", "Lucas Mendes", "Juliana Rocha", "Fernando Alencar", "Ricardo Sousa", "Gabriela Cruz", "Thiago Reis", "Camila Viana", "Bruno Dias", "Amanda Melo", "Rafael Guedes", "Patricia Borges", "Rodrigo Nogueira", "Larissa Freitas", "Marcelo Neto"]
    for idx, nome in enumerate(nomes_pool, start=1):
        lista_clientes.append((idx, nome, f"{random.randint(1980, 2005)}-03-15", random.choice(['Bronze', 'Prata', 'Ouro']), f"{nome.lower().replace(' ', '.')}@email.com", random.randint(1, 20)))
    cursor.executemany(query_cliente, lista_clientes)

    # --- ETAPA B: CINEMAS E SALAS DINÂMICAS (REGRA: Entre 2 e 5 salas por cinema) ---
    print("A estruturar cinemas e definicao dinamica de salas...")
    cinemas_base = [
        (1, 'SertaoFlix Central', '12345678000101', '88999991111', 'Rua Central, 100'),
        (2, 'SertaoFlix Norte', '12345678000202', '88999992222', 'Av. Norte, 250'),
        (3, 'SertaoFlix Sul', '12345678000303', '88999993333', 'Praca do Sul, 15'),
        (4, 'SertaoFlix Sertao', '12345678000404', '88999994444', 'Rodovia do Sol, Km 5'),
        (5, 'SertaoFlix Praia', '12345678000505', '88999995555', 'Av. Beira Mar, 1010')
    ]
    
    salas_map = []
    lista_cinemas_insert = []
    id_sala_global = 1
    id_sessao_global = 1

    for c_id, c_nome, c_cnpj, c_tel, c_end in cinemas_base:
        qnt_salas = random.randint(2, 5) # REGRA: Entre 2 e 5 salas por cinema
        capacidade_total_cinema = 0
        
        for num_sala in range(1, qnt_salas + 1):
            tamanho_sala = random.randint(100, 200)
            capacidade_total_cinema += tamanho_sala
            
            salas_map.append({
                "id_Salas": id_sala_global,
                "Numero_Sala": num_sala,
                "Tipo": random.choice(['IMAX', '3D', 'VIP', 'Convencional', 'MacroXE']),
                "Tamanho": tamanho_sala,
                "Sistema_som": random.choice(['Dolby Atmos', 'Dolby Digital', 'DTS:X', 'Stereo']),
                "Projecao": random.choice(['Laser 4K', 'Digital', 'Laser', '4K']),
                "Fileiras": random.randint(10, 15),
                "Status": 'Ativa',
                "cinema_id_Cinema": c_id,
                "primeiro_id_sessao": id_sessao_global
            })
            id_sala_global += 1
            id_sessao_global += 5 # Reserva blocos de 5 sessões obrigatórias por sala
            
        lista_cinemas_insert.append((c_id, c_nome, c_cnpj, c_tel, c_end, qnt_salas, capacidade_total_cinema, 1, random.choice([0,1])))
    
    query_cinema = "INSERT INTO `cinema` (`id_Cinema`, `Nome`, `CNPJ`, `Telefone`, `Endereco`, `Qnt_salas`, `Capacidade_total`, `Acessibilidade_PCD`, `VIP`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"
    cursor.executemany(query_cinema, lista_cinemas_insert)

    # --- ETAPA C: CÁLCULO DE SESSÕES (REGRA: Filme + 15 min) E OCUPAÇÃO DE INGRESSOS (50% a 90%) ---
    print("A planejar sessoes dinamicas e lotes de ingressos comprados...")
    lista_filmes_tmdb = df_tmdb.to_dict('records')
    
    sessoes_insert_lista = []
    ingressos_insert_lote = []
    ingresso_cliente_lote = []
    
    id_ingresso_counter = 1
    id_avalia_counter = 1
    
    lista_avalia_lote = []
    lista_avalia_filme_lote = []
    
    filme_sessao_link_map = {}
    lote_gen_filme = []
    lote_elenco_filme = []
    lote_filmes = []

    # Montagem da árvore estrutural correlacionada
    for sala in salas_map:
        sala_cap = sala['Tamanho']
        sessao_inicial = sala['primeiro_id_sessao']
        
        # REGRA: Ao menos 5 sessões por sala
        for s_offset in range(5):
            curr_sessao_id = sessao_inicial + s_offset
            
            # Sorteia um filme do pool para rodar nesta sessão
            f_escolhido = random.choice(lista_filmes_tmdb)
            f_id = int(f_escolhido['id'])
            
            runtime_f = int(f_escolhido['runtime']) if f_escolhido['runtime'] != '' and not pd.isna(f_escolhido['runtime']) else 120
            if runtime_f <= 0: runtime_f = 120
            
            # REGRA: Duração da sessão = Tempo de duração do filme + 15 minutos
            duracao_sessao = runtime_f + 15 
            
            horario_sessao = f"2026-06-{10 + s_offset} {14 + s_offset}:00:00"
            val_ing = random.choice([25, 30, 40])
            desc_ing = random.choice([0, 5])
            
            sessoes_insert_lista.append((curr_sessao_id, duracao_sessao, horario_sessao, val_ing, desc_ing))
            
            if f_id not in filme_sessao_link_map:
                filme_sessao_link_map[f_id] = curr_sessao_id
                
            # REGRA: Cada sala/sessão possui entre 50% e 90% de ingressos vendidos
            pct_venda = random.uniform(0.50, 0.90)
            qnt_ingressos_vender = int(sala_cap * pct_venda)
            
            assentos_gerados = gerar_lista_assentos(qnt_ingressos_vender)
            for assento in assentos_gerados:
                c_sorteado = random.randint(1, len(nomes_pool))
                ingressos_insert_lote.append((id_ingresso_counter, val_ing, assento, f"2026-06-02 {random.randint(10,21)}:15:00", c_sorteado, curr_sessao_id, 'Nenhum' if desc_ing==0 else 'Estudante'))
                ingresso_cliente_lote.append((id_ingresso_counter, c_sorteado))
                id_ingresso_counter += 1

    # --- ETAPA D: PROCESSAMENTO DOS FILMES E CRIAÇÃO DE CRÍTICAS OBRIGATÓRIAS ---
    print("A amarrar integridade referencial e avaliacoes obrigatorias por filme...")
    total_sessoes_geradas = id_sessao_global - 1

    for idx, row in enumerate(lista_filmes_tmdb):
        id_filme = int(row['id'])
        titulo = str(row['title']).strip()
        sinopse = str(row['overview']).strip()
        duracao = int(row['runtime']) if row['runtime'] != '' and not pd.isna(row['runtime']) else 120
        
        data_raw = str(row['release_date'])
        ano_match = re.search(r'\d{4}', data_raw)
        data_formatada = f"{ano_match.group(0)}-01-01" if ano_match else "2026-01-01"
        
        orcamento = row['budget']
        if pd.isna(orcamento) or orcamento < 1.00: orcamento = 1500000.00
        bilheteria = row['revenue']
        if pd.isna(bilheteria) or bilheteria < 0: bilheteria = 3000000.00

        poster = str(row['poster_path']).strip() if not pd.isna(row['poster_path']) else ''
        nota_media = float(row['vote_average']) if not pd.isna(row['vote_average']) else 0.0
        total_votos = int(row['vote_count']) if not pd.isna(row['vote_count']) else 0
        
        t_busca = row['titulo_busca']
        dados_enriquecidos = lookup_filmes.get(t_busca, {'director': '', 'cast': '', 'rating': 'Livre'})
        
        classificacao = dados_enriquecidos['rating']
        if not classificacao or classificacao == 'nan': classificacao = 'Livre'
        
        # Mapeamento do Diretor
        diretor_raw = dados_enriquecidos['director']
        if diretor_raw and diretor_raw != 'nan':
            diretor_principal = [d.strip() for d in diretor_raw.split(',') if d.strip()][0]
            if diretor_principal not in map_elenco:
                map_elenco[diretor_principal] = (elenco_id_counter, 'Diretor')
                elenco_id_counter += 1
            id_diretor_elenco = map_elenco[diretor_principal][0]
            lote_elenco_filme.append((id_diretor_elenco, id_filme))
        else:
            id_diretor_elenco = None  
            
        # Determina a sessão vinculada ou calcula uma ciclicamente dentro do range gerado
        sessao_final_id = filme_sessao_link_map.get(id_filme, (idx % total_sessoes_geradas) + 1)
        
        lote_filmes.append((
            id_filme, titulo, sinopse, duracao, data_formatada, 
            round(orcamento, 2), round(bilheteria, 2), classificacao, id_diretor_elenco, sessao_final_id, 
            poster, round(nota_media, 1), total_votos
        ))
        
        # REGRA: Cada filme cadastrado deve possuir obrigatoriamente ao menos uma avaliacao
        c_sorteado_avalia = random.randint(1, len(nomes_pool))
        lista_avalia_lote.append((id_avalia_counter, round(random.uniform(7.0, 10.0), 1), random.choice(comentarios_pool), c_sorteado_avalia))
        lista_avalia_filme_lote.append((id_avalia_counter, id_filme))
        id_avalia_counter += 1

        # Gêneros Relacionais (N:N)
        generos_raw = str(row['genres']).replace('|', ',')
        if generos_raw and generos_raw != 'nan':
            generos_lista = [g.strip() for g in generos_raw.split(',') if g.strip()]
            for g in generos_lista:
                if g not in map_generos:
                    map_generos[g] = gen_id_counter
                    gen_id_counter += 1
                lote_gen_filme.append((map_generos[g], id_filme))

        # Elenco Relacional (N:N)
        elenco_raw = dados_enriquecidos['cast']
        if elenco_raw and elenco_raw != 'nan':
            elenco_lista = [a.strip() for a in elenco_raw.split(',') if a.strip()]
            for a in elenco_lista:
                if a not in map_elenco:
                    map_elenco[a] = (elenco_id_counter, 'Ator')
                    elenco_id_counter += 1
                lote_elenco_filme.append((map_elenco[a][0], id_filme))

    # --- ETAPA E: PERSISTÊNCIA COMPLETA DOS DADOS (BULK INSERTS EM ORDEM) ---
    print("\nA enviar sessoes geradas...")
    query_sessao = "INSERT INTO `sessao` (`id_Sessao`, `Duracao_da_sala`, `Horario`, `Valor_Ingresso`, `Desconto`) VALUES (%s, %s, %s, %s, %s);"
    cursor.executemany(query_sessao, sessoes_insert_lista)
    conexao.commit()

    print("A enviar salas calculadas...")
    query_sala = "INSERT INTO `salas` (`id_Salas`, `Numero_Sala`, `Tipo`, `Tamanho`, `Sistema_som`, `Projecao`, `Fileiras`, `Status`, `sessao_id_Sessao`, `cinema_id_Cinema`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
    lista_salas_insert = [(s['id_Salas'], s['Numero_Sala'], s['Tipo'], s['Tamanho'], s['Sistema_som'], s['Projecao'], s['Fileiras'], s['Status'], s['primeiro_id_sessao'], s['cinema_id_Cinema']) for s in salas_map]
    cursor.executemany(query_sala, lista_salas_insert)
    conexao.commit()

    print("A enviar catalogo principal de filmes filtrados...")
    query_filme = "INSERT IGNORE INTO `filme` (`id_FIlme`, `Titulo`, `Sinopse`, `Duracao_min`, `data_lancamento`, `Orcamento`, `Bilheteria`, `Classificacao_indicativa`, `id_Elenco`, `sessao_id_Sessao`, `Poster_path`, `Nota_media`, `Total_votos`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
    
    # Executa a quebra de inserção em lotes de 5000 registros para evitar estouro de pacotes do MySQL
    TAMANHO_LOTE = 5000
    for i in range(0, len(lote_filmes), TAMANHO_LOTE):
        cursor.executemany(query_filme, lote_filmes[i:i+TAMANHO_LOTE])
        conexao.commit()

    print(f"A enviar bilheteria e ingressos comprados ({id_ingresso_counter - 1} registros)...")
    query_ingresso = "INSERT INTO `ingresso` (`id_Ingresso`, `Valor`, `Assento`, `Data_de_compra`, `id_cliente`, `id_sessao`, `Tipo_Desconto`) VALUES (%s, %s, %s, %s, %s, %s, %s);"
    for i in range(0, len(ingressos_insert_lote), TAMANHO_LOTE):
        cursor.executemany(query_ingresso, ingressos_insert_lote[i:i+TAMANHO_LOTE])
    
    query_ing_cli = "INSERT INTO `ingresso_cliente` (`ingresso_id_Ingresso`, `cliente_id_Cliente`) VALUES (%s, %s);"
    for i in range(0, len(ingresso_cliente_lote), TAMANHO_LOTE):
        cursor.executemany(query_ing_cli, ingresso_cliente_lote[i:i+TAMANHO_LOTE])
    conexao.commit()

    print("A enviar críticas e avaliacoes obrigatorias de filmes...")
    query_avalia = "INSERT INTO `avalia` (`id_Avalia`, `Nota`, `Comentario`, `cliente_id_Cliente`) VALUES (%s, %s, %s, %s);"
    cursor.executemany(query_avalia, lista_avalia_lote)
    query_avalia_filme = "INSERT INTO `Avalia_filme` (`Avalia_id_Avalia`, `filme_id_FIlme`) VALUES (%s, %s);"
    cursor.executemany(query_avalia_filme, lista_avalia_filme_lote)
    conexao.commit()

    print("A enviar tabelas intermediarias relacionais N:N...")
    for i in range(0, len(lote_gen_filme), TAMANHO_LOTE):
        cursor.executemany(query_gen_filme, lote_gen_filme[i:i+TAMANHO_LOTE])
    for i in range(0, len(lote_elenco_filme), TAMANHO_LOTE):
        cursor.executemany(query_elenco_filme, lote_elenco_filme[i:i+TAMANHO_LOTE])
    conexao.commit()

    # --- ETAPA F: INSERÇÃO DOS CATÁLOGOS BASE E CORPO DE FUNCIONÁRIOS (COM HISTÓRICO) ---
    print("A finalizar envio de catalogos de suporte de gêneros e elencos...")
    query_base_genero = "INSERT IGNORE INTO `genero` (`id_Genero`, `id_Filme`, `Genero`) VALUES (%s, %s, %s);"
    lista_base_genero = [(gid, 0, gen) for gen, gid in map_generos.items()]
    cursor.executemany(query_base_genero, lista_base_genero)
    
    query_base_elenco = "INSERT IGNORE INTO `elenco` (`id_Elenco`, `Nome`, `Nascimento`, `Cargo`) VALUES (%s, %s, %s, %s);"
    lista_base_elenco = [(eid, nome, '1980-01-01', cargo) for nome, (eid, cargo) in map_elenco.items()]
    cursor.executemany(query_base_elenco, lista_base_elenco)

    print("A cadastrar corpo de funcionários corporativos e de historico...")
    query_funcionarios = "INSERT INTO `funcionarios` (`id_Funcionarios`, `Nome`, `Nascimento`, `Funcao`, `Cinema`, `Genero`, `Salario`, `cinema_id_Cinema`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"
    funcionarios_dados = [
        (1, 'Lucas Lima', '1994-03-10', 'Gerente', 'SertaoFlix Central', 1, 4500, 1),
        (2, 'Beatriz Reis', '2000-09-25', 'Atendente', 'SertaoFlix Norte', 2, 1800, 2),
        (3, 'Ricardo Rocha', '1988-12-05', 'Tecnico de Projecao', 'SertaoFlix Sul', 1, 3200, 3),
        (4, 'Juliana Mendes', '2003-06-14', 'Bilheteira', 'SertaoFlix Sertao', 2, 1700, 4),
        (5, 'Fernando Alencar', '1997-01-30', 'Supervisor', 'SertaoFlix Praia', 1, 2800, 5),
        # REGRA: Dois funcionários adicionais de histórico da empresa criados abaixo
        (6, 'Carlos Antunes (Historico)', '1975-04-12', 'Ex-Diretor Operacional', 'SertaoFlix Central', 1, 0, 1),
        (7, 'Mariana Costa (Historico)', '1982-08-19', 'Ex-Supervisora Regional', 'SertaoFlix Praia', 2, 0, 5)
    ]
    cursor.executemany(query_funcionarios, funcionarios_dados)

    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    conexao.commit()
    print("\n[SUCESSO COMPLETO] O banco de dados foi limpo e inteiramente populado de forma dinamica!")

except mysql.connector.Error as erro:
    print(f"\nErro durante as operacoes no MySQL: {erro}")
    if 'conexao' in locals() and conexao.is_connected():
        conexao.rollback() 

finally:
    if 'conexao' in locals() and conexao.is_connected():
        cursor.close()
        conexao.close()
        print("Conexao com o MySQL encerrada com seguranca.")