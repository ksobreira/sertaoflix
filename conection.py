import mysql.connector

try:
    # 1. Estabelecer a ligação com o servidor
    ligacao = mysql.connector.connect(
        host="localhost",          # Se o MySQL estiver na sua máquina
        user="root",               # O seu utilizador do MySQL
        password="12345678",    # A senha que usa para entrar no Workbench
        database="sertaoflix"      # O nome da sua base de dados
    )

    if ligacao.is_connected():
        print("Sucesso: Ligação estabelecida direta ao MySQL!")
        
        # O cursor permite executar comandos SQL de forma nativa
        cursor = ligacao.cursor()
        
        # Executa uma consulta simples de teste
        cursor.execute("SELECT VERSION();")
        versao = cursor.fetchone()
        print(f"Versão do Servidor MySQL: {versao[0]}")

except mysql.connector.Error as erro:
    print(f"Erro ao tentar ligar ao MySQL: {erro}")

finally:
    # Garantir que fechamos os canais de comunicação de forma segura
    if 'ligacao' in locals() and ligacao.is_connected():
        cursor.close()
        ligacao.close()
        print("Ligação encerrada com segurança.")