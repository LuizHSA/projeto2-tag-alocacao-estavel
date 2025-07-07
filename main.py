import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import random
from ClassCreate import Aluno, Projeto, carregarDados


def tratarDados(listaDeAlunos, listaDeProjetos):
    dp, da = [], []

    for i in listaDeAlunos:
        da.append({
            'id': i.id,
            'p': i.preferencias,
            'n': i.nota,
        })

    for j in listaDeProjetos:
        dp.append({
            'id': j.id,
            'v': j.vagas,
            'nM': j.notaMinima,
        })
    da = pd.DataFrame(da).set_index('id')
    dp = pd.DataFrame(dp).set_index('id')
    print(da.head(), ' ', dp.head())
    return da, dp


def galeShapley(DadosAlunos, DadosProjetos, iteracao):
    notas_alunos = DadosAlunos['n'].to_dict()
    vagas_projetos = DadosProjetos['v'].to_dict()
    
    DadosAlunos['projeto_alocado'] = None
    DadosAlunos['proxima_proposta_idx'] = 0
    
    ordenar = list(DadosAlunos.index)
    if iteracao == 1:
        alunos_livres = ordenar
    elif iteracao == 2:
        alunos_livres = ordenar[::-1]
    else:
        alunos_livres = ordenar
        random.shuffle(alunos_livres)

    alocacoes_projetos = {proj_id: [] for proj_id in DadosProjetos.index}

    while alunos_livres:

        aluno_id = alunos_livres.pop(0)
        
        preferencias_aluno = DadosAlunos.loc[aluno_id, 'p']
        idx_proposta_atual = DadosAlunos.loc[aluno_id, 'proxima_proposta_idx']

        if idx_proposta_atual >= len(preferencias_aluno):
            continue

        projeto_id_alvo = preferencias_aluno[idx_proposta_atual]
        
        DadosAlunos.loc[aluno_id, 'proxima_proposta_idx'] += 1

        if projeto_id_alvo not in DadosProjetos.index:
            alunos_livres.append(aluno_id) # Aluno tentará a próxima preferência na sua vez
            continue # Pula para o próximo aluno livre

        # Agora que sabemos que o projeto existe, podemos pegar seus dados com segurança
        nota_aluno_atual = notas_alunos[aluno_id]
        nota_minima_projeto = DadosProjetos.loc[projeto_id_alvo, 'nM']

        if nota_aluno_atual < nota_minima_projeto:
            alunos_livres.append(aluno_id) # Proposta rejeitada, aluno tenta a próxima preferência
            continue # Pula para o próximo aluno livre

        alunos_ja_alocados = alocacoes_projetos[projeto_id_alvo]
        
        if len(alunos_ja_alocados) < vagas_projetos[projeto_id_alvo]:
            alunos_ja_alocados.append(aluno_id)
            DadosAlunos.loc[aluno_id, 'projeto_alocado'] = projeto_id_alvo
        else:
            pior_aluno_id = min(alunos_ja_alocados, key=lambda id: notas_alunos[id])
            
            if notas_alunos[aluno_id] > notas_alunos[pior_aluno_id]:
                alunos_ja_alocados.remove(pior_aluno_id)
                DadosAlunos.loc[pior_aluno_id, 'projeto_alocado'] = None
                alunos_livres.append(pior_aluno_id)
                
                alunos_ja_alocados.append(aluno_id)
                DadosAlunos.loc[aluno_id, 'projeto_alocado'] = projeto_id_alvo
            else:
                alunos_livres.append(aluno_id)

    return DadosAlunos


def imprimirResultados(DadosAlunos, DadosProjetos):
    
    print("\n--- RESULTADO FINAL DA ALOCAÇÃO ---")
    
    # Filtra apenas alunos que foram alocados
    alunos_alocados = DadosAlunos.dropna(subset=['projeto_alocado'])
    
    # Agrupa os alunos por projeto para facilitar a impressão
    agrupado_por_projeto = alunos_alocados.groupby('projeto_alocado')
    
    for projeto_id, grupo_alunos in agrupado_por_projeto:
        vagas_totais = DadosProjetos.loc[projeto_id, 'v']
        print(f"\nProjeto: {projeto_id} (Vagas: {len(grupo_alunos)}/{vagas_totais})")
        
        # Ordena os alunos do grupo pela nota (do maior para o menor)
        alunos_ordenados = grupo_alunos.sort_values(by='n', ascending=False)
        
        for aluno_id, dados_aluno in alunos_ordenados.iterrows():
            print(f"  - Aluno: {aluno_id} (Nota: {dados_aluno['n']})")
    
    print(f"\nTotal de alunos alocados: {len(alunos_alocados)}")

