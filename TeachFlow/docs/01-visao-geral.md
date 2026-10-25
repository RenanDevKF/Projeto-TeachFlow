# Visão Geral do TeachFlow

## 1. Sobre o projeto

O **TeachFlow** é uma aplicação web voltada à organização do trabalho
cotidiano de professores. Seu objetivo é oferecer um espaço único para
planejar aulas, registrar o que foi realizado, reutilizar materiais
pedagógicos e consultar o histórico construído ao longo do tempo.

O produto foi concebido como um **diário de trabalho do professor**, e
não como uma plataforma institucional de fiscalização. Essa distinção
orienta as regras de negócio: o sistema deve proteger a integridade dos
registros e impedir estados objetivamente inválidos, sem transformar a
rotina docente em um fluxo burocrático de autorizações e bloqueios.

O TeachFlow está atualmente em fase de consolidação do MVP. Os
principais módulos funcionais já foram implementados e passaram por
revisões funcionais e por uma auditoria transversal de segurança. As
próximas etapas concentram-se em testes automatizados, definição dos
limites Free/Pro, integração financeira e preparação do ambiente de
produção.

## 2. Problema que o TeachFlow busca resolver

O trabalho de um professor envolve informações que normalmente ficam
distribuídas entre anotações, documentos, planilhas e ferramentas sem
relação entre si:

-   turmas e alunos;
-   planejamento de aulas;
-   registros do que efetivamente foi realizado;
-   exercícios reutilizáveis;
-   objetivos de aprendizagem;
-   tags de organização;
-   observações e histórico pedagógico.

O TeachFlow centraliza esses elementos e mantém suas relações ao longo
do tempo.

A proposta não é decidir como o professor deve trabalhar. O sistema
fornece estrutura para que ele organize o próprio processo e preserve um
histórico confiável criado por ele.

## 3. Usuário principal

O usuário principal do MVP é o **professor**.

Cada professor possui um domínio de dados próprio. Turmas, alunos,
aulas, exercícios, tags e objetivos pertencem ao seu contexto e devem
permanecer isolados dos dados de outros professores.

Esse isolamento é uma regra de domínio e também uma fronteira de
segurança: a proteção é aplicada no backend, não apenas na interface.

## 4. Escopo atual do MVP

### 4.1 Dashboard

O dashboard fornece uma visão operacional do dia, incluindo o
planejamento diário, aulas previstas, planejamentos pendentes e um
resumo das turmas ativas.

### 4.2 Turmas

O professor pode criar e administrar turmas com informações como nome,
escola, ano letivo, período, horário e descrição.

Turmas podem ser arquivadas sem destruir os alunos e as aulas que
compõem seu histórico.

### 4.3 Alunos

Alunos pertencem a uma turma e podem armazenar nome, sobrenome, data de
nascimento opcional e observações.

O sistema permite homônimos e trata possíveis duplicidades de forma
contextual, evitando transformar uma heurística de identificação em uma
restrição rígida de banco de dados.

### 4.4 Aulas

A aula é um dos principais elementos do domínio.

Uma aula pode registrar:

-   turma;
-   data;
-   status;
-   título;
-   conteúdo;
-   observações de desempenho;
-   tags;
-   exercícios.

Os estados atuais são **Planejada**, **Realizada** e **Cancelada**.

A interface também distingue planejamentos futuros de planejamentos cuja
data já passou, permitindo ao professor localizar aulas pendentes sem
criar um estado de domínio artificial apenas para essa visualização.

### 4.5 Exercícios

Exercícios formam uma biblioteca reutilizável e podem conter descrição,
duração, materiais, tags e objetivos de aprendizagem.

Um exercício também pode ser marcado como modelo no momento de sua
criação. Ao utilizar um modelo, o TeachFlow cria um novo exercício
independente. A referência ao modelo de origem é apenas histórica e não
transforma a cópia em dependente permanente do original.

### 4.6 Biblioteca

A Biblioteca reúne atualmente dois tipos de recurso:

-   **Objetivos de aprendizagem**;
-   **Tags**.

Tags são universais dentro do domínio do professor e podem ser
reutilizadas em aulas e exercícios.

Objetivos representam finalidades pedagógicas reutilizáveis associadas
aos exercícios.

O antigo conceito de `FutureIdea` foi removido deliberadamente do MVP
após a evolução do fluxo de planejamento de aulas tornar sua
responsabilidade redundante.

## 5. Preservação do histórico

Uma das regras centrais do TeachFlow é distinguir **arquivamento** de
**exclusão**.

Quando um recurso deixa de ser utilizado no presente, mas ainda
participa do histórico do professor, o sistema procura preservar esse
relacionamento.

Em termos gerais:

-   recursos arquivados deixam de ser oferecidos normalmente para novos
    vínculos;
-   relacionamentos históricos existentes permanecem preservados;
-   exclusão permanente continua disponível quando não compromete
    informações relevantes.

