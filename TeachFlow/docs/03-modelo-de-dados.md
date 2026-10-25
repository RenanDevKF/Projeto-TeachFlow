# Modelo de Dados do TeachFlow

## 1. Objetivo

Este documento descreve o modelo de dados atual do TeachFlow, suas
principais relações, responsabilidades e regras de integridade.

Ele representa o **estado atual do domínio**, não uma proposta futura.
Elementos planejados para produção ou para a futura integração
financeira são identificados separadamente quando necessário.

## 2. Visão geral

O domínio é centrado no professor.

``` mermaid
erDiagram
    CustomUser ||--|| Teacher : possui
    CustomUser ||--|| Subscription : possui

    Teacher ||--o{ ClassGroup : administra
    Teacher ||--o{ Exercise : cria
    Teacher ||--o{ Tag : possui
    Teacher ||--o{ LearningObjective : possui

    ClassGroup ||--o{ Student : possui
    ClassGroup ||--o{ Lesson : possui

    Lesson ||--o{ LessonExercise : utiliza
    Exercise ||--o{ LessonExercise : participa

    Lesson }o--o{ Tag : classifica
    Exercise }o--o{ Tag : classifica
    Exercise }o--o{ LearningObjective : trabalha

    Exercise o|--o{ Exercise : origina
```

A relação recursiva de `Exercise` representa `source_template`: um
exercício criado a partir de um modelo pode registrar sua origem sem
depender do ciclo de vida desse modelo.

## 3. `CustomUser`

`CustomUser` representa a identidade autenticável da aplicação.

Além das características fornecidas pelo sistema de usuários do Django,
o modelo atual possui regras próprias relacionadas a username, e-mail e
verificação de endereço.

### Regras relevantes

-   e-mail é obrigatório no fluxo normal de cadastro;
-   username e e-mail são tratados com unicidade case-insensitive;
-   username não pode conter `@`;
-   contas comuns nascem inativas;
-   `email_verified_at` registra a confirmação do endereço;
-   superusuários possuem tratamento próprio compatível com a
    administração do sistema.

A proibição de `@` no username também elimina ambiguidade no backend que
permite autenticação por username ou e-mail.

## 4. `Teacher`

`Teacher` é o perfil profissional associado ao usuário.

``` text
CustomUser 1 ─── 1 Teacher
```

O modelo foi mantido propositalmente enxuto. Dados sem utilização
concreta pelo produto foram removidos durante a evolução do módulo de
Conta e Perfil.

O perfil funciona também como uma das principais raízes de ownership do
domínio pedagógico.

## 5. `Subscription`

`Subscription` representa o estado conceitual da assinatura do usuário.

O modelo atual contempla os planos:

``` text
Free
Pro
```

Toda conta nasce Free.

A estrutura é intencionalmente mínima e não tenta antecipar a modelagem
de um gateway de pagamento ainda não escolhido.

### Importante

O modelo atual **não representa ainda um ciclo financeiro completo**.
Estados, identificadores e eventos específicos do futuro gateway deverão
ser modelados somente quando a integração financeira for definida.

## 6. `ClassGroup`

`ClassGroup` representa uma turma administrada pelo professor.

Principais informações:

-   professor;
-   nome;
-   descrição;
-   escola;
-   ano letivo;
-   período;
-   horário;
-   status ativo/arquivado;
-   timestamps.

### Relações

``` text
Teacher 1 ─── N ClassGroup
ClassGroup 1 ─── N Student
ClassGroup 1 ─── N Lesson
```

### Integridade

O domínio protege a identidade das turmas dentro do contexto do
professor e possui constraint para manter o ano letivo no intervalo
aceito pelo produto:

``` text
2000 <= year <= 2100
```

Arquivar uma turma não destrói seus alunos ou aulas.

## 7. `Student`

`Student` representa um aluno pertencente a uma turma.

Principais informações:

-   turma;
-   nome;
-   sobrenome;
-   data de nascimento opcional;
-   observações;
-   status ativo/inativo;
-   timestamps.

``` text
ClassGroup 1 ─── N Student
```

### Homônimos

O TeachFlow não define nome como identidade única de uma pessoa.

Por isso, alunos homônimos são permitidos. Possíveis duplicidades são
tratadas pela camada de aplicação de forma contextual, inclusive com uso
da data de nascimento quando disponível.

Essa regra é deliberadamente **não transformada em uma
`UniqueConstraint` rígida**.

## 8. `Lesson`

`Lesson` representa uma aula ou planejamento pertencente a uma turma.

Principais informações:

