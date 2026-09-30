import pandas as pd
import streamlit as st
from banco import (
    alterar_senha_usuario,
    autenticar_usuario,
    atualizar_devolucao,
    conectar,
    criar_tabela,
    criar_tabela_livros,
    criar_tabela_usuarios,
    excluir_livro_por_id,
    excluir_registros,
    excluir_usuario_por_id,
    importar_livros_em_massa,
    inserir_livro,
    inserir_registro,
    inserir_usuario,
    limpar_e_reiniciar_tabela,
    listar_livros_disponiveis_por_genero,
    listar_registro,
    listar_todos_os_livros,
    listar_usuarios,
)

from documento import exibir_canvas, exibir_manual

st.set_page_config(
    page_title="Sistema de Gerenciamento da Biblioteca", layout="wide"
)

if "msg_sucesso" in st.session_state:
  st.success(st.session_state["msg_sucesso"])
  del st.session_state["msg_sucesso"]

criar_tabela()
criar_tabela_livros()
criar_tabela_usuarios()

if "usuario_logado" not in st.session_state:
  st.session_state["usuario_logado"] = None


###### TELA INICIAL / LOGIN

if st.session_state["usuario_logado"] is None:
  st.title("Acesso ao Sistema de Biblioteca")

  aba_login, aba_manual, aba_canvas = st.tabs([
      "Acesso ao Sistema",
      "Manual do Usuário",
      "Modelo de Negócio Canvas",
  ])

  with aba_login:
    col_login, _ = st.columns([1, 2])
    with col_login:
      with st.form("form_login"):
        st.subheader("Login")
        usuario_input = st.text_input("Usuário:")
        senha_input = st.text_input("Senha:", type="password")
        btn_entrar = st.form_submit_button("Entrar", type="primary")

        if btn_entrar:
          dados_usuario = autenticar_usuario(
              usuario_input.strip(), senha_input.strip()
          )
          if dados_usuario:
            st.session_state["usuario_logado"] = dados_usuario
            st.toast("Login efetuado com sucesso!")
            st.rerun()
          else:
            st.toast("Usuário ou Senha incorretos.")
            st.error("Usuário ou Senha incorretos.")

  with aba_manual:
    exibir_manual()

  with aba_canvas:
    exibir_canvas()

  st.stop()


##### BARRA LATERAL E SISTEMA PRINCIPAL

st.sidebar.markdown(
    f"**Usuário:** {st.session_state['usuario_logado']['usuario']}"
)
with st.sidebar.expander("Alterar Senha"):
  with st.form("form_alterar_senha"):
    nova_senha = st.text_input("Nova Senha:", type="password")
    confirmar_senha = st.text_input("Confirmar Senha:", type="password")
    btn_alterar = st.form_submit_button("Atualizar Senha")

    if btn_alterar:
      if not nova_senha.strip():
        st.toast("A Senha não pode estar em branco.")
        st.error("A Senha não pode estar em branco.")
      elif nova_senha != confirmar_senha:
        st.toast("As senhas não coincidem.")
        st.error("As senhas não coincidem.")
      else:
        alterar_senha_usuario(
            st.session_state["usuario_logado"]["id"], nova_senha.strip()
        )
        st.toast("Senha alterada com sucesso!")

st.sidebar.markdown(
    f"**Perfil:** {st.session_state['usuario_logado']['perfil']}"
)
if st.sidebar.button("Sair / Logout"):
  st.session_state["usuario_logado"] = None
  st.toast("Sessão encerrada.")
  st.rerun()

######## SISTEMA DE GERENCIAMENTO DA BIBLIOTECA

st.title("Sistema de Gerenciamento da Biblioteca")

GENEROS_DISPONIVEIS = [
    "Suspense", "Fantasia", "Terror", "Aventura", "Autobiografia",
    "Thriller", "Educativo", "Romance", "Ficção", "Ficção Científica",
    "Ciência", "Não-Ficção", "Filosofia"
]

perfil_atual = st.session_state["usuario_logado"]["perfil"]

if perfil_atual == "Administrador":
    aba_emprestimo, aba_cadastro_livro, aba_admin = st.tabs([
        "Registrar e Gerenciar Empréstimos", 
        "Cadastrar Novo Livro / Acervo", 
        "Administração"
    ])