O TeachFlow não adota soft delete universal. A estratégia depende da
semântica de cada entidade.

## 6. Relação entre aulas e exercícios

A relação entre uma aula e seus exercícios é representada explicitamente
por `LessonExercise`.

Isso permite armazenar informações pertencentes ao **uso de um exercício
em uma aula específica**, como o indicador de que ele foi aplicado.

Portanto, o estado de aplicação não pertence ao exercício global. O
mesmo exercício pode ser utilizado em diferentes aulas com estados
independentes.

Os objetivos apresentados no contexto de uma aula são derivados dos
exercícios associados a ela, evitando manter uma segunda relação
redundante entre aulas e objetivos.

## 7. Conta e acesso

O TeachFlow possui fluxo próprio de conta, incluindo:

-   cadastro;
-   confirmação de e-mail;
-   reenvio de ativação;
-   login por e-mail ou username;
-   proteção contra tentativas abusivas;
-   recuperação de senha;
-   perfil;
-   alteração de senha;
-   troca de e-mail com confirmação do novo endereço;
-   logout.

Toda conta comum nasce com o e-mail ainda não verificado e é ativada
após a confirmação válida.

## 8. Modelo Free e Pro

O produto foi planejado com dois planos:

-   **Free**;
-   **Pro**.

Toda conta nasce no plano Free. A intenção é permitir que o usuário
conheça o produto e compreenda desde cedo as vantagens da assinatura.

A integração financeira ainda não faz parte do estado implementado do
MVP. Checkout, gateway, webhooks e ciclo financeiro serão adicionados em
uma etapa própria.

A futura implementação seguirá alguns contratos já definidos:

-   somente conta com e-mail confirmado poderá contratar Pro;
-   frontend ou redirects nunca serão autoridade para promover uma
    conta;
-   o gateway e seus webhooks autenticados serão a fonte externa de
    verdade;
-   processamento financeiro deverá ser idempotente, transacional e
    tolerante a eventos fora de ordem;
-   o TeachFlow não armazenará dados de cartão.

## 9. Princípios de produto e engenharia

As decisões atuais podem ser resumidas nos seguintes princípios:

1.  **O professor controla seu próprio diário de trabalho.**
2.  **Histórico relevante deve ser preservado.**
3.  **Ownership é garantido pelo backend.**
4.  **Reutilização não deve criar dependências acidentais.**
5.  **Invariantes rígidas devem ser protegidas também pelo banco quando
    apropriado.**
6.  **Recursos arquivados permanecem válidos no histórico, mas deixam de
    ser oferecidos para novos vínculos.**
7.  **Toda conta nasce Free.**
8.  **Funcionalidades e dados sem função real no produto devem ser
    removidos em vez de mantidos por especulação.**
9.  **Segurança deve ser construída em camadas, sem depender
    exclusivamente da interface.**
10. **Atualizações técnicas são orientadas por risco e necessidade, não
    apenas pela existência de versões mais novas.**

## 10. Estado atual e próximos marcos

### Implementado

-   domínio principal de professores, turmas, alunos, aulas e
    exercícios;
-   Biblioteca de Tags e Objetivos;
-   cadastro, ativação, autenticação, recuperação de senha e perfil;
-   assinatura conceitual Free/Pro;
-   isolamento de dados por professor;
-   preservação histórica por arquivamento;
-   proteções de segurança revisadas no estágio atual;
-   configuração de ambiente preparada para evolução de produção.

### Próxima fase

-   congelamento funcional do MVP;
-   construção da suíte automatizada priorizada por risco;
-   regressão dos fluxos críticos;
-   definição prática dos limites Free/Pro.

### Planejado para produto comercial

-   escolha e integração do gateway de pagamento;
-   checkout;
-   webhooks;
-   ciclo de assinatura;
-   tratamento de cancelamento e demais estados financeiros.

### Gate de produção

Antes de receber usuários e dados reais, permanecem obrigatórios, entre
outros:

-   PostgreSQL;
-   tratamento e testes dos cenários de concorrência identificados;
-   HTTPS e cookies seguros;
-   política definitiva de HSTS;
-   provedor real de e-mail;
-   configuração segura de proxy;
-   observabilidade sem exposição indevida de dados e tokens;
-   backups automatizados com teste real de restauração;
-   validação de deploy e fail-safe de configuração.

## 11. O que o TeachFlow não pretende ser

No escopo atual, o TeachFlow não é:

-   um sistema escolar corporativo de fiscalização;
-   um ERP educacional;
-   um sistema de gestão administrativa de instituições;
-   uma plataforma de pagamentos própria;
-   um armazenador de dados de cartão;
-   uma ferramenta que decide a prática pedagógica pelo professor.

Seu foco permanece deliberadamente mais específico: **ajudar o professor
a planejar, registrar, reutilizar e consultar seu próprio trabalho com
organização, segurança e preservação histórica**.
