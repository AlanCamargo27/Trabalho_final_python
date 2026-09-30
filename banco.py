import hashlib
import sqlite3
import pandas as pd
import streamlit as st

NOME_BANCO = "biblioteca_v4.db"


@st.cache_resource
def conectar():
  return sqlite3.connect(NOME_BANCO, check_same_thread=False)


def gerar_hash_senha(senha):
  return hashlib.sha256(senha.encode('utf-8')).hexdigest()

def criar_tabela_usuarios():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            perfil TEXT NOT NULL
        )
    """)
    conexao.commit()

    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        senha_hash = gerar_hash_senha("admin123")
        cursor.execute(
            "INSERT INTO usuarios (usuario, senha, perfil) VALUES (?, ?, ?)",
            ("admin", senha_hash, "Administrador")
        )
        conexao.commit()
    
    #conexao.close()

def autenticar_usuario(usuario, senha):
    conexao = conectar()
    cursor = conexao.cursor()
    senha_hash = gerar_hash_senha(senha)
    
    cursor.execute(
        "SELECT id, usuario, perfil FROM usuarios WHERE usuario = ? AND senha = ?",
        (usuario, senha_hash)
    )
    resultado = cursor.fetchone()
    #conexao.close()
    
    if resultado:
        return {"id": resultado[0], "usuario": resultado[1], "perfil": resultado[2]}
    return None

def inserir_usuario(usuario, senha, perfil):
    try:
        conexao = conectar()
        senha_hash = gerar_hash_senha(senha)
        conexao.execute(
            "INSERT INTO usuarios (usuario, senha, perfil) VALUES (?, ?, ?)",
            (usuario, senha_hash, perfil)
        )
        conexao.commit()
        #conexao.close()
        return True, "usuário criado com sucesso!"
    except sqlite3.IntegrityError:
        return False, "Nome de usuário já existente."

def listar_usuarios():
    conexao = conectar()
    df = pd.read_sql_query("SELECT id, usuario, perfil FROM usuarios ORDER BY id ASC", conexao)
    #conexao.close()
    return df

def excluir_usuario_por_id(id_usuario):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = ?", (id_usuario,))
    conexao.commit()
    #conexao.close()

def criar_tabela():
    conexao = conectar()
    conexao.execute("""
        CREATE TABLE IF NOT EXISTS registro (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            leitor TEXT NOT NULL,
            genero TEXT NOT NULL,
            livro TEXT NOT NULL,
            devolucao TEXT NOT NULL,
            data TEXT NOT NULL
        )
    """)
    conexao.commit()
    #conexao.close()

def criar_tabela_livros():
    conexao = conectar()
    conexao.execute("""
        CREATE TABLE IF NOT EXISTS livros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            genero TEXT NOT NULL,
            UNIQUE(titulo, autor)
        )
    """)
    conexao.commit()
    #conexao.close()

def inserir_registro(leitor, genero, livro, devolucao, data):
    conexao = conectar()
    cursor = conexao.cursor()
    
    if devolucao == "Não":
        cursor.execute(
            "SELECT id FROM registro WHERE livro = ? AND devolucao = 'Não'", 
            (livro,)
        )
        ja_emprestado = cursor.fetchone()
        
        if ja_emprestado:
            #conexao.close()
            return False 
            
    cursor.execute(
        """
        INSERT INTO registro (leitor, genero, livro, devolucao, data)
        VALUES (?, ?, ?, ?, ?)
        """,
        (leitor, genero, livro, devolucao, data)
    )
    conexao.commit()
    #conexao.close()
    return True

def listar_registro():
    conexao = conectar()
    df = pd.read_sql_query("SELECT * FROM registro ORDER BY id DESC", conexao)
    #conexao.close()
    return df

def atualizar_devolucao(id_registro, novo_status="Sim"):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("SELECT livro, genero FROM registro WHERE id = ?", (id_registro,))
    resultado = cursor.fetchone()
    
    if resultado and novo_status == "Sim":
        texto_livro, genero = resultado

        if "]" in texto_livro:
            texto_limpo = texto_livro.split("]", 1)[1].strip()
        else:
            texto_limpo = texto_livro.strip()  

        if " - " in texto_limpo:
            titulo, autor = texto_limpo.rsplit(" - ", 1)
            titulo = titulo.strip()
            autor = autor.strip()

            cursor.execute("SELECT id FROM livros WHERE titulo = ? AND autor = ?", (titulo, autor))
            livro_existe = cursor.fetchone()

            if not livro_existe:
                cursor.execute(
                    "INSERT INTO livros (titulo, autor, genero) VALUES (?, ?, ?)",
                    (titulo, autor, genero)
                )

    conexao.execute(
        "UPDATE registro SET devolucao = ? WHERE id = ?",
        (novo_status, id_registro)
    )
    conexao.commit()
    #conexao.close()                             

def excluir_registros(id_registro):
    conexao = conectar()
    conexao.execute("DELETE FROM registro WHERE id = ?", (id_registro,))
    conexao.commit()
    #conexao.close()

def importar_livros_em_massa(lista_de_livros):
    conexao = conectar()
    conexao.executemany(
        "INSERT OR IGNORE INTO livros (titulo, autor, genero) VALUES (?, ?, ?)",
        lista_de_livros
    )
    conexao.commit()
    #conexao.close()

def listar_livros_disponiveis_por_genero(genero):
    conexao = conectar()
    cursor = conexao.cursor()

    query = """
        SELECT '[' || id || '] ' || titulo || ' - ' || autor 
        FROM livros 
        WHERE genero = ? 
        AND '[' || id || '] ' || titulo || ' - ' || autor NOT IN (
            SELECT livro FROM registro WHERE devolucao = 'Não'
        )
        ORDER BY titulo ASC
    """
    cursor.execute(query, (genero,))
    livros = [linha[0] for linha in cursor.fetchall()]
    #conexao.close()
    return livros 

def listar_todos_os_livros():
    conexao = conectar()
    df = pd.read_sql_query("SELECT id, titulo, autor, genero FROM livros ORDER BY id DESC", conexao)
    #conexao.close()
    return df   

def excluir_livro_por_id(id_livro):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT id FROM registro 
        WHERE devolucao = 'Não' AND livro LIKE ?
    """, (f'[{id_livro}] %',))
    
    if cursor.fetchone():
        #conexao.close()
        return False, f"O livro ID {id_livro} não pode ser excluído pois está atualmente emprestado."

    cursor.execute("DELETE FROM livros WHERE id = ?", (id_livro,))
    conexao.commit()
    #conexao.close()
    return True, f"Livro ID {id_livro} excluído com sucesso!"

def limpar_e_reiniciar_tabela(nome_tabela):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(f"DELETE FROM {nome_tabela}")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name = ?", (nome_tabela,))
    conexao.commit()
    #conexao.close()

def inserir_livro(titulo, autor, genero):
    try:
        conexao = conectar()
        conexao.execute(
            "INSERT INTO livros (titulo, autor, genero) VALUES (?, ?, ?)",
            (titulo, autor, genero)
        )
        conexao.commit()
        #conexao.close()
        return True
    except sqlite3.IntegrityError:
        return False

def alterar_senha_usuario(id_usuario, nova_senha):
    conn = conectar()
    cursor = conn.cursor()
    senha_hash = gerar_hash_senha(nova_senha)
    cursor.execute("UPDATE usuarios SET senha = ? WHERE id = ?", (senha_hash, id_usuario))
    conn.commit()
    conn.close()