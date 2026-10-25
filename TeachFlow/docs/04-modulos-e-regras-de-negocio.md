# Módulos e Regras de Negócio do TeachFlow

## 1. Objetivo

Este documento descreve o comportamento funcional dos módulos atuais do
TeachFlow e as principais regras de negócio que orientam cada fluxo.

O foco é explicar **o que o sistema faz e por quê**. Detalhes de
autenticação, segurança transversal, modelo físico de dados e
infraestrutura são tratados em documentos específicos.

## 2. Princípio de domínio

O TeachFlow é um diário de trabalho do professor.

Isso significa que o sistema deve:

-   organizar;
-   auxiliar;
-   preservar histórico;
-   impedir inconsistências objetivas;
-   proteger dados entre usuários.

Ele não pretende fiscalizar burocraticamente a prática docente.

Uma regra só deve restringir a ação do professor quando houver uma
justificativa concreta de domínio, integridade ou segurança.

------------------------------------------------------------------------

# 3. Dashboard

## Finalidade

O Dashboard oferece uma visão rápida do trabalho atual do professor.

Ele funciona como ponto de entrada após a autenticação.

## Informações principais

A visão atual inclui:

-   planejamento do dia;
-   aulas de hoje;
-   quantidade de planejamentos pendentes;
-   resumo das turmas ativas;
-   quantidade de alunos ativos nas turmas;
-   quantidade de aulas relacionadas.

A expressão **Planejamento do dia** é uma escolha deliberada de produto.

## Ordenação

Turmas e aulas são apresentadas de maneira previsível, considerando
informações como período, horário e identificação.

## Regras

-   somente dados do professor autenticado são considerados;
-   apenas turmas ativas entram no resumo principal;
-   o dashboard limita a quantidade de turmas exibidas e sinaliza quando
    existem outras;
-   planejamentos pendentes são derivados de aulas ainda planejadas cuja
    data já passou;
-   superusuários são direcionados ao Django Admin.

------------------------------------------------------------------------

# 4. Turmas

## Finalidade

Turmas estruturam o contexto em que alunos e aulas existem.

Uma turma representa um grupo administrado pelo professor em determinado
contexto escolar e período letivo.

## Dados principais

-   nome;
-   escola;
-   ano;
-   período;
-   horário;
-   descrição;
-   status ativo/arquivado.

## Operações

O módulo permite:

-   listar;
-   buscar;
-   filtrar;
-   visualizar;
-   criar;
-   editar;
-   arquivar;
-   restaurar;
-   excluir quando permitido.

## Filtros

A listagem pode trabalhar com critérios como:

-   status;
-   busca textual;
-   escola;
-   ano;
-   período.

## Arquivamento

Arquivar uma turma:

``` text
não exclui alunos
não exclui aulas
não destrói histórico
```

A turma deixa de participar normalmente dos fluxos destinados a recursos
correntes.

## Turma arquivada e aulas existentes

Uma aula já existente pode continuar relacionada à sua turma arquivada.

Isso é necessário para preservar o registro histórico.

Por outro lado, uma turma arquivada não deve ser oferecida normalmente
como destino para novas aulas ou transferências.

## Identidade

A aplicação normaliza os campos relevantes e impede duplicidades de
turma conforme a identidade definida no domínio do professor.

------------------------------------------------------------------------

# 5. Alunos

## Finalidade

O módulo de Alunos mantém os estudantes associados às turmas do
professor.

## Dados principais

-   nome;
-   sobrenome;
-   data de nascimento opcional;
-   observações;
-   status ativo/inativo;
-   turma.

## Operações

O professor pode:

-   visualizar lista geral;
-   visualizar alunos de uma turma;
-   buscar;
-   filtrar;
-   abrir detalhes;
-   cadastrar;
-   editar;
-   excluir conforme as regras atuais.

## Data de nascimento

A data é opcional.

Quando informada:

``` text
data futura → inválida
```

A idade exibida pelo sistema é calculada a partir da data de nascimento
e não precisa ser armazenada como dado redundante.

## Homônimos e possíveis duplicidades

Nome não é considerado identificador suficiente para impedir um
cadastro.

A regra atual diferencia situações.

### Mesmo nome e mesma data de nascimento

A combinação representa evidência forte de duplicidade e o cadastro é
bloqueado.

### Mesmo nome com informação insuficiente ou divergente

O sistema pode solicitar confirmação explícita.

