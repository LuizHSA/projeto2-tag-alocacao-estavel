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

def galeShapley_var1(DadosAlunos, DadosProjetos):
    preferencias_projetos = {}
    for proj_id, dados_proj in DadosProjetos.iterrows():
        candidatos_qualificados = DadosAlunos[DadosAlunos['n'] >= dados_proj['nM']]
        
        candidatos_interessados = candidatos_qualificados[
            candidatos_qualificados['p'].apply(lambda prefs: proj_id in prefs)
        ]

        preferencias_projetos[proj_id] = candidatos_interessados.sort_values(by='n', ascending=False).index.to_list()


    alocacao_alunos = {aluno_id: None for aluno_id in DadosAlunos.index}
    ranking_projeto_alocado = {aluno_id: float('inf') for aluno_id in DadosAlunos.index}

    projetos_livres = list(DadosProjetos.index)
    proximo_convite_idx = {proj_id: 0 for proj_id in DadosProjetos.index}

    while projetos_livres:
        projeto_id = projetos_livres.pop(0)
        
        vagas_preenchidas = sum(1 for aluno, proj in alocacao_alunos.items() if proj == projeto_id)
        
        if vagas_preenchidas >= DadosProjetos.loc[projeto_id, 'v']:
            continue
            
        idx_proposta_atual = proximo_convite_idx[projeto_id]

        if idx_proposta_atual >= len(preferencias_projetos[projeto_id]):
            continue

        aluno_id_alvo = preferencias_projetos[projeto_id][idx_proposta_atual]
        proximo_convite_idx[projeto_id] += 1

        aluno_pref_list = DadosAlunos.loc[aluno_id_alvo, 'p']
        projeto_atual_do_aluno = alocacao_alunos[aluno_id_alvo]
        
        if projeto_atual_do_aluno is None:
            alocacao_alunos[aluno_id_alvo] = projeto_id
            ranking_projeto_alocado[aluno_id_alvo] = aluno_pref_list.index(projeto_id)
        else:
            ranking_novo_projeto = aluno_pref_list.index(projeto_id)
            if ranking_novo_projeto < ranking_projeto_alocado[aluno_id_alvo]:
                projeto_antigo_id = alocacao_alunos[aluno_id_alvo]
                alocacao_alunos[aluno_id_alvo] = projeto_id
                ranking_projeto_alocado[aluno_id_alvo] = ranking_novo_projeto
                
                if projeto_antigo_id not in projetos_livres:
                    projetos_livres.append(projeto_antigo_id)

        if projeto_id not in projetos_livres:
            projetos_livres.append(projeto_id)

    DadosAlunos['projeto_alocado'] = DadosAlunos.index.map(alocacao_alunos)
    return DadosAlunos


def galeShapley_var2(DadosAlunos, DadosProjetos):
    notas_alunos = DadosAlunos['n'].to_dict()
    vagas_projetos = DadosProjetos['v'].to_dict()
    
    DadosAlunos['projeto_alocado'] = None
    DadosAlunos['proxima_proposta_idx'] = 0
    
    alunos_livres = list(DadosAlunos.index)
    
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
            alunos_livres.append(aluno_id)
            continue

        nota_aluno_atual = notas_alunos[aluno_id]
        nota_minima_projeto = DadosProjetos.loc[projeto_id_alvo, 'nM']

        if nota_aluno_atual < nota_minima_projeto:
            alunos_livres.append(aluno_id)
            continue

        alunos_ja_alocados = alocacoes_projetos[projeto_id_alvo]
        
        if len(alunos_ja_alocados) < vagas_projetos[projeto_id_alvo]:
            alunos_ja_alocados.append(aluno_id)
            DadosAlunos.loc[aluno_id, 'projeto_alocado'] = projeto_id_alvo
        else:
            pior_aluno_id = min(alunos_ja_alocados, key=lambda id: notas_alunos[id])
            
            # --- ÚNICA MUDANÇA É AQUI: de '>' para '>=' ---
            if notas_alunos[aluno_id] >= notas_alunos[pior_aluno_id]:
                alunos_ja_alocados.remove(pior_aluno_id)
                DadosAlunos.loc[pior_aluno_id, 'projeto_alocado'] = None
                alunos_livres.append(pior_aluno_id)
                
                alunos_ja_alocados.append(aluno_id)
                DadosAlunos.loc[aluno_id, 'projeto_alocado'] = projeto_id_alvo
            else:
                alunos_livres.append(aluno_id)
                
    return DadosAlunos