else:
    aba_emprestimo, aba_cadastro_livro = st.tabs([
        "Registrar e Gerenciar Empréstimos", 
        "Cadastrar Novo Livro / Acervo"
    ])


####### REGISTRAR E GERENCIAR EMPRÉSTIMOS

with aba_emprestimo:
    st.header("Registrar e Gerenciar Empréstimos")

    col_a, col_b = st.columns(2)
    with col_a:
        leitor = st.text_input("Leitor:", key="input_leitor")
        genero_selecionado = st.selectbox(
            "Gênero:",
            GENEROS_DISPONIVEIS,
            index=None,
            placeholder="Selecione o gênero",
            key="sb_genero"
        )
        
        opcoes_livros = listar_livros_disponiveis_por_genero(genero_selecionado) if genero_selecionado else []
            
        livro_selecionado = st.selectbox(
            "Livro:",
            opcoes_livros,
            index=None,
            placeholder="Escolha o gênero primeiro" if not genero_selecionado else "Escolha o livro disponível",
            disabled=not genero_selecionado,
            key="sb_livro"
        )

    with col_b:
        data = st.date_input("Data do Empréstimo:", format="DD/MM/YYYY", key="di_data")

    st.write("") 
    if st.button("Salvar Registro de Empréstimo", type="primary"):
        if not leitor.strip() or not genero_selecionado or not livro_selecionado:
            st.toast("Preencha todos os campos obrigatórios.")
            st.error("Preencha todos os campos obrigatórios antes de salvar.")
        else:
            sucesso = inserir_registro(
                leitor,
                genero_selecionado,
                livro_selecionado,
                "Não",
                data.strftime("%d/%m/%Y")
            )
            
            if sucesso:
                st.session_state["msg_sucesso"] = f"Empréstimo para {leitor} registrado com sucesso!"
                st.toast(f"Empréstimo para {leitor} registrado com sucesso!")
                st.rerun()
            else:
                st.toast("Livro já se encontra emprestado.")
                st.error(f"Erro: O livro '{livro_selecionado}' já se encontra emprestado no momento!")

    st.divider()
    st.subheader("Análise Automática")

    df_emprestimos = listar_registro()

    if df_emprestimos.empty:
        st.info("Nenhum empréstimo registrado ainda.")
    else:
        f1, f2 = st.columns(2)
        with f1:
            generos_no_df = list(df_emprestimos["genero"].unique())
            filtro_genero = st.multiselect(
                "Filtrar por Gênero:",
                options=generos_no_df,
                default=generos_no_df
            )
        with f2:
            filtro_status = st.selectbox(
                "Filtrar por Status:",
                options=["Todos", "Sim", "Não"],
                index=0
            )
            st.write("<br>" * 3, unsafe_allow_html=True)

        df_filtrado = df_emprestimos.copy()
        if filtro_genero:
            df_filtrado = df_filtrado[df_filtrado["genero"].isin(filtro_genero)]
        if filtro_status != "Todos":
            df_filtrado = df_filtrado[df_filtrado["devolucao"] == filtro_status]


        col1, col2, col3, col4 = st.columns(4)
        total_livros = len(df_filtrado)
        total_devolvidos = len(df_filtrado[df_filtrado["devolucao"] == "Sim"])
        taxa_devolucao = (total_devolvidos / total_livros * 100) if total_livros > 0 else 0
        genero_top = df_filtrado['genero'].mode()[0] if not df_filtrado.empty else "N/A"

        col1.metric("Total por Filtro", f"{total_livros}")
        col2.metric("Gênero Mais Popular", genero_top)
        col3.metric("Taxa de Devolução", f"{taxa_devolucao:.1f}%")
        col4.metric("Pendentes", f"{len(df_filtrado[df_filtrado['devolucao'] == 'Não'])}")

        st.write("<br>" * 3, unsafe_allow_html=True)

        if not df_filtrado.empty:
            col_graf1, col_graf2 = st.columns(2)

            with col_graf1:
                st.subheader("Livros Mais Emprestados")
                df_top_livros = (
                    df_filtrado.groupby("livro")["id"]
                    .count()
                    .reset_index()
                    .rename(columns={"id": "Quantidade", "livro": "Livro"})
                    .sort_values(by="Quantidade", ascending=False)
                    .head(5)
                )
                st.bar_chart(df_top_livros.set_index("Livro"), color="#ff4b4b")

            with col_graf2:
                st.subheader("Leitores Mais Assíduos")
                df_top_leitores = (
                    df_filtrado.groupby("leitor")["id"]
                    .count()
                    .reset_index()
                    .rename(columns={"id": "Empréstimos", "leitor": "Leitor"})
                    .sort_values(by="Empréstimos", ascending=False)
                    .head(5)
                )
                st.bar_chart(df_top_leitores.set_index("Leitor"), color="#0083B8")
        else:
            st.warning("Nenhum registro encontrado para os filtros selecionados.")

        st.divider()

        df_ativos = df_emprestimos[df_emprestimos["devolucao"] == "Não"]
        df_historico = df_emprestimos[df_emprestimos["devolucao"] == "Sim"]

        col_acao1, col_acao2 = st.columns(2)

        with col_acao1:
            st.subheader("Confirmar Devolução")
            if df_ativos.empty:
                st.info("Não há empréstimos ativos.")
            else:
                with st.form("form_atualizar", clear_on_submit=True):
                    opcoes_ativos_id = df_ativos["id"].tolist()
                    id_atualizar = st.selectbox("ID do Registro:", opcoes_ativos_id)
                    botao_atualizar = st.form_submit_button("Confirmar Devolução", type="primary")

                    if botao_atualizar:
                        atualizar_devolucao(id_atualizar, "Sim")
                        st.toast(f"Registro ID {id_atualizar} atualizado para 'Devolvido'.")
                        st.rerun()

        with col_acao2:
            st.subheader("Excluir Empréstimo Individual")
            with st.form("form_excluir", clear_on_submit=True):
                id_excluir = st.number_input("ID para excluir:", min_value=1, step=1, value=None)
                botao_excluir = st.form_submit_button("Excluir Registro")
                
                if botao_excluir:
                    if id_excluir is not None:
                        registro_alvo = df_emprestimos[df_emprestimos["id"] == id_excluir]
                        
                        if not registro_alvo.empty and registro_alvo.iloc[0]["devolucao"] == "Não":
                            st.toast("Ação bloqueada: Empréstimo ativo.")
                            st.error(f"O registro ID {id_excluir} Está Atualmente Empréstado.")
                        elif registro_alvo.empty:
                            st.toast("Registro não encontrado.")
                            st.warning(f"O registro ID {id_excluir} não foi encontrado.")
                        else:
                            excluir_registros(id_excluir)
                            st.toast(f"Registro ID {id_excluir} excluído!")
                            st.rerun()
                    else:
                        st.toast("Digite um ID válido.")
                        st.warning("Digite um ID válido.")

        with st.expander("Excluir Vários Registros Devolvidos em Lote"):
            if df_historico.empty:
                st.info("Não há registros devolvidos disponíveis para exclusão.")
            else:
                tabela_empr_interativa = st.dataframe(
                    df_historico,
                    use_container_width=True,
                    hide_index=True,
                    on_select="rerun",
                    selection_mode="multi-row"
                )
                
                linhas_empr_selecionadas = tabela_empr_interativa.get("selection", {}).get("rows", [])

                if linhas_empr_selecionadas:
                    registros_devolvidos_selecionados = df_historico.iloc[linhas_empr_selecionadas]
                    qtd_validos = len(registros_devolvidos_selecionados)

                    st.error(f"Você selecionou {qtd_validos} registro(s) devolvido(s) para exclusão.")
                    confirmar_empr_del = st.checkbox("Confirmo que desejo apagar os registros devolvidos selecionados")

                    if st.button("Remover Registros Selecionados", type="primary", disabled=not confirmar_empr_del):
                        for id_reg in registros_devolvidos_selecionados["id"]:
                            excluir_registros(id_reg)
                        st.toast(f"{qtd_validos} registro(s) excluído(s) com sucesso!")
                        st.rerun()

        st.divider()

        st.subheader("Livros Atualmente Emprestados")
        if df_ativos.empty:
            st.info("Nenhum livro está pendente de devolução.")
        else:
            st.dataframe(df_ativos, use_container_width=True, hide_index=True)

        st.write("")

        st.subheader("Histórico de Devoluções")
        if df_historico.empty:
            st.info("Nenhum livro foi devolvido ainda.")
        else:
            st.dataframe(df_historico, use_container_width=True, hide_index=True)