-   turma;
-   data;
-   status;
-   título;
-   conteúdo;
-   observações de desempenho;
-   tags;
-   exercícios;
-   timestamps.

Estados atuais:

``` text
PLANNED    → Planejada
COMPLETED  → Realizada
CANCELLED  → Cancelada
```

``` text
ClassGroup 1 ─── N Lesson
```

Uma aula realizada não pode representar uma data futura.

A noção de aula "pendente" usada na interface não é um quarto estado
persistido: ela é derivada de uma aula ainda planejada cuja data já
passou.

## 9. Relação `Lesson` ↔ `Tag`

Aulas podem possuir múltiplas Tags e uma Tag pode aparecer em múltiplas
aulas.

``` text
Lesson N ─── N Tag
```

Tags pertencem ao professor e são reutilizáveis.

Recursos arquivados já relacionados permanecem preservados no histórico,
embora não sejam normalmente oferecidos para novas associações.

## 10. Relação `Lesson` ↔ `Exercise`

A relação entre aulas e exercícios utiliza explicitamente
`LessonExercise` como modelo intermediário.

``` mermaid
erDiagram
    Lesson ||--o{ LessonExercise : possui
    Exercise ||--o{ LessonExercise : participa

    LessonExercise {
        boolean is_applied
        datetime created_at
        datetime updated_at
    }
```

Essa decisão permite armazenar estado pertencente à associação.

`is_applied` significa:

> o exercício foi aplicado **nesta aula**.

Ele não é uma característica global de `Exercise`.

### Unicidade

A combinação:

``` text
lesson + exercise
```

é única.

Assim, um mesmo exercício não pode possuir duas associações
independentes com a mesma aula.

### Concorrência

A sincronização normal desses vínculos é executada transacionalmente
pela aplicação.

Cenários concorrentes específicos foram identificados durante a
auditoria e serão revisitados com PostgreSQL e testes concorrentes antes
da produção.

## 11. `Exercise`

`Exercise` representa um exercício reutilizável criado pelo professor.

Principais informações:

-   professor criador;
-   título;
-   descrição;
-   duração opcional;
-   materiais;
-   objetivos;
-   tags;
-   indicador de modelo;
-   status ativo/arquivado;
-   modelo de origem opcional;
-   timestamps.

### Relações

``` text
Teacher 1 ─── N Exercise
Exercise N ─── N Tag
Exercise N ─── N LearningObjective
Exercise 1 ─── N LessonExercise
```

### Duração

Quando informada, a duração deve permanecer no intervalo:

``` text
1 <= duration <= 1440
```

`NULL` também é permitido.

Essa invariante possui proteção no banco.

## 12. Modelos de exercício e `source_template`

Um exercício pode ser criado como modelo.

Quando o professor utiliza esse modelo, o TeachFlow cria outro
`Exercise` com dados próprios e copia os relacionamentos aplicáveis.

``` text
Modelo A
   |
   +------> Exercício B
   |
   +------> Exercício C
```

B e C são independentes.

`source_template` registra apenas a procedência:

``` text
Exercise B.source_template → Modelo A
```

A relação utiliza semântica equivalente a `SET_NULL`: se A for excluído,
B continua existindo e sua referência de origem pode se tornar `NULL`.

Essa decisão evita transformar modelos em pais permanentes das cópias.

## 13. `Tag`

`Tag` é um recurso universal de classificação dentro do domínio do
professor.

Principais informações:

-   professor;
-   nome;
-   cor;
-   status ativo/arquivado;
-   timestamps.

``` text
Teacher 1 ─── N Tag
Tag N ─── N Lesson
Tag N ─── N Exercise
```

Não existe mais `Tag.type`.

### Identidade

A identidade lógica é:

``` text
professor + nome case-insensitive
```

A normalização centraliza espaços e valida os caracteres permitidos
antes da persistência.

Uma Tag arquivada continua sendo a mesma entidade. O sistema não deve
criar silenciosamente uma segunda Tag ativa com o mesmo nome.

## 14. `LearningObjective`

`LearningObjective` representa um objetivo de aprendizagem reutilizável.

Principais informações:

-   professor;
-   título;
-   descrição;
-   status ativo/arquivado;
-   timestamps.

``` text
Teacher 1 ─── N LearningObjective
LearningObjective N ─── N Exercise
```

### Identidade

A identidade lógica é:

``` text
professor + título case-insensitive
```

Os títulos são normalizados centralmente.

## 15. Por que `Lesson` não possui relação própria com `LearningObjective`

Uma versão anterior do domínio permitia associar objetivos diretamente à
aula.