### Pessoas realmente homônimas

Continuam permitidas.

Essa escolha evita impedir o cadastro legítimo de pessoas diferentes que
compartilham o mesmo nome.

------------------------------------------------------------------------

# 6. Aulas

## Finalidade

A aula é um dos elementos centrais do TeachFlow.

Ela representa tanto o planejamento quanto o registro posterior do
trabalho realizado pelo professor.

## Dados principais

-   turma;
-   data;
-   status;
-   título;
-   conteúdo;
-   observações de desempenho;
-   tags;
-   exercícios.

## Estados persistidos

``` text
Planejada
Realizada
Cancelada
```

## Seções de visualização

A interface pode organizar as aulas em:

``` text
Próximas
Pendentes
Realizadas
Canceladas
```

**Pendente não é um estado persistido.**

Uma aula é considerada pendente quando:

``` text
status = Planejada
e
data < hoje
```

Essa distinção evita criar estado de banco desnecessário apenas para uma
necessidade de consulta.

## Regra temporal

Uma aula marcada como Realizada não pode possuir data futura.

O objetivo dessa regra é impedir uma contradição objetiva, sem
transformar o TeachFlow em fiscal do calendário do professor.

## Listagem

A listagem suporta filtros como:

-   seção/status;
-   turma;
-   tag;
-   data.

Ela utiliza paginação para manter a navegação controlada.

## Criação

Ao criar uma aula, os recursos selecionáveis devem pertencer ao
professor autenticado.

Turmas arquivadas não são oferecidas normalmente para novas aulas.

## Edição

Ao editar uma aula existente, o sistema preserva relacionamentos
históricos válidos mesmo quando algum recurso associado foi
posteriormente arquivado.

Isso impede que simplesmente abrir e salvar uma aula antiga provoque
perda silenciosa de histórico.

## Exercícios da aula

A relação com exercícios utiliza `LessonExercise`.

Cada vínculo possui seu próprio estado de aplicação.

``` text
Aula A + Exercício X → aplicado
Aula B + Exercício X → não aplicado
```

O estado pertence ao vínculo, não ao exercício global.

## Progresso

A tela de detalhe pode calcular:

-   total de exercícios;
-   exercícios aplicados;
-   percentual de aplicação.

Esses valores são derivados dos vínculos da aula.

## Objetivos da aula

A aula não possui mais uma coleção independente de Objetivos.

Eles são obtidos através dos exercícios relacionados:

``` text
Aula
→ Exercícios
→ Objetivos
```

Isso evita duplicidade de fontes de verdade.

## Duplicação de aula

O professor pode utilizar uma aula existente como base para um novo
planejamento.

A duplicação reaproveita elementos de planejamento, como:

-   conteúdo;
-   exercícios;
-   tags.

A nova aula nasce como novo planejamento.

Observações ligadas à execução da aula anterior não devem ser tratadas
como conteúdo automaticamente reutilizável da nova execução.

------------------------------------------------------------------------

# 7. Exercícios

## Finalidade

Exercícios constituem uma biblioteca reutilizável de atividades
pedagógicas.

## Dados principais

-   título;
-   descrição;
-   duração;
-   materiais;
-   Tags;
-   Objetivos;
-   status ativo/arquivado;
-   indicador de modelo;
-   modelo de origem opcional.

## Operações

O módulo permite:

-   listar;
-   buscar;
-   filtrar;
-   visualizar detalhes;
-   criar;
-   editar;
-   arquivar;
-   restaurar;
-   excluir quando permitido;
-   utilizar um exercício modelo.

## Ownership

Exercícios pertencem ao professor que os criou.

Tags e Objetivos relacionados também devem pertencer ao mesmo domínio do
professor.

## Arquivamento

Um exercício arquivado deixa de ser oferecido normalmente para novas
utilizações.

Se já estiver relacionado a registros históricos, esses vínculos
permanecem.

## Exclusão

Um exercício que já participa de uma aula não pode ser simplesmente
excluído, pois isso destruiria parte do histórico da aula.

Nesses casos, o caminho apropriado é preservá-lo, inclusive por
arquivamento quando necessário.

## Duração

A duração é opcional.

Quando informada, deve respeitar os limites aceitos pelo domínio.

## Modelos

Um exercício pode ser marcado como modelo durante sua criação.

Essa identidade não deve ser convertida livremente depois que o registro
já existe.

