from ClassCreate import Aluno, Projeto, carregarDados

def galeShapley(listaDeAlunos, listaDeProjetos):

    projetosDict = {p.id: p for p in listaDeProjetos}
    alunosLivres = [aluno for aluno in listaDeAlunos]

    while alunosLivres:
        aluno = alunosLivres.pop(0)

        if aluno.proximaPropostaIdx >= len(aluno.preferencias):
            continue

        idProjetoAlvo = aluno.preferencias[aluno.proximaPropostaIdx]
        aluno.proximaPropostaIdx +=1

        projeto = projetosDict.get(idProjetoAlvo)
        if not projeto:
            alunosLivres.append(aluno)
            continue

        if len(projeto.alunosAlocados) < projeto.vagas:
            projeto.alunosAlocados.append(aluno)
            aluno.projetoAlocado = projeto
        
        else:
            
            piorAlunoAlocado = min(projeto.alunosAlocados, key=lambda a: a.nota)

            if aluno.nota > piorAlunoAlocado.nota:
                
                projeto.alunosAlocados.remove(piorAlunoAlocado)
                piorAlunoAlocado.projetoAlocado = None

                projeto.alunosAlocados.append(aluno) 
                aluno.projetoAlocado = projeto

                alunosLivres.append(piorAlunoAlocado)
            else:
                alunosLivres.append(aluno)    

    return listaDeAlunos, listaDeProjetos    

def imprimirResultados(listaDeProjetos):
    
    print("\n--- RESULTADO FINAL DA ALOCAÇÃO ---")
    alunosAlocadosCount = 0
    for projeto in sorted(listaDeProjetos, key=lambda p: p.id):
        if projeto.alunosAlocados:
            print(f"\nProjeto: {projeto.id} (Vagas: {len(projeto.alunosAlocados)}/{projeto.vagas})")
            
            alunosOrdenados = sorted(projeto.alunosAlocados, key=lambda a: a.nota, reverse=True)
            for aluno in alunosOrdenados:
                print(f"  - Aluno: {aluno.id} (Nota: {aluno.nota})")
                alunosAlocadosCount += 1
    
    print(f"\nTotal de alunos alocados: {alunosAlocadosCount}")

# --- Bloco de Execução Principal ---

if __name__ == "__main__":
    
    diretorioInputs = 'inputs'
    projetos, alunos = carregarDados(diretorioInputs)

    if projetos and alunos:
        print("Dados carregados com sucesso. Iniciando o algoritmo de emparelhamento...")
        
        alunos, projetos = galeShapley(alunos, projetos)

        imprimirResultados(projetos)