Essa relação foi removida.

Atualmente:

``` text
Lesson
  ↓
LessonExercise
  ↓
Exercise
  ↓
LearningObjective
```

Os objetivos de uma aula são derivados dos exercícios que fazem parte
dela.

Isso evita duas fontes independentes de verdade para o mesmo conceito
pedagógico.

## 16. Ownership e fronteiras de dados

As principais rotas de ownership são:

  Entidade              Caminho de propriedade
  --------------------- -------------------------
  `ClassGroup`          `teacher`
  `Student`             `class_group → teacher`
  `Lesson`              `class_group → teacher`
  `Exercise`            `created_by`
  `Tag`                 `teacher`
  `LearningObjective`   `teacher`

A autorização não depende do conhecimento ou ocultação de IDs.

Views e formulários restringem consultas e relacionamentos ao professor
autenticado.

## 17. Arquivamento e histórico

`is_active` não significa que um registro arquivado deixou de existir.

A regra geral é:

``` text
ativo
→ disponível para operações correntes

arquivado
→ preservado no histórico
→ normalmente indisponível para novos vínculos
```

Formulários de edição podem preservar recursos arquivados já
relacionados ao objeto que está sendo alterado.

Isso evita que uma edição posterior destrua silenciosamente parte do
histórico.

## 18. Exclusão e integridade referencial

O TeachFlow não utiliza uma única política de exclusão para todas as
entidades.

A estratégia é escolhida de acordo com a semântica da relação.

Exemplos conceituais:

``` text
modelo de exercício excluído
→ cópias sobrevivem
→ source_template pode virar NULL

exercício já utilizado em aula
→ exclusão protegida

recurso sem histórico protegido
→ exclusão pode ser permitida
```

O objetivo é preservar registros pedagógicos sem impedir a remoção
legítima de dados que não possuem mais função.

## 19. Normalização

Algumas identidades textuais precisam permanecer consistentes
independentemente do fluxo de entrada.

Por isso, normalizações importantes foram centralizadas.

Entre elas:

-   e-mail;
-   username;
-   nome de Tag;
-   título de Objetivo.

A normalização de Tags também controla espaços internos e caracteres
aceitos.

Essa centralização reduz divergências entre formulários tradicionais,
criação rápida e outras entradas do sistema.

## 20. Aplicação versus banco de dados

A arquitetura distingue dois tipos de regra.

### Regras contextuais

Pertencem principalmente à aplicação:

-   ownership;
-   disponibilidade de recurso arquivado;
-   confirmação de possível aluno duplicado;
-   regras dependentes do usuário atual;
-   validações ligadas ao fluxo da operação.

### Invariantes estruturais

Quando uma condição representa um estado que jamais deve existir e pode
ser expressa de maneira estável, ela também é protegida pelo banco.

Exemplos:

``` text
unicidades case-insensitive
LessonExercise único por Lesson + Exercise
ClassGroup.year entre 2000 e 2100
Exercise.duration entre 1 e 1440 ou NULL
```

Essa combinação fornece defesa em profundidade sem deslocar regras
contextuais complexas para constraints inadequadas.

## 21. Banco atual e banco de produção

### Desenvolvimento

O desenvolvimento utiliza SQLite.

### Produção

PostgreSQL é o banco definido para produção.

A migração não será tratada apenas como troca de engine. Ela incluirá
revalidação das constraints, comportamento transacional e cenários de
concorrência previamente identificados.

## 22. Evolução do modelo

O modelo atual é resultado de simplificações deliberadas.

Entre as mudanças relevantes já realizadas estão:

-   criação explícita de `LessonExercise`;
-   remoção da relação direta `Lesson` ↔ `LearningObjective`;
-   remoção de `FutureIdea`;
-   remoção de `Tag.type`;
-   Tags universais;
-   unicidade case-insensitive por professor para Tags e Objetivos;
-   introdução de arquivamento para recursos reutilizáveis;
-   constraints adicionais de integridade;
-   redução de dados não utilizados no perfil do professor.

O objetivo dessas mudanças foi aproximar a estrutura persistida das
regras reais do produto e reduzir conceitos redundantes.

## 23. Escopo financeiro futuro

`Subscription` é a única representação financeira conceitual atual.

A futura integração com gateway poderá exigir novas entidades para
eventos, estados ou referências externas.

Essas estruturas **não são especificadas neste documento como se já
existissem**.

O modelo financeiro definitivo será desenhado a partir da API e da
máquina de estados do provedor escolhido, respeitando o contrato
arquitetural definido para pagamentos.