## Usar um modelo

Ao utilizar um modelo, o sistema cria um **novo exercício**.

São reaproveitados os dados aplicáveis, inclusive relacionamentos como
Tags e Objetivos.

A cópia é independente.

Alterar posteriormente o modelo não significa alterar automaticamente
exercícios que já foram criados a partir dele.

## Exclusão do modelo original

Um modelo pode ser excluído mesmo que tenha originado cópias.

As cópias permanecem funcionais.

A referência de origem é histórica e pode desaparecer sem destruir o
novo exercício.

------------------------------------------------------------------------

# 8. Biblioteca

## Finalidade

A Biblioteca centraliza recursos pedagógicos reutilizáveis.

No estado atual, ela contém:

``` text
Objetivos de aprendizagem
Tags
```

O antigo módulo de Ideias Futuras (`FutureIdea`) foi removido
deliberadamente por ter se tornado redundante diante da evolução do
planejamento de aulas.

## Organização

A Biblioteca oferece navegação por seções e permite:

-   busca;
-   filtro por status;
-   paginação;
-   criação;
-   edição;
-   arquivamento;
-   restauração;
-   exclusão quando segura.

A paginação atual utiliza 15 itens por página.

## Busca

A busca opera por termos, permitindo localizar recursos sem exigir
correspondência textual integral.

------------------------------------------------------------------------

# 9. Objetivos de aprendizagem

## Finalidade

Objetivos representam finalidades pedagógicas reutilizáveis associadas
aos exercícios.

## Dados

-   título;
-   descrição;
-   status ativo/arquivado.

## Identidade

Dentro do domínio do professor, o título possui identidade
case-insensitive.

Exemplos conceitualmente equivalentes não devem gerar duplicatas apenas
por diferença de capitalização.

## Normalização

O título passa por normalização centralizada.

Isso evita comportamento diferente entre:

-   formulário tradicional;
-   criação rápida;
-   outros fluxos que venham a reutilizar a mesma regra.

## Arquivamento

Arquivar um Objetivo não remove suas relações históricas com exercícios.

Ele apenas deixa de ser oferecido normalmente para novas associações.

## Exclusão

A exclusão definitiva só deve ocorrer quando não comprometer
relacionamentos que precisam ser preservados.

## Criação rápida

Objetivos podem ser criados durante fluxos em que o professor está
trabalhando com exercícios.

A criação rápida utiliza as mesmas regras de identidade e normalização
da criação convencional.

------------------------------------------------------------------------

# 10. Tags

## Finalidade

Tags fornecem classificação flexível e reutilizável.

## Dados

-   nome;
-   cor;
-   status ativo/arquivado.

## Tags universais

Não existe mais divisão por tipo.

A mesma Tag pode participar dos contextos permitidos pelo produto,
especialmente:

``` text
Aulas
Exercícios
```

Essa decisão substituiu a antiga arquitetura baseada em `Tag.type`.

## Identidade

Dentro do domínio do professor:

``` text
nome case-insensitive → único
```

A normalização também trata espaços e caracteres permitidos.

## Tag arquivada com mesmo nome

Uma Tag arquivada continua sendo a mesma entidade.

Se o professor tentar criar outra com o mesmo nome, o sistema não deve
criar silenciosamente uma duplicata.

O fluxo orienta a recuperação/reativação da entidade existente.

## Arquivamento

Tags arquivadas permanecem nos registros antigos.

Elas deixam de ser normalmente oferecidas para novas associações.

## Exclusão

Tags sem vínculos protegidos podem ser removidas.

Quando participam de histórico que deve permanecer, arquivamento é
preferido à destruição da entidade.

## Criação rápida

Tags podem ser criadas diretamente de fluxos que necessitam delas.

A criação rápida utiliza as mesmas regras centrais de validação e
normalização.

------------------------------------------------------------------------

# 11. Regras transversais de ownership

Todos os módulos pedagógicos respeitam o domínio do professor
autenticado.

Uma requisição não ganha autorização simplesmente porque contém um ID
válido.

Exemplos:

``` text
professor A não pode selecionar turma do professor B
professor A não pode editar exercício do professor B
professor A não pode relacionar Tag do professor B
professor A não pode consultar aula do professor B apenas conhecendo seu ID
```

Essa regra é aplicada no backend.

------------------------------------------------------------------------

# 12. Regras transversais de arquivamento

