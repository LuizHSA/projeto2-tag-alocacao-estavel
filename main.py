import networkx as nx
import matplotlib as plt
import pandas as pd
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


def galeShapley(DadosAlunos, DadosProjetos):
    # --- Inicialização ---
    # Dicionários para acesso rápido (muito mais rápido que buscar no DF dentro do loop)
    notas_alunos = DadosAlunos['n'].to_dict()
    vagas_projetos = DadosProjetos['v'].to_dict()
    
    # Adiciona colunas para gerenciar o estado da alocação
    DadosAlunos['projeto_alocado'] = None
    DadosAlunos['proxima_proposta_idx'] = 0
    
    # Lista de alunos que ainda não foram alocados
    alunos_livres = list(DadosAlunos.index)
    
    # Dicionário para rastrear as alocações atuais de cada projeto
    alocacoes_projetos = {proj_id: [] for proj_id in DadosProjetos.index}

    while alunos_livres:
        aluno_id = alunos_livres.pop(0)
        
        # Pega a lista de preferências do aluno
        preferencias_aluno = DadosAlunos.loc[aluno_id, 'p']
        idx_proposta_atual = DadosAlunos.loc[aluno_id, 'proxima_proposta_idx']

        # Se o aluno já esgotou suas preferências, ele permanece livre
        if idx_proposta_atual >= len(preferencias_aluno):
            continue

        # Identifica o projeto alvo da proposta
        projeto_id_alvo = preferencias_aluno[idx_proposta_atual]
        
        # Atualiza o índice para a próxima proposta deste aluno
        DadosAlunos.loc[aluno_id, 'proxima_proposta_idx'] += 1

        # Verifica se o projeto alvo é válido
        if projeto_id_alvo not in vagas_projetos:
            alunos_livres.append(aluno_id) # Devolve o aluno à lista para tentar a próxima opção
            continue

        # --- Lógica de Alocação ---
        alunos_ja_alocados = alocacoes_projetos[projeto_id_alvo]
        
        # Caso 1: Projeto tem vagas livres
        if len(alunos_ja_alocados) < vagas_projetos[projeto_id_alvo]:
            alunos_ja_alocados.append(aluno_id)
            DadosAlunos.loc[aluno_id, 'projeto_alocado'] = projeto_id_alvo
        
        # Caso 2: Projeto está cheio, precisa verificar se o novo aluno é melhor
        else:
            # Encontra o pior aluno atualmente alocado no projeto
            pior_aluno_id = min(alunos_ja_alocados, key=lambda id: notas_alunos[id])
            
            # Se o novo aluno tem nota maior que o pior alocado
            if notas_alunos[aluno_id] > notas_alunos[pior_aluno_id]:
                # Remove o pior aluno
                alunos_ja_alocados.remove(pior_aluno_id)
                DadosAlunos.loc[pior_aluno_id, 'projeto_alocado'] = None
                alunos_livres.append(pior_aluno_id) # O pior aluno volta a estar livre
                
                # Adiciona o novo aluno
                alunos_ja_alocados.append(aluno_id)
                DadosAlunos.loc[aluno_id, 'projeto_alocado'] = projeto_id_alvo
            
            # Se o novo aluno não for melhor, ele continua livre
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


# --- Bloco de Execução Principal ---

if __name__ == "__main__":
    
    diretorioInputs = 'inputs'
    projetos, alunos = carregarDados(diretorioInputs)

    if projetos and alunos:
        print("Dados carregados com sucesso. Iniciando o algoritmo de emparelhamento...")

        alunos, projetos = tratarDados(alunos, projetos)
        DadosProcessados = galeShapley(alunos, projetos)
        imprimirResultados(DadosProcessados, projetos)

        