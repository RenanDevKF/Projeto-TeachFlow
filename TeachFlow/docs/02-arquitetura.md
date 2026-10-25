# Arquitetura do TeachFlow

## 1. Visão geral

O TeachFlow é uma aplicação web server-rendered construída com Django.

A arquitetura atual prioriza simplicidade operacional, regras de domínio
explícitas e proteção de dados por professor. O frontend utiliza Django
Templates, Tailwind CSS e JavaScript para interações progressivas,
enquanto o backend concentra autenticação, autorização, validação e
persistência.

``` text
Navegador
    |
    v
Django
├── accounts
├── core
├── templates
├── static
└── middleware
    |
    v
Django ORM
    |
    +-- SQLite       [desenvolvimento]
    |
    `-- PostgreSQL   [produção planejada]
```

O projeto não utiliza uma SPA como fronteira principal da aplicação. As
páginas são renderizadas pelo servidor e enriquecidas com JavaScript
onde necessário.

## 2. Organização principal

A aplicação é dividida em dois apps de domínio principais e um pacote de
configuração do projeto.

``` text
TeachFlow/
├── accounts/
│   └── identidade, autenticação, perfil e assinatura
│
├── core/
│   └── domínio pedagógico
│
├── teachflow/
│   └── configuração global, middleware e roteamento raiz
│
├── templates/
│   └── templates Django
│
└── static/
    └── CSS, JavaScript e dependências frontend locais
```

### `accounts`

Responsável por:

-   `CustomUser`;
-   perfil `Teacher`;
-   `Subscription`;
-   cadastro;
-   ativação de conta;
-   autenticação;
-   lockout;
-   recuperação de senha;
-   perfil;
-   alteração de senha;
-   troca de e-mail;
-   geração e validação de tokens;
-   envio dos e-mails transacionais relacionados à conta.

### `core`

Responsável pelo domínio pedagógico:

``` text
Dashboard
├── Turmas
│   ├── Alunos
│   └── Aulas
│       └── LessonExercise
│
├── Exercícios
│   ├── Tags
│   ├── Objetivos
│   └── Modelos de exercício
│
└── Biblioteca
    ├── Tags
    └── Objetivos de aprendizagem
```

### `teachflow`

Centraliza configurações globais do Django, middlewares, URLs raiz e
parâmetros de ambiente.

## 3. Modelo de identidade

O sistema utiliza um `CustomUser`.

Cada usuário professor possui um perfil `Teacher` em relação 1:1.

``` text
CustomUser
   |
   +-- 1:1 --> Teacher
   |
   `-- 1:1 --> Subscription
```

Durante o cadastro, usuário, perfil de professor e assinatura Free são
criados como parte do mesmo fluxo transacional.

Contas comuns permanecem inativas até a confirmação do endereço de
e-mail.

## 4. Autenticação

O login aceita dois identificadores:

``` text
e-mail
ou
username
```

O backend de autenticação normaliza o identificador e realiza consultas
case-insensitive.

Username não pode conter `@`, o que evita ambiguidade entre os
namespaces de username e e-mail.

A aplicação utiliza o sistema de sessões do Django. Não depende de
tokens de autenticação armazenados no `localStorage` do navegador.

## 5. Confirmação de e-mail e tokens

Ativação de conta e troca de e-mail utilizam tokens assinados com salts
independentes e expiração configurável.

### Ativação

O token de ativação associa a confirmação ao usuário e ao endereço de
e-mail esperado.

``` text
Cadastro
→ conta inativa
→ e-mail de ativação
→ token válido
→ conta ativa
→ email_verified_at preenchido
```

### Troca de e-mail

A alteração exige autenticação e confirmação da senha atual.

``` text
Solicitação
→ novo endereço
→ confirmação no novo endereço
→ validação do estado da conta
→ alteração
→ notificação no endereço antigo
```

O token carrega informação suficiente para verificar se o e-mail atual
ainda corresponde ao estado existente quando a solicitação foi criada.

## 6. Modelo de ownership

O isolamento entre professores é uma propriedade central da arquitetura.

As entidades chegam ao professor por diferentes relações:

``` text
Teacher
├── ClassGroup
│   ├── Student
│   └── Lesson
│       └── LessonExercise
│
├── Exercise
├── Tag
└── LearningObjective
```

Em termos de propriedade:

``` text
ClassGroup         → teacher
Student            → class_group → teacher
Lesson             → class_group → teacher
Exercise           → created_by
Tag                → teacher
LearningObjective  → teacher
```