def CalculoIndicePreferencia(DadosProcessados):
    """
    Calcula e exibe a média da ordem de preferência para cada projeto que recebeu alunos.
    Um índice menor indica que o projeto foi, em média, uma escolha prioritária.
    """
    print("\n--- ÍNDICE DE PREFERÊNCIA POR PROJETO ---")
    
    alunos_alocados = DadosProcessados.dropna(subset=['projeto_alocado'])
    
    preferencias_por_projeto = {}

    for aluno_id, info_aluno in alunos_alocados.iterrows():
        projeto_alocado = info_aluno['projeto_alocado']
        preferencias_do_aluno = info_aluno['p']
        
        try:
            ranking_da_escolha = preferencias_do_aluno.index(projeto_alocado) + 1
            
            if projeto_alocado not in preferencias_por_projeto:
                preferencias_por_projeto[projeto_alocado] = []
            preferencias_por_projeto[projeto_alocado].append(ranking_da_escolha)

        except ValueError:
            continue

    indice_final = {}
    for projeto_id, rankings in preferencias_por_projeto.items():
        if rankings:
            indice_final[projeto_id] = sum(rankings) / len(rankings)
            
    indice_series = pd.Series(indice_final).sort_values()
    
    print("Média da ordem de preferência (menor = mais preferido):")
    print(indice_series)
    
    return indice_series

def ExibirMatrizFinal(DadosProcessados):
    """
    Cria e exibe uma matriz (DataFrame) com os detalhes do emparelhamento final.
    """
    print("\n--- MATRIZ FINAL DE EMPARELHAMENTOS ---")
    
    dados_para_matriz = []
    alunos_alocados = DadosProcessados.dropna(subset=['projeto_alocado'])

    for aluno_id, info_aluno in alunos_alocados.sort_index().iterrows():
        projeto_alocado = info_aluno['projeto_alocado']
        nota_aluno = info_aluno['n']
        preferencias_do_aluno = info_aluno['p']

        try:
            ordem_da_preferencia = preferencias_do_aluno.index(projeto_alocado) + 1
        except ValueError:
            ordem_da_preferencia = "N/A"

        dados_para_matriz.append({
            'Aluno': aluno_id,
            'Projeto Alocado': projeto_alocado,
            'Nota do Aluno': nota_aluno,
            'Opção de Preferência': ordem_da_preferencia
        })

    matriz_df = pd.DataFrame(dados_para_matriz).set_index('Aluno')
    
    print(matriz_df)

    return matriz_df

def imprimirResultados(DadosAlunos, DadosProjetos):
    
    print("\n--- RESULTADO FINAL DA ALOCAÇÃO ---")
    
    alunos_alocados = DadosAlunos.dropna(subset=['projeto_alocado'])
    
    agrupado_por_projeto = alunos_alocados.groupby('projeto_alocado')
    
    for projeto_id, grupo_alunos in agrupado_por_projeto:
        vagas_totais = DadosProjetos.loc[projeto_id, 'v']
        print(f"\nProjeto: {projeto_id} (Vagas: {len(grupo_alunos)}/{vagas_totais})")
        
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
    
    if alunos_alocados_df.empty:
        print("Nenhum aluno foi alocado, não é possível gerar o grafo.")
        return

    alunos_alocados_ids = alunos_alocados_df.index.to_list()
    projetos_envolvidos_ids = alunos_alocados_df['projeto_alocado'].unique().tolist()
    
    arestas_alocadas = []
    for aluno_id, info_aluno in alunos_alocados_df.iterrows():
        arestas_alocadas.append((aluno_id, info_aluno['projeto_alocado']))

    G = nx.Graph()

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
    
    pos = dict()
    pos.update( (n, (1, i*1.5 - 1)) for i, n in enumerate(alunos_alocados_ids) )
    pos.update( (n, (2, i*1.5)) for i, n in enumerate(projetos_ordenados) )

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

        print('------ GALE SHAPLEY ORIGINAL ------')
        DadosProcessados = galeShapley(alunos, projetos, 1)
        imprimirResultados(DadosProcessados, projetos)
        CalculoIndicePreferencia(DadosProcessados)
        ExibirMatrizFinal(DadosProcessados)

        print('--- GALE SHAPLEY VAR 1 ---')
        DadosProcessados = galeShapley_var1(alunos, projetos)
        imprimirResultados(DadosProcessados, projetos)
        CalculoIndicePreferencia(DadosProcessados)
        ExibirMatrizFinal(DadosProcessados)

        print('--- GALE SHAPLEY VAR 2 ---')
        DadosProcessados = galeShapley_var2(alunos, projetos)
        imprimirResultados(DadosProcessados, projetos)
        CalculoIndicePreferencia(DadosProcessados)
        ExibirMatrizFinal(DadosProcessados)

        print('------ DEZ ITERAÇÕES COM INICIO EM POSIÇÕES DISTINTAS ------')
        for i in range(1, 11):
            print(f'Iteração {i}')
            DadosProcessados = galeShapley(alunos, projetos, i)
            fazerGrafo(DadosProcessados)