def fazerGrafo(DadosAlunos):
    """
    Desenha e exibe um grafo bipartido mostrando APENAS os alunos e projetos
    que fazem parte do emparelhamento final.
    """
    alunos_alocados_df = DadosAlunos.dropna(subset=['projeto_alocado'])
    
    # Se ninguém foi alocado, não há o que desenhar.
    if alunos_alocados_df.empty:
        print("Nenhum aluno foi alocado, não é possível gerar o grafo.")
        return

    alunos_alocados_ids = alunos_alocados_df.index.to_list()
    projetos_envolvidos_ids = alunos_alocados_df['projeto_alocado'].unique().tolist()
    
    arestas_alocadas = []
    for aluno_id, info_aluno in alunos_alocados_df.iterrows():
        arestas_alocadas.append((aluno_id, info_aluno['projeto_alocado']))

    # CRIAR E DESENHAR O GRAFO
    G = nx.Graph()
    # Adicionamos apenas os nós que participam do emparelhamento
    G.add_nodes_from(alunos_alocados_ids, bipartite=0)
    G.add_nodes_from(projetos_envolvidos_ids, bipartite=1)
    G.add_edges_from(arestas_alocadas)

    pos_y_alunos = {aluno_id: i for i, aluno_id in enumerate(alunos_alocados_ids)}
    media_y_por_projeto = {}
    for proj_id in projetos_envolvidos_ids:
        alunos_neste_projeto = [aluno for aluno, projeto in arestas_alocadas if projeto == proj_id]
        if alunos_neste_projeto:
            soma_y = sum(pos_y_alunos[aluno_id] for aluno_id in alunos_neste_projeto)
            media_y_por_projeto[proj_id] = soma_y / len(alunos_neste_projeto)
    projetos_ordenados = sorted(projetos_envolvidos_ids, key=lambda p_id: media_y_por_projeto.get(p_id, 0))
    
    # Posicionamento
    pos = dict()
    pos.update( (n, (1, i*1.5 - 1)) for i, n in enumerate(alunos_alocados_ids) )
    pos.update( (n, (2, i*1.5)) for i, n in enumerate(projetos_ordenados) )

    # Desenho
    altura_figura = max(100, len(alunos_alocados_ids) / 4) 
    plt.figure(figsize=(12, altura_figura))
    
    nx.draw_networkx_nodes(G, pos, nodelist=alunos_alocados_ids, node_color='yellow', node_size=300)
    nx.draw_networkx_nodes(G, pos, nodelist=projetos_envolvidos_ids, node_color='lightgreen', node_size=300)
    nx.draw_networkx_edges(G, pos, edgelist=arestas_alocadas, edge_color='gray', alpha=0.7)
    nx.draw_networkx_labels(G, pos, font_size=6)

    plt.title(f"Visualização do Emparelhamento Final ({len(arestas_alocadas)} Alunos Alocados)", size=16)
    plt.axis('off')
    plt.show()

# --- Bloco de Execução Principal ---

if __name__ == "__main__":
    
    diretorioInputs = 'inputs'
    projetos, alunos = carregarDados(diretorioInputs)

    if projetos and alunos:
        print("Dados carregados com sucesso. Iniciando o algoritmo de emparelhamento...")

        alunos, projetos = tratarDados(alunos, projetos)
        DadosProcessados = galeShapley(alunos, projetos, 1)
        imprimirResultados(DadosProcessados, projetos)

        for i in range(1, 11):
            print(f'Iteração {i}')
            DadosProcessados = galeShapley(alunos, projetos, i)
            fazerGrafo(DadosProcessados)