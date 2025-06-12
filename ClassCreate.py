import os
import re

# --- Definição das Classes ---

class Projeto:
    def __init__(self, id, vagas, notaMinima):
        self.id = id
        self.vagas = int(vagas)
        self.notaMinima = int(notaMinima)
        # Atributo para armazenar os alunos alocados durante o algoritmo
        self.alunosAlocados = []

    def __repr__(self):
        return (f"Projeto(id='{self.id}', vagas={self.vagas}, "
                f"notaMinima={self.notaMinima})")

class Aluno:
    def __init__(self, id, preferencias, nota):
        self.id = id
        self.preferencias = preferencias # Deve ser uma lista de strings [P1, P2, ...]
        self.nota = int(nota)
        # Atributos para controlar o estado do aluno no algoritmo
        self.proximaPropostaIdx = 0
        self.projetoAlocado = None

    def __repr__(self):
        return (f"Aluno(id='{self.id}', nota={self.nota}, "
                f"preferencias={self.preferencias})")

# --- Função de Carregamento e Parsing ---

def carregarDados(diretorioInputs):

    listaDeProjetos = []
    listaDeAlunos = []
    
    # --- Carregar Projetos ---
    arquivoProjetosPath = os.path.join(diretorioInputs, 'projetos.txt')
    try:
        with open(arquivoProjetosPath, 'r', encoding='utf-8') as f:
            for linha in f:
                linha = linha.strip()
                if not linha: continue
                # Usa expressão regular para extrair dados do formato (P1, 2, 5)
                match = re.search(r'\((\w+),\s*(\d+),\s*(\d+)\)', linha)
                if match:
                    id, vagas, notaMinima = match.groups()
                    projeto = Projeto(id, vagas, notaMinima)
                    listaDeProjetos.append(projeto)
    except FileNotFoundError:
        print(f"ERRO: Arquivo de projetos não encontrado em '{arquivoProjetosPath}'")
        return None, None

    # --- Carregar Alunos ---
    arquivoAlunosPath = os.path.join(diretorioInputs, 'alunos.txt')
    try:
        with open(arquivoAlunosPath, 'r', encoding='utf-8') as f:
            for linha in f:
                linha = linha.strip()
                if not linha: continue
                # Usa expressão regular para extrair dados do formato (A1):(P1,P30,P50) (5)
                match = re.search(r'\((\w+)\):\((.*?)\)\s*\((\d+)\)', linha)
                if match:
                    idAluno, prefsStr, nota = match.groups()
                    # Limpa e separa as preferências em uma lista
                    listaPrefs = [p.strip() for p in prefsStr.split(',')]
                    aluno = Aluno(idAluno, listaPrefs, nota)
                    listaDeAlunos.append(aluno)
    except FileNotFoundError:
        print(f"ERRO: Arquivo de alunos não encontrado em '{arquivoAlunosPath}'")
        return None, None
        
    return listaDeProjetos, listaDeAlunos

# --- Bloco de Execução Principal ---

if __name__ == "__main__":
    # Define o caminho para o diretório de entrada
    diretorioInputs = 'inputs'
    
    print(f"Carregando dados do diretório: '{diretorioInputs}'...")
    
    # Carrega os dados para as listas de objetos
    projetos, alunos = carregarDados(diretorioInputs)
    
    # Verifica se o carregamento foi bem-sucedido
    if projetos is not None and alunos is not None:
        print("\n--- Carregamento Concluído ---")
        print(f"Total de projetos carregados: {len(projetos)}")
        print(f"Total de alunos carregados: {len(alunos)}")
        
        # Exibe os primeiros 3 projetos e alunos como exemplo
        print("\n--- Exemplos de Dados Carregados ---")
        print("Projetos:")
        for p in projetos[:3]:
            print(p)
            
        print("\nAlunos:")
        for a in alunos[:3]:
            print(a)