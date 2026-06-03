import pandas as pd
import re
import mysql.connector

# ==============================================================================
# 1. CONFIGURAÇÃO DA CONEXÃO COM O SEU BANCO DE DADOS
# ==============================================================================
CONFIG_BANCO = {
    "host": "localhost",          
    "user": "root",               
    "password": "12345678", # COLOQUE A SUA SENHA DO WORKBENCH AQUI
    "database": "sertaoflix"      
}

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

# Executa o mapeamento de metadados das 5 plataformas
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

# Remove linhas sem ID ou sem contagem de votos válida
df_tmdb = df_tmdb.dropna(subset=['id', 'vote_count'])

# --- CORTE DE RELEVÂNCIA (MANTER OS 30% MELHORES COM NO MÍNIMO 100 VOTOS) ---
MINIMO_VOTOS_RELEVANCIA = 50 
df_tmdb = df_tmdb[df_tmdb['vote_count'] >= MINIMO_VOTOS_RELEVANCIA]
#df_tmdb = df_tmdb.sort_values(by='vote_count', ascending=False)
#df_tmdb = df_tmdb.head(int(len(df_tmdb) * 0.30))
print(f"Quantidade final após o corte dos top 30%: {len(df_tmdb)} filmes.")

# Dicionários únicos para IDs relacionais das tabelas base
map_generos = {}
map_elenco = {}
gen_id_counter = 100
elenco_id_counter = 100