O backend filtra os querysets pelo professor autenticado. IDs recebidos
por URL, formulário ou requisição não são considerados autorização
suficiente.

Um mixin genérico de ownership é utilizado onde o relacionamento
permite, e views específicas aplicam filtros próprios quando a estrutura
do domínio exige outro caminho.

## 7. Modelo de dados pedagógico

Uma representação simplificada das relações atuais é:

``` text
Teacher
├── ClassGroup
│   ├── Student
│   └── Lesson
│       ├── Tag
│       └── LessonExercise
│           └── Exercise
│
├── Exercise
│   ├── Tag
│   ├── LearningObjective
│   └── source_template → Exercise
│
├── Tag
└── LearningObjective
```

O modelo detalhado, constraints e cardinalidades são tratados
separadamente em `03-modelo-de-dados.md`.

## 8. `LessonExercise` como entidade intermediária

A relação entre `Lesson` e `Exercise` utiliza um modelo intermediário
explícito.

``` text
Lesson
   |
   v
LessonExercise
├── exercise
└── is_applied
```

Essa estrutura resolve uma diferença semântica importante:

> um exercício não é globalmente "aplicado"; ele é aplicado ou não no
> contexto de uma aula.

Assim, o mesmo `Exercise` pode ser reutilizado em várias aulas com
estados independentes.

A sincronização desses relacionamentos é executada pela camada de
aplicação de forma transacional.

Questões específicas de concorrência dessa sincronização permanecem
registradas para revisão e testes com PostgreSQL antes da produção.

## 9. Exercícios e modelos

`Exercise` pode funcionar como exercício comum ou como modelo
reutilizável.

Ao utilizar um modelo:

``` text
Exercise (modelo)
       |
       | cria cópia
       v
Exercise (independente)
       |
       `-- source_template
```

A cópia recebe seus próprios dados e relacionamentos.

`source_template` representa procedência, não dependência de ciclo de
vida. Por isso, a exclusão do modelo original não exclui as cópias; a
referência pode ser convertida para `NULL`.

O status de modelo é definido na criação e não é livremente convertido
durante a edição.

## 10. Biblioteca

A Biblioteca possui atualmente:

``` text
Tag
LearningObjective
```

Tags são universais dentro do domínio do professor. Não existe mais uma
classificação por `Tag.type`.

Tags e títulos de objetivos possuem normalização centralizada para
evitar que diferentes fluxos implementem regras divergentes.

Recursos arquivados permanecem válidos em relacionamentos históricos,
mas deixam de ser oferecidos normalmente para novas associações.

## 11. Validação e integridade

O TeachFlow divide responsabilidades entre aplicação e banco.

### Camada de aplicação

É utilizada para regras contextuais, dependentes do usuário ou da
operação, por exemplo:

-   restringir relações ao professor atual;
-   validar recursos disponíveis para novos vínculos;
-   tratar homônimos de alunos;
-   impedir transições semanticamente inválidas;
-   preservar relacionamentos arquivados durante edição.

### Banco de dados

É utilizado como defesa em profundidade para invariantes rígidas que
nunca devem representar estados válidos.

Exemplos incluem:

-   unicidades case-insensitive;
-   unicidade de `LessonExercise` por aula e exercício;
-   limites válidos para ano de turma;
-   limites válidos para duração de exercício.

A arquitetura evita transferir ao frontend responsabilidades de
integridade ou autorização.

## 12. Estratégia de arquivamento

O sistema não utiliza soft delete universal.

A estratégia depende do papel histórico da entidade.

``` text
Recurso ainda relevante ao histórico
→ arquivar / preservar vínculos

