import streamlit as st

def exibir_manual():
    st.subheader("Manual do Usuário & Instruções")
    st.markdown("""
        #### Credenciais Padrão de Acesso
        * **Administrador:** Usuário `senai` | Senha `python123`
        
        ---
        
        #### Como Navegar e Usar o Sistema
        * **Registrar e Gerenciar Empréstimos:** Escolha o leitor, o gênero e o livro disponível. Informe a data e clique em salvar.
        * **Filtros e Análise Automática:** Filtre por gênero ou status da devolução para atualizar as 4 métricas e os 2 gráficos de barras em tempo real.
        * **Confirmar Devolução e Exclusão:** Na aba de empréstimos, selecione o ID do empréstimo ativo para confirmar a devolução ou excluir um registro devolvido.
        * **Cadastrar Novo Livro / Acervo:** Adicione novos livros manualmente ou importe em massa via arquivo CSV (na aba de Administração).
        
        ---
        
        #### Arquitetura Técnica
        * **Frontend / Interface:** Streamlit
        * **Análise de Dados:** Pandas (`groupby`, métricas e filtragem de DataFrames)
        * **Banco de Dados:** SQLite (`biblioteca_v4.db` gerenciado em `banco.py`)
    """)

def exibir_canvas():
    st.subheader("Modelo de Negócio Canvas (Projeto Final)")
    st.markdown("Abaixo está o mapeamento do Canvas do sistema conforme os requisitos do projeto:")
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.info("**Parcerias-Chave**\n\nSetor de TI, gestores da biblioteca, fornecedores de tecnologia/hospedagem (Streamlit Cloud, GitHub).")
        st.info("**Recursos-Chave**\n\nBanco de dados SQLite, servidor Python, computadores/tablets do balcão de atendimento e acesso à internet.")
        
    with c2:
        st.success("**Atividades-Chave**\n\nRegistrar empréstimos/devoluções, gerenciar acervo de livros, calcular estatísticas automaticamente e gerenciar acessos.")
        st.success("**Canais**\n\nNavegador web (computador ou tablet da recepção da biblioteca).")
        
    with c3:
        st.warning("**Proposta de Valor**\n\nOrganização e rapidez na gestão de empréstimos, eliminação de controles manuais e visibilidade do acervo em tempo real.")
        st.warning("**Segmentos de Usuários**\n\nAtendentes do balcão, administradores do acervo e comunidade de leitores da instituição.")

    st.divider()

    col_bottom1, col_bottom2, col_bottom3 = st.columns(3)
    
    with col_bottom1:
        st.markdown("**Relacionamento com Usuários**\nInterface intuitiva, mensagens instantâneas de confirmação e suporte com níveis de permissão.")
    
    with col_bottom2:
        st.markdown("**Estrutura de Custos**\nEquipamento do balcão, manutenção de internet e treinamento simples da equipe.")
        
    with col_bottom3:
        st.markdown("**Economia Gerada / Retorno**\nRedução substancial do tempo de atendimento, eliminação de perdas de livros e fim do gasto com papel/fichas.")