# ==============================================================================
# 3. LIGAÇÃO DIRETA E OPERAÇÕES NO BANCO DE DADOS
# ==============================================================================
print("\nA tentar estabelecer conexao direta com o servidor MySQL...")
try:
    conexao = mysql.connector.connect(**CONFIG_BANCO)
    cursor = conexao.cursor()
    print("Conexao direta estabelecida com sucesso!")
    
    # Desativa checagem de chaves para permitir modificações estruturais rápidas
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    
    # [RESET] Limpeza das tabelas antes da nova carga
    print("\n[RESET] Apagando filmes e relacionamentos antigos do banco de dados...")
    cursor.execute("DELETE FROM `genero_filme`;")
    cursor.execute("DELETE FROM `elenco_filme`;")
    cursor.execute("DELETE FROM `Avalia_filme`;")
    cursor.execute("DELETE FROM `filme`;")
    conexao.commit()
    print("[RESET] Tabelas limpas com sucesso. Pronto para a nova carga.")
    
    # --- QUERIES CORRIGIDAS DE ACORDO COM O SEU DDL ---
    # Alterado de id_Diretor para id_Ddiretor na tabela filme
    query_filme = """
    INSERT IGNORE INTO `filme` 
    (`id_Filme`, `Titulo`, `Sinopse`, `Duracao_min`, `data_lancamento`, `Orcamento`, `Bilheteria`, `Poster_path`, `Nota_media`, `Total_votos`, `Classificacao_indicativa`, `id_Elenco`, `sessao_id_Sessao`) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    # Corrigido os campos de relacionamento para bater com as minúsculas/maiúsculas do seu DDL
    query_gen_filme = "INSERT IGNORE INTO `genero_filme` (`genero_id_Genero`, `filme_id_Filme`) VALUES (%s, %s);"
    query_elenco_filme = "INSERT IGNORE INTO `elenco_filme` (`Elenco_id_Elenco`, `filme_id_Filme`) VALUES (%s, %s);"

    lote_filmes = []
    lote_gen_filme = []
    lote_elenco_filme = []
    TAMANHO_LOTE = 5000
    
    print("\nA processar e enviar lotes de dados diretamente ao banco...")
    counter = 0
    
    for index, row in df_tmdb.iterrows():
        id_Filme = int(row['id'])
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
        
        # --- CORREÇÃO DO DIRETOR (AGORA VAI PARA A TABELA ELENCO VIA ID_ELENCO) ---
        diretor_raw = dados_enriquecidos['director']
        if diretor_raw and diretor_raw != 'nan':
            diretor_principal = [d.strip() for d in diretor_raw.split(',') if d.strip()][0]
            if diretor_principal not in map_elenco:
                map_elenco[diretor_principal] = (elenco_id_counter, 'Diretor')
                elenco_id_counter += 1
            
            id_diretor_val = map_elenco[diretor_principal][0] # Esse é o id_Elenco dele
            
            # AMARRAÇÃO N:N: Vincula o diretor ao filme na tabela elenco_filme
            lote_elenco_filme.append((id_diretor_val, id_Filme))
        else:
            id_diretor_val = None  
            
        sessao_id = (counter % 5) + 1
        
        lote_filmes.append((
            id_Filme, titulo, sinopse, duracao, data_formatada, 
            round(orcamento, 2), round(bilheteria, 2), classificacao, id_diretor_val, sessao_id, 
            poster, round(nota_media, 1), total_votos
        ))
        
        # Gêneros Relacionais (N:N)
        generos_raw = str(row['genres']).replace('|', ',')
        if generos_raw and generos_raw != 'nan':
            generos_lista = [g.strip() for g in generos_raw.split(',') if g.strip()]
            for g in generos_lista:
                if g not in map_generos:
                    map_generos[g] = gen_id_counter
                    gen_id_counter += 1
                lote_gen_filme.append((map_generos[g], id_Filme))

        # Elenco Relacional (N:N - Atores)
        elenco_raw = dados_enriquecidos['cast']
        if elenco_raw and elenco_raw != 'nan':
            elenco_lista = [a.strip() for a in elenco_raw.split(',') if a.strip()]
            for a in elenco_lista:
                if a not in map_elenco:
                    map_elenco[a] = (elenco_id_counter, 'Ator')
                    elenco_id_counter += 1
                lote_elenco_filme.append((map_elenco[a][0], id_Filme))
        
        counter += 1
        
        if len(lote_filmes) >= TAMANHO_LOTE:
            cursor.executemany(query_filme, lote_filmes)
            cursor.executemany(query_gen_filme, lote_gen_filme)
            cursor.executemany(query_elenco_filme, lote_elenco_filme)
            conexao.commit()  
            lote_filmes, lote_gen_filme, lote_elenco_filme = [], [], []
            print(f"-> {counter} filmes enviados...")

    if lote_filmes:
        cursor.executemany(query_filme, lote_filmes)
    if lote_gen_filme:
        cursor.executemany(query_gen_filme, lote_gen_filme)
    if lote_elenco_filme:
        cursor.executemany(query_elenco_filme, lote_elenco_filme)
    conexao.commit()
    print(f"-> Envio da massa principal finalizado. Total: {counter} filmes.")

    # 4. INSERÇÃO MASSIVA NAS TABELAS DE SUPORTE (Gêneros e Elenco Unificados)
    print("\nA enviar catalogos base de suporte (generos e elenco)...")
    
    query_base_genero = "INSERT IGNORE INTO `genero` (`id_Genero`, `id_Filme`, `Genero`) VALUES (%s, %s, %s);"
    lista_base_genero = [(gid, 0, gen) for gen, gid in map_generos.items()]
    cursor.executemany(query_base_genero, lista_base_genero)
    
    # Aqui os Diretores e Atores entram juntos na tabela `elenco` usando a coluna `id_Elenco`
    query_base_elenco = "INSERT IGNORE INTO `elenco` (`id_Elenco`, `Nome`, `Nascimento`, `Cargo`) VALUES (%s, %s, %s, %s);"
    lista_base_elenco = [(eid, nome, '1980-01-01', cargo) for nome, (eid, cargo) in map_elenco.items()]
    cursor.executemany(query_base_elenco, lista_base_elenco)
    
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    conexao.commit()
    print("[SUCESSO GERAL] Todos os dados foram inseridos diretamente no banco MySQL!")

except mysql.connector.Error as erro:
    print(f"\nErro durante as operacoes no MySQL: {erro}")
    if 'conexao' in locals() and conexao.is_connected():
        conexao.rollback() 

finally:
    if 'conexao' in locals() and conexao.is_connected():
        cursor.close()
        conexao.close()
        print("Conexao com o MySQL encerrada com seguranca.")