####### CADASTRAR NOVO LIVRO / ACERVO

with aba_cadastro_livro:
    st.header("Cadastrar Novo Livro / Acervo")
    
    with st.form("form_novo_livro", clear_on_submit=True):
        col_c, col_d = st.columns(2)
        with col_c:
            novo_titulo = st.text_input("Título:")
            novo_autor = st.text_input("Autor:")
        with col_d:
            novo_genero = st.selectbox("Gênero:", GENEROS_DISPONIVEIS, index=None, placeholder="Selecione o gênero")

        botao_salvar_livro = st.form_submit_button("Salvar Livro")
        
        if botao_salvar_livro:
            if not novo_titulo.strip() or not novo_autor.strip() or not novo_genero:
                st.toast("Preencha todos os campos do livro.")
                st.error("Preencha o título, autor e gênero do livro.")
            else:
                sucesso = inserir_livro(novo_titulo.strip(), novo_autor.strip(), novo_genero)
                if sucesso:
                    st.toast(f"Livro '{novo_titulo}' adicionado com sucesso!")
                    st.rerun()
                else:
                    st.toast("Este livro já está cadastrado.")
                    st.error("Este livro já está cadastrado no sistema.")

    st.divider()
    st.subheader("Visualização do Acervo")
    df_acervo = listar_todos_os_livros()

    if df_acervo.empty:
        st.info("O acervo está vazio.")
    else:
        st.dataframe(df_acervo, use_container_width=True, hide_index=True)

