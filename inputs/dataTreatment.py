def separarDadosEntrada(arquivoEntrada='entradaProj2_25TAG.txt'):
    
    arquivoProjetos = 'projetos.txt'
    arquivoAlunos = 'alunos.txt'
    
    try:
        with open(arquivoEntrada, 'r', encoding='utf-8') as fEntrada, \
             open(arquivoProjetos, 'w', encoding='utf-8') as fProjetos, \
             open(arquivoAlunos, 'w', encoding='utf-8') as fAlunos:
            
            emSecaoDeProjetos = True
            
            print('Lendo o arquivo')

            for linha in fEntrada:
                # Remove espaços em branco no início e no fim da linha
                linhaLimpa = linha.strip()

                # Ignora linhas em branco
                if not linhaLimpa:
                    continue

                # Detecta a linha de comentário que separa as seções 
                if '//alunos' in linhaLimpa:
                    emSecaoDeProjetos = False
                    continue # Pula para a próxima linha sem escrever o comentário

                # Ignora outras linhas de comentário 
                if linhaLimpa.startswith('//'):
                    continue

                # Escreve no arquivo apropriado com base na seção atual
                if emSecaoDeProjetos:
                    fProjetos.write(linha)
                else:
                    fAlunos.write(linha)

            print(f"✔ Arquivos '{arquivoProjetos}' e '{arquivoAlunos}' criados com sucesso!")

    except FileNotFoundError:
        print(f"Erro: O arquivo de entrada '{arquivoEntrada}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

# Executa a função
separarDadosEntrada()