Recurso sem vínculo histórico protegido
→ exclusão pode ser permitida
```

Isso permite preservar a história pedagógica sem transformar todo
registro em dado permanente.

## 13. Segurança em camadas

A arquitetura atual utiliza diferentes mecanismos para problemas
diferentes.

### Autenticação e brute force

`django-axes` é responsável pela proteção do fluxo de autenticação
contra repetidas tentativas de login.

### Rate limiting de operações sensíveis

`django-ratelimit` é utilizado em operações específicas sujeitas a
abuso, como cadastro e determinados fluxos de e-mail.

### CSRF

Operações mutáveis seguem as proteções CSRF do Django.

### CSP

A aplicação utiliza Content Security Policy efetiva.

JavaScript executável próprio e dependências críticas são servidos
localmente, com `script-src 'self'`.

Estilos inline permanecem conscientemente autorizados porque existem
estilos dinâmicos legítimos no produto.

### Cache de páginas autenticadas

Um middleware específico aplica política de `no-store`/`no-cache` a HTML
autenticado para reduzir exposição em navegadores e dispositivos
compartilhados.

## 14. Frontend

A interface utiliza:

-   Django Templates;
-   Tailwind CSS;
-   JavaScript;
-   Lucide;
-   Flatpickr.

Lucide e Flatpickr são servidos localmente em vez de dependerem de
JavaScript remoto por CDN.

O JavaScript é utilizado para melhorar interações como formulários,
filtros, modais e componentes dinâmicos, enquanto autorização e regras
de negócio permanecem no servidor.

## 15. Configuração por ambiente

Configurações sensíveis e dependentes de infraestrutura são
parametrizadas por variáveis de ambiente.

Entre elas estão:

-   `SECRET_KEY`;
-   `DEBUG`;
-   `ALLOWED_HOSTS`;
-   origens CSRF;
-   HTTPS;
-   cookies Secure;
-   configuração de proxy;
-   HSTS;
-   backend e credenciais de e-mail.

Credenciais reais não devem ser versionadas.

O arquivo `.env.example` documenta a superfície esperada de configuração
sem conter secrets reais.

## 16. Banco de dados

### Desenvolvimento

O ambiente atual utiliza SQLite.

Ele é adequado ao estágio de desenvolvimento local e não deve receber
soluções artificiais específicas apenas para simular características de
concorrência do ambiente futuro.

### Produção

PostgreSQL foi definido como banco obrigatório para produção.

A migração será acompanhada de testes específicos dos comportamentos
transacionais identificados durante a auditoria, especialmente:

-   concorrência na sincronização de `LessonExercise`;
-   corrida entre exclusão de Tag/Objetivo e criação simultânea de novas
    associações.

## 17. Arquitetura financeira futura

O modelo financeiro implementado atualmente é intencionalmente pequeno.

``` text
Subscription
├── plan
├── external_id
└── is_active
```

A arquitetura não antecipa campos específicos de um gateway ainda não
escolhido.

Quando a integração for implementada, o fluxo esperado será:

``` text
Usuário
   |
   v
Checkout do gateway
   |
   v
Gateway
   |
   v
Webhook autenticado
   |
   v
Backend TeachFlow
   |
   v
Subscription
```

Princípios já definidos:

-   e-mail confirmado antes da contratação;
-   browser não é fonte de verdade financeira;
-   redirects não promovem conta para Pro;
-   webhook autenticado é a fonte externa de verdade;
-   processamento idempotente e transacional;
-   eventos fora de ordem devem ser suportados;
-   dados de cartão não são armazenados pelo TeachFlow.

## 18. Arquitetura de produção planejada

A topologia definitiva ainda dependerá da infraestrutura escolhida, mas
existem gates já estabelecidos.

Antes da exposição a usuários reais deverão estar resolvidos:

``` text
HTTPS
PostgreSQL
cookies Secure
proxy confiável
e-mail de produção
static files
backups + restore testado
observabilidade
proteção de URLs com tokens nos logs
check --deploy
fail-safe de configuração
```

HSTS será ativado somente depois de HTTPS estar efetivamente configurado
e validado.

A aplicação também deverá impedir que um ambiente declarado como
produção suba em condições inseguras, como `DEBUG=True`, SQLite, cookies
inseguros ou backend de e-mail de console.

## 19. Decisões deliberadamente não antecipadas

Algumas implementações foram conscientemente adiadas para evitar
arquitetura especulativa:

-   campos específicos do gateway;
-   máquina completa de estados financeiros;
-   política de exclusão de conta antes da definição de retenção e
    cancelamento;
-   locking específico para concorrência antes da migração para
    PostgreSQL;
-   configuração final de domínio público;
-   infraestrutura definitiva de deploy.

Esses pontos não representam esquecimentos. São dependências explícitas
das próximas fases do produto.

## 20. Direção arquitetural

A direção técnica do TeachFlow pode ser resumida assim:

``` text
MVP funcional
    ↓
documentação
    ↓
congelamento de escopo
    ↓
testes automatizados por risco
    ↓
Free × Pro
    ↓
gateway
    ↓
PostgreSQL + infraestrutura
    ↓
validação de produção
    ↓
beta
```

A prioridade imediata não é aumentar a quantidade de funcionalidades,
mas consolidar as garantias do sistema já construído e prepará-lo para
operar como produto real.