##### ADMINISTRAÇÃO

if perfil_atual == "Administrador":
    with aba_admin:
        st.header("Administração")

        st.subheader("Gerenciamento de usuários")
        col_cad_usr, col_list_usr = st.columns([1, 1])
        
        with col_cad_usr:
            st.markdown("##### Criar Novo usuário")
            with st.form("form_novo_usuario", clear_on_submit=True):
                novo_usuario = st.text_input("usuário:")
                nova_senha = st.text_input("Senha:", type="password")
                novo_perfil = st.selectbox("Perfil:", ["usuário Comum", "Administrador"])
                btn_salvar_usr = st.form_submit_button("Cadastrar usuário")

                if btn_salvar_usr:
                    if not novo_usuario.strip() or not nova_senha.strip():
                        st.toast("Preencha todos os campos.")
                        st.error("Preencha todos os campos do usuário.")
                    else:
                        sucesso, msg = inserir_usuario(novo_usuario.strip(), nova_senha.strip(), novo_perfil)
                        if sucesso:
                            st.toast(msg)
                            st.rerun()
                        else:
                            st.toast(msg)
                            st.error(msg)

        with col_list_usr:
            st.markdown("##### usuários Registrados")
            df_usuarios = listar_usuarios()
            st.dataframe(df_usuarios, use_container_width=True, hide_index=True)

            with st.expander("Deletar usuário"):
                id_usr_excluir = st.number_input("ID do usuário:", min_value=1, step=1, value=None)
                if st.button("Deletar usuário", type="primary"):
                    if id_usr_excluir:
                        if id_usr_excluir == st.session_state["usuario_logado"]["id"]:
                            st.toast("Ação não permitida.")
                            st.error("Não pode Deletar a sua própria conta!")
                        else:
                            excluir_usuario_por_id(id_usr_excluir)
                            st.toast(f"usuário ID {id_usr_excluir} deletado com sucesso!")
                            st.rerun()
                    else:
                        st.toast("Informe um ID válido.")

            with st.expander("Alterar Senha de usuário"):
                st.markdown("##### Redefinir Senha")
                with st.form("form_admin_reset_senha", clear_on_submit=True):
                    id_alvo = st.number_input("ID do usuário:", min_value=1, step=1, value=None)
                    senha_nova_admin = st.text_input("Nova Senha:", type="password")
                    btn_reset = st.form_submit_button("Redefinir Senha")

                    if btn_reset:
                        if id_alvo and senha_nova_admin.strip():
                            alterar_senha_usuario(id_alvo, senha_nova_admin.strip())
                            st.toast(f"Senha do usuário ID {id_alvo} atualizada!")
                            st.rerun()
                        else:
                            st.toast("Preencha o ID e a nova Senha.")
                            st.error("Preencha o ID e a nova Senha.")

        st.divider()
        st.subheader("Importar Livros em Lote")
        
        arquivo_carregado = st.file_uploader("Escolha seu arquivo CSV", type=["csv"])
        
        if arquivo_carregado is not None:
            try:
                df_upload = pd.read_csv(arquivo_carregado, sep=None, engine='python', encoding='utf-8-sig')
                df_upload.columns = df_upload.columns.str.strip()
                mapeamento = {
                    "Título": "titulo", "titulo": "titulo", 
                    "Gênero": "genero", "genero": "genero", 
                    "Autor": "autor", "autor": "autor"
                }
                df_upload = df_upload.rename(columns=mapeamento)
                
                if "titulo" in df_upload.columns and "autor" in df_upload.columns and "genero" in df_upload.columns:
                    df_upload["titulo"] = df_upload["titulo"].astype(str).str.strip()
                    df_upload["autor"] = df_upload["autor"].astype(str).str.strip()
                    df_upload["genero"] = df_upload["genero"].astype(str).str.strip()
                    
                    df_final = df_upload[["titulo", "autor", "genero"]]
                    tuplas_livros = list(df_final.itertuples(index=False, name=None))
                    
                    if st.button("Confirmar Importação", type="primary"):
                        importar_livros_em_massa(tuplas_livros)
                        st.toast(f"Importação concluída! {len(tuplas_livros)} registros enviados.")
                        st.rerun()
                else:
                    st.toast("Formato CSV inválido.")
                    st.error("Erro: O arquivo precisa conter as colunas 'titulo', 'autor' e 'genero'.")
            except Exception as e:
                st.toast("Erro ao processar CSV.")
                st.error(f"Erro ao ler o arquivo: {e}")

        st.divider()
        st.subheader("Gerenciamento do Acervo")
        df_acervo_admin = listar_todos_os_livros()

        if df_acervo_admin.empty:
            st.info("O acervo está vazio.")
        else:
            tabela_interativa = st.dataframe(
                df_acervo_admin,
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="multi-row" 
            )
            
            linhas_selecionadas = tabela_interativa.get("selection", {}).get("rows", [])

            if linhas_selecionadas:
                livros_selecionados = df_acervo_admin.iloc[linhas_selecionadas]
                quantidade = len(livros_selecionados)

                st.error(f"Você selecionou {quantidade} livro(s) para exclusão.")
                confirmar = st.checkbox("Confirmo que desejo apagar os livros selecionados")

                if st.button("Remover Livros Selecionados", type="primary", disabled=not confirmar):
                    for id_livro in livros_selecionados["id"]:
                        excluir_livro_por_id(id_livro)
                    st.toast(f"{quantidade} livro(s) removido(s) com sucesso!")
                    st.rerun()

        st.divider()
        st.subheader("Reset de Tabelas")
        with st.expander("Limpar Tabelas e Reiniciar IDs"):
            col_reset1, col_reset2 = st.columns(2)
            with col_reset1:
                confirmar_reset_livros = st.checkbox("Confirmo apagar todo o acervo")
                if st.button("Zerar Acervo", type="primary", disabled=not confirmar_reset_livros):
                    limpar_e_reiniciar_tabela("livros")
                    st.toast("Tabela de livros zerada!")
                    st.rerun()

            with col_reset2:
                confirmar_reset_registros = st.checkbox("Confirmo apagar histórico de empréstimos")
                if st.button("Zerar Empréstimos", type="primary", disabled=not confirmar_reset_registros):
                    limpar_e_reiniciar_tabela("registro")
                    st.toast("Tabela de empréstimos zerada!")
                    st.rerun()