O arquivamento segue uma ideia comum em diferentes módulos:

``` text
recurso ativo
→ disponível para novos usos

recurso arquivado
→ preservado
→ normalmente fora dos novos usos
```

A edição de um registro histórico não deve remover automaticamente um
relacionamento válido apenas porque o recurso relacionado foi arquivado
depois.

------------------------------------------------------------------------

# 13. Regras transversais de exclusão

O TeachFlow não aplica uma regra simplista de "nunca excluir" nem de
"sempre excluir".

A pergunta utilizada é:

> remover este objeto destruiria informação histórica que o professor
> espera preservar?

Se sim, o domínio protege o histórico ou direciona para arquivamento.

Se não, a exclusão definitiva pode permanecer uma operação legítima.

------------------------------------------------------------------------

# 14. Normalização e unicidade

Campos que representam identidades reutilizáveis são normalizados para
reduzir duplicidades acidentais.

Casos importantes:

``` text
username
e-mail
Tag
Objetivo
```

Unicidades case-insensitive relevantes também são protegidas pelo banco
quando a regra representa uma invariante estrutural.

------------------------------------------------------------------------

# 15. Concorrência

Alguns fluxos possuem proteção transacional na aplicação.

Durante a auditoria foram identificados dois cenários que merecem
tratamento adicional no banco de produção:

1.  concorrência na sincronização de `LessonExercise`;
2.  corrida entre exclusão de Tag/Objetivo e criação simultânea de
    associação.

Esses pontos foram conscientemente adiados para PostgreSQL, onde poderão
ser implementados e testados utilizando o comportamento transacional
real do ambiente de produção.

Não serão criadas soluções provisórias específicas para SQLite.

------------------------------------------------------------------------

# 16. Conta e assinatura no contexto funcional

Embora Conta e Perfil sejam documentados em detalhe separadamente,
algumas regras impactam o produto como um todo.

### Conta nova

``` text
Cadastro
→ conta ainda não confirmada
→ Subscription Free
→ confirmação de e-mail
→ acesso normal
```

### Pro

O plano Pro existe conceitualmente, mas o fluxo comercial ainda não foi
implementado.

Nenhum parâmetro de frontend ou cadastro pode transformar uma conta em
Pro.

A futura promoção dependerá da confirmação do gateway.

------------------------------------------------------------------------

# 17. Funcionalidades removidas

## `FutureIdea`

Foi removido do MVP.

Motivo:

-   sobreposição com o planejamento de aulas;
-   redução de valor conforme o fluxo de aulas evoluiu;
-   manutenção de um módulo separado deixou de se justificar.

## `Tag.type`

Foi removido.

Motivo:

-   Tags passaram a funcionar melhor como recurso universal;
-   a categorização artificial adicionava complexidade sem benefício
    proporcional.

## Relação direta Aula ↔ Objetivo

Foi removida.

Motivo:

-   os Objetivos já pertencem aos Exercícios;
-   manter ambos criava fontes de verdade duplicadas.

Essas remoções representam **decisões de produto**, não funcionalidades
acidentalmente ausentes.

------------------------------------------------------------------------

# 18. Filosofia das validações

O TeachFlow procura diferenciar:

``` text
contradição objetiva
versus
decisão legítima do professor
```

Uma contradição objetiva pode ser bloqueada.

Exemplo:

``` text
aula Realizada + data futura
```

Já uma escolha que apenas pareça incomum não deve automaticamente ser
proibida se ainda fizer sentido no diário pessoal do professor.

Essa filosofia evita transformar a aplicação em sistema de fiscalização
institucional.

------------------------------------------------------------------------

# 19. Estado do escopo funcional

Os módulos descritos neste documento compõem o núcleo funcional atual do
MVP:

``` text
Dashboard
Turmas
Alunos
Aulas
Exercícios
Biblioteca
├── Tags
└── Objetivos
```

A prioridade após a documentação é consolidar esse escopo por meio de
testes automatizados e regressão antes de ampliar o produto.

------------------------------------------------------------------------

# 20. Próxima evolução funcional

A próxima grande evolução não será adicionar indiscriminadamente novos
módulos.

A sequência planejada é:

``` text
consolidar MVP
→ testes críticos
→ definir limites Free/Pro
→ integrar gateway
→ preparar produção
→ beta
```

Novas funcionalidades deverão ser avaliadas contra o escopo congelado e
contra uma necessidade concreta do produto.
