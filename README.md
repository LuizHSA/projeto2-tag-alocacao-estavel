# Descrição das Variações do Algoritmo de Emparelhamento

Este projeto explora o desafio de alocar alunos a projetos, um cenário conhecido na Ciência da Computação como o Problema do Emparelhamento Estável. O objetivo é criar um sistema de alocação que seja não apenas eficiente, mas também "estável" — ou seja, um estado onde não exista um aluno e um projeto que prefeririam estar juntos em vez de suas alocações atuais. Para investigar as nuances desse problema, implementamos e comparamos três variações distintas do clássico algoritmo de Gale-Shapley, cada uma oferecendo uma perspectiva diferente.

## A Abordagem Clássica: O Poder da Escolha dos Alunos

Nossa primeira implementação segue a lógica mais tradicional do algoritmo, colocando o poder de escolha nas mãos dos alunos. Nesta versão, os alunos são os agentes ativos que buscam uma vaga. Cada aluno, um por um, faz propostas aos projetos seguindo estritamente sua lista de preferências, da mais desejada para a menos.

Do outro lado, um projeto, ao receber uma proposta, age de forma pragmática e baseada em mérito. Se um projeto ainda tem vagas livres e o aluno proponente cumpre o requisito de nota mínima, o aluno é aceito provisoriamente. A situação se torna mais interessante quando o projeto já está cheio. Neste caso, ele só aceitará o novo candidato se sua nota for estritamente maior (>) que a do pior aluno já alocado. Se a troca ocorrer, o aluno com a nota mais baixa é desalojado e volta para a fila de "alunos livres", tendo que tentar sua próxima opção.

Como esperado de uma abordagem onde os alunos ditam o ritmo, o resultado tende a ser ótimo para os alunos, garantindo que eles consigam a melhor alocação possível do seu ponto de vista. Em nossa simulação, este método resultou em 58 alunos alocados.

## Variação 1: Invertendo os Papéis - A Vez dos Projetos

Para explorar uma perspectiva diferente, esta variação inverte a dinâmica: aqui, são os projetos que tomam a iniciativa. Cada projeto cria sua própria "lista de desejos", contendo apenas os alunos que são simultaneamente qualificados (possuem a nota mínima) e interessados (incluíram o projeto em suas preferências). Essa lista é ordenada da maior para a menor nota, garantindo que o projeto sempre tente recrutar os melhores talentos primeiro.

Neste cenário, um projeto com vagas disponíveis faz um "convite" ao melhor aluno em sua lista. O aluno, por sua vez, avalia a proposta: se estiver livre, ele aceita; se já estiver alocado em um "Projeto A", ele consultará sua própria lista de preferências e só aceitará o novo convite do "Projeto B" se o considerar melhor. Caso aceite, ele abandona o Projeto A, que volta à "caça" por um novo candidato.

Este emparelhamento é, por sua vez, ótimo para os projetos, garantindo que eles montem a equipe mais forte possível. Curiosamente, o número total de alocados foi o mesmo da abordagem anterior (58), mas a composição mudou, revelando uma estabilidade diferente. Por exemplo, no Projeto P10, o aluno A10 foi substituído pelo A66, mostrando como a mudança de perspectiva altera o resultado final.

## Variação 2: Uma Pequena Mudança, um Grande Impacto

Esta última variação retorna ao modelo onde os alunos propõem, mas altera uma única e crucial regra: o critério de desempate quando um projeto está cheio. Enquanto a abordagem padrão é conservadora, esta é mais "agressiva".

A lógica é idêntica à do algoritmo padrão, com uma exceção: se um projeto está lotado, a troca ocorre se a nota do novo aluno for maior ou igual (>=) à do pior aluno já alocado. Em caso de empate na nota, o novo proponente tem a preferência.

Essa pequena alteração revelou um resultado notável: o algoritmo conseguiu encontrar um emparelhamento máximo maior, alocando 59 alunos no total. A maior "rotatividade" permitiu que um aluno a mais (A127, no projeto P31) encontrasse uma vaga que não estava disponível nas outras duas simulações. Isso demonstra o quão sensível o resultado pode ser a regras aparentemente menores e como uma abordagem diferente de desempate pode levar a uma solução globalmente mais eficiente em termos de ocupação de vagas.