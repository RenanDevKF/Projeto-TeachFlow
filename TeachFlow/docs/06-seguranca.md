# Segurança do TeachFlow

## 1. Objetivo

Este documento consolida a postura de segurança atual do TeachFlow.

Ele não deve ser interpretado como uma afirmação de que a aplicação está
pronta para produção. A segurança foi tratada em camadas durante o
desenvolvimento e passou por uma auditoria transversal, mas existem
**gates obrigatórios de pré-produção** que dependem da infraestrutura
definitiva.

A documentação distingue três categorias:

``` text
IMPLEMENTADO
→ controle presente no estado atual

DECISÃO CONSCIENTE
→ comportamento analisado e aceito no estágio atual

GATE DE PRODUÇÃO
→ requisito obrigatório antes de usuários/dados reais
```

## 2. Modelo de ameaça resumido

As principais superfícies consideradas incluem:

-   acesso de um professor aos dados de outro;
-   brute force e credential stuffing;
-   abuso de endpoints de e-mail;
-   CSRF;
-   XSS e execução de conteúdo remoto;
-   enumeração de contas;
-   manipulação de IDs e relacionamentos;
-   estados inválidos por escrita concorrente;
-   exposição de tokens em logs;
-   configuração insegura de produção;
-   dependências vulneráveis;
-   comprometimento ou exposição de secrets;
-   fraude no futuro fluxo financeiro.

O TeachFlow adota defesa em profundidade: nenhuma única camada é
considerada suficiente para todos esses riscos.

------------------------------------------------------------------------

# 3. Autorização e ownership

**Status: IMPLEMENTADO**

O isolamento de dados por professor é uma das fronteiras de segurança
mais importantes do sistema.

O backend restringe os querysets conforme o ownership da entidade.

Exemplos:

``` text
ClassGroup         → teacher
Student            → class_group → teacher
Lesson             → class_group → teacher
Exercise            → created_by
Tag                 → teacher
LearningObjective   → teacher
```

Conhecer o ID de um objeto não concede acesso a ele.

Formulários e endpoints que criam relacionamentos também validam o
domínio do professor, reduzindo riscos de IDOR e associação entre dados
de usuários diferentes.

## 4. Autenticação

**Status: IMPLEMENTADO**

A autenticação utiliza os mecanismos de sessão do Django.

O login aceita e-mail ou username por backend próprio, mantendo a
verificação da senha sob os mecanismos seguros do framework.

Username e e-mail possuem regras de unicidade case-insensitive e
normalização centralizada.

Username não pode conter `@`, reduzindo ambiguidade entre os dois
identificadores aceitos.

## 5. Verificação de e-mail

**Status: IMPLEMENTADO**

Contas comuns exigem confirmação de e-mail para ativação.

A confirmação utiliza token assinado e temporário.

`email_verified_at` registra explicitamente a verificação.

A futura contratação do plano Pro também dependerá de endereço
confirmado.

## 6. Brute force no login

**Status: IMPLEMENTADO**

`django-axes` protege o fluxo de login.

Durante a auditoria, foram validados:

-   incremento das tentativas inválidas;
-   lockout;
-   impossibilidade de contornar lockout usando senha correta;
-   expiração/liberação após cooloff;
-   autenticação normal depois da liberação.

O Axes é a solução destinada ao problema de brute force de autenticação;
rate limiting genérico não substitui essa responsabilidade.

## 7. Rate limiting de operações sensíveis

**Status: IMPLEMENTADO**

`django-ratelimit` é aplicado a fluxos específicos que podem ser
abusados independentemente do login.

Os controles consideram chaves adequadas ao contexto, incluindo:

-   IP;
-   e-mail normalizado;
-   usuário autenticado.

Entre os objetivos estão reduzir:

-   spam de cadastro;
-   abuso de reenvio de ativação;
-   abuso de recuperação de senha;
-   abuso de solicitações sensíveis da conta.

Rate limiting é defesa adicional e não mecanismo de autorização.

## 8. Enumeração de contas

**Status: IMPLEMENTADO / CONTROLADO**

Fluxos como recuperação de senha e reenvio de ativação evitam respostas
excessivamente reveladoras sobre a existência ou estado de uma conta.

A aplicação busca equilibrar:

-   experiência do usuário legítimo;
-   não transformar endpoints públicos em ferramentas triviais de
    enumeração.

Essa proteção deve continuar sendo considerada ao alterar mensagens
desses fluxos.

## 9. CSRF

**Status: IMPLEMENTADO**

O TeachFlow utiliza as proteções CSRF do Django para operações mutáveis.

Formulários incluem tokens apropriados e views sensíveis mantêm a
proteção esperada.

Requisições JavaScript que alteram estado também devem seguir a mesma
fronteira de confiança.

## 10. XSS e escaping

**Status: IMPLEMENTADO COM DEFESAS EM CAMADAS**

Django Templates escapam conteúdo por padrão.

Além disso, a Content Security Policy limita as origens capazes de
executar scripts.

A aplicação não deve utilizar marcação de conteúdo do usuário como
seguro sem justificativa explícita.

## 11. Content Security Policy

**Status: IMPLEMENTADO**

A CSP está em modo efetivo de bloqueio.

A política restringe scripts a origens controladas pelo TeachFlow:

``` text
script-src 'self'
```

JavaScript inline executável foi removido durante a auditoria.

Também são restringidos, conforme a política atual:

-   objetos;
-   frames;
-   formulários;
-   conexões;
-   demais origens relevantes.

A CSP foi primeiro validada em modo Report-Only e posteriormente ativada
de forma efetiva após testes funcionais.

## 12. Estilos inline

**Status: DECISÃO CONSCIENTE**

`style-src` mantém `'unsafe-inline'`.

A exceção existe porque o produto utiliza estilos dinâmicos legítimos,
incluindo cores de Tags e indicadores visuais.

Eliminar essa exceção exigiria uma refatoração ampla com benefício de
segurança considerado baixo no estágio atual.

A exceção **não se estende a scripts**.

## 13. Dependências frontend remotas

**Status: IMPLEMENTADO / REDUZIDO**

Lucide e Flatpickr deixaram de depender de JavaScript remoto por CDN e
passaram a ser servidos localmente.

Isso reduz a superfície de supply chain em runtime e torna a CSP mais
restritiva.

## 14. Google Fonts

**Status: DECISÃO CONSCIENTE**

Poppins permanece carregada por infraestrutura do Google Fonts.

O risco foi considerado menor que o de JavaScript remoto porque o
recurso é fonte/CSS e não código executável equivalente a scripts.

As origens necessárias são explicitamente autorizadas pela CSP.

A decisão pode ser revista no futuro se houver motivo de privacidade,
disponibilidade ou independência de terceiros.

## 15. Cache de conteúdo autenticado

**Status: IMPLEMENTADO**

Um `AuthenticatedNoCacheMiddleware` aplica política restritiva às
respostas HTML autenticadas.

Diretivas utilizadas incluem:

``` text
private
no-store
no-cache
must-revalidate
```

A finalidade é reduzir persistência indevida de conteúdo privado em
caches e dispositivos compartilhados.

O comportamento foi validado por inspeção real dos headers.

## 16. Segurança de tokens

**Status: IMPLEMENTADO + GATE OPERACIONAL**

Ativação e troca de e-mail utilizam tokens assinados com salts próprios
e expiração.

O reset de senha utiliza os mecanismos apropriados do Django.

Tokens não são tratados como identificadores permanentes.

### URLs

Tokens aparecem em URLs nesses fluxos.

Isso é tecnicamente esperado, mas cria requisitos operacionais de
produção:

-   HTTPS;
-   cuidado com access logs;
-   cuidado com observabilidade;
-   cuidado com analytics;
-   evitar registro indiscriminado de URLs completas.

## 17. Mudança de estado via links GET

**Status: DECISÃO CONSCIENTE**

Ativação de conta e confirmação de troca de e-mail atualmente alteram
estado por GET ao acessar um token secreto válido.

O padrão foi aceito para o MVP.

A decisão deverá ser reavaliada se prefetchers, scanners de segurança de
e-mail ou intermediários demonstrarem executar esses links de maneira
problemática.

Não foi adicionada uma etapa POST apenas por formalismo.

## 18. Troca de e-mail

**Status: IMPLEMENTADO**

A operação exige usuário autenticado e confirmação da senha atual.

O novo endereço precisa ser confirmado antes de substituir o endereço
existente.

Tokens validam também o estado esperado da conta, reduzindo risco de uma
solicitação antiga sobrescrever alteração posterior.

Após mudança válida, o endereço anterior recebe notificação.

## 19. Senhas

**Status: IMPLEMENTADO COM FRAMEWORK**

Senhas são tratadas pelos mecanismos do Django.

O TeachFlow não armazena senha em texto puro nem implementa algoritmo
próprio de hashing.

Cadastro, autenticação, alteração e recuperação utilizam os componentes
apropriados do framework.

A política final de senha deverá continuar fazendo parte da revisão de
pré-produção.

## 20. Logout

**Status: IMPLEMENTADO**

O fluxo de logout foi revisado para manter uma operação explícita e
protegida de encerramento da sessão.

A interface não deve depender de uma simples navegação insegura para
produzir efeitos mutáveis quando isso contrariar as proteções definidas
para o fluxo.

## 21. Sessões e cookies

**Status: IMPLEMENTADO EM DESENVOLVIMENTO / GATE DE PRODUÇÃO**

A aplicação utiliza sessões Django.

A configuração de desenvolvimento não deve ser confundida com a
configuração de produção.

Antes do lançamento serão obrigatórios:

``` text
HTTPS
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
configuração correta de proxy
origens confiáveis revisadas
```

Demais parâmetros de sessão devem ser validados no ambiente real.

## 22. HTTPS

**Status: GATE DE PRODUÇÃO**

Produção deverá operar exclusivamente sobre HTTPS.

Isso protege:

-   credenciais;
-   cookies;
-   tokens em URLs;
-   conteúdo privado em trânsito.

Redirecionamento HTTPS e interpretação de protocolo encaminhado pelo
proxy deverão ser configurados conforme a infraestrutura escolhida.

## 23. HSTS

**Status: GATE DE PRODUÇÃO**

HSTS permanece desativado no desenvolvimento.

Ele será habilitado somente depois que HTTPS estiver corretamente
configurado e validado.

A ativação deve ser gradual e consciente, especialmente antes de
utilizar:

-   `includeSubDomains`;
-   preload;
-   períodos longos.

Uma configuração incorreta de HSTS pode causar indisponibilidade difícil
de reverter pelo navegador.

## 24. Secrets

**Status: IMPLEMENTADO COMO POLÍTICA + GATE OPERACIONAL**

Secrets reais não devem ser versionados.

A configuração é feita por variáveis de ambiente.

`.env.example` documenta as variáveis esperadas sem conter credenciais.

A verificação realizada durante a auditoria não encontrou `.env`
versionado no histórico consultado.

Produção deverá fornecer secrets pelo mecanismo seguro da infraestrutura
escolhida.

## 25. Configuração de e-mail

**Status: IMPLEMENTADO POR AMBIENTE / GATE DE PRODUÇÃO**

O backend de e-mail é parametrizado.

Desenvolvimento pode utilizar `ConsoleEmailBackend`.

Produção deverá utilizar provedor real e não poderá subir
inadvertidamente com backend de console.

Credenciais de SMTP/provedor serão fornecidas pelo ambiente.

## 26. Logs

**Status: REVISADO + GATE OPERACIONAL**

Os pontos explícitos de logging do backend foram revisados com foco em
não registrar:

-   senhas;
-   tokens;
-   payloads completos;
-   dados sensíveis desnecessários.

Os `console.error()` do JavaScript próprio também foram revisados sem
identificação de exposição relevante.

Produção exigirá revisão adicional da cadeia inteira de logs, incluindo
componentes fora do Django.

## 27. Observabilidade

**Status: GATE DE PRODUÇÃO**

A ferramenta definitiva ainda não foi escolhida.

Antes do lançamento, a observabilidade deverá ser configurada com
política de minimização de dados.

Especial atenção será dada a:

-   URLs contendo tokens;
-   headers;
-   payloads;
-   dados pessoais;
-   stack traces;
-   integração com serviços terceiros.

## 28. Integridade no banco

**Status: IMPLEMENTADO**

Invariantes estruturais relevantes são protegidas também no banco quando
apropriado.

Exemplos incluem:

-   unicidades case-insensitive;
-   unicidade de `LessonExercise`;
-   limites para ano de turma;
-   limites para duração de exercício.

Essa camada reduz a dependência exclusiva de validações em formulário.

## 29. Concorrência em `LessonExercise`

**Status: GATE POSTGRESQL**

A aplicação utiliza transações nos fluxos relevantes, mas a auditoria
identificou necessidade de proteção/testes adicionais contra
concorrência real na sincronização de `LessonExercise`.

Esse trabalho foi conscientemente adiado para PostgreSQL.

A solução poderá envolver mecanismos como locking de linhas e testes
concorrentes reais, escolhidos após validação do comportamento no banco
de produção.

Não será criada implementação provisória específica para SQLite.

## 30. Corrida entre exclusão e associação de Tag/Objetivo

**Status: GATE POSTGRESQL**

Existe também um cenário concorrente entre:

``` text
transação A → exclusão de Tag/Objetivo
transação B → criação simultânea de nova associação
```

A revisão definitiva será feita com PostgreSQL e controle transacional
apropriado.

O ponto permanece explicitamente registrado como requisito pré-produção.

## 31. Dependências Python

**Status: AUDITADO**

Durante a auditoria de supply chain:

-   Django foi atualizado dentro da série 5.2;
-   `sqlparse` foi atualizado após vulnerabilidades conhecidas;
-   `django-axes` foi atualizado para versão compatível com Django 5.2;
-   a árvore Python declarada foi verificada com `pip-audit`.

Após as adequações, a auditoria utilizada não encontrou vulnerabilidades
conhecidas nas dependências declaradas.

Isso representa o estado da auditoria naquele momento, não uma garantia
permanente. Dependências precisam ser reavaliadas continuamente.

## 32. Dependências Node

**Status: AUDITADO**

A árvore Node passou por `npm audit` e correções não destrutivas.

Após os ajustes:

``` text
npm audit
npm audit --omit=dev
```

não reportaram vulnerabilidades conhecidas no momento da revisão.

Warnings de manutenção sem vulnerabilidade conhecida foram
deliberadamente separados de problemas de segurança.

## 33. Política de atualização

**Status: DECISÃO CONSCIENTE**

O projeto não atualiza dependências apenas porque uma versão mais nova
existe.

A decisão considera:

-   vulnerabilidade;
-   compatibilidade;
-   suporte;
-   benefício;
-   risco de regressão.

Major upgrades sem necessidade concreta não são tratados como hardening
automático.

## 34. PostgreSQL

**Status: GATE DE PRODUÇÃO**

SQLite permanece como banco de desenvolvimento.

PostgreSQL é obrigatório para produção.

Além da migração dos dados, essa etapa inclui:

-   validação das migrations;
-   constraints;
-   comportamento transacional;
-   testes concorrentes;
-   performance dos principais querysets;
-   estratégia de backup.

## 35. Backups

**Status: GATE DE PRODUÇÃO**

Produção deverá possuir backups automatizados.

Entretanto, possuir arquivos de backup não é suficiente.

Antes de receber dados relevantes será necessário executar **teste real
de restauração**.

A capacidade de recuperação é a garantia importante, não apenas a
existência de uma rotina de cópia.

## 36. Arquivos estáticos e servidor

**Status: GATE DE PRODUÇÃO**

A estratégia definitiva dependerá da infraestrutura escolhida.

Antes do lançamento deverão estar definidos e testados:

-   processo WSGI/ASGI;
-   servidor/reverse proxy quando aplicável;
-   coleta e entrega de static files;
-   headers;
-   HTTPS;
-   comportamento em reinício e falhas.

## 37. `check --deploy`

**Status: GATE DE PRODUÇÃO**

A preparação final deverá executar:

``` text
python manage.py check --deploy
```

Os avisos precisam ser interpretados no contexto do ambiente real, e não
apenas ignorados para obter saída limpa.

## 38. Fail-safe de configuração

**Status: GATE DE PRODUÇÃO**

O projeto deverá impedir que um ambiente identificado como produção suba
com condições reconhecidamente inseguras.

Entre os cenários a bloquear ou validar explicitamente estão:

``` text
DEBUG=True
SQLite
cookies inseguros
backend de e-mail de console
configuração inconsistente de HTTPS/proxy
```

A intenção é transformar requisitos de produção em garantias
executáveis, não depender apenas de checklist humano.

## 39. Segurança financeira futura

**Status: CONTRATO ARQUITETURAL**

A integração financeira ainda não foi implementada, mas seus limites de
confiança já foram definidos.

### Regras obrigatórias

``` text
toda conta nasce Free
e-mail confirmado antes de contratar Pro
frontend não promove conta
redirect de checkout não promove conta
gateway/webhook autenticado é fonte externa de verdade
processamento idempotente
processamento transacional
eventos fora de ordem precisam ser tolerados
dados de cartão não são armazenados
secrets financeiros ficam no ambiente
```

Esses requisitos deverão orientar a escolha e a implementação do
gateway.

## 40. CSP e futuras integrações

Qualquer futura integração de terceiros que exija scripts, frames ou
conexões adicionais deverá justificar explicitamente a ampliação da CSP.

A política não deve ser relaxada globalmente apenas para fazer uma
integração funcionar.

Novas origens deverão ser mínimas e específicas.

## 41. Segurança versus regras de produto

Nem toda restrição adicional representa melhoria de segurança.

Durante a auditoria, o projeto evitou transformar preferências
institucionais em bloqueios artificiais ao professor.

O critério utilizado é distinguir:

``` text
integridade / autorização / segurança
de
fiscalização desnecessária da atividade docente
```

Isso preserva a filosofia do produto sem abrir mão das fronteiras
técnicas que realmente precisam ser rígidas.

## 42. Checklist consolidada de pré-produção

Antes da exposição do TeachFlow a usuários reais, deverão ser
revalidados pelo menos:

-   PostgreSQL;
-   cenários concorrentes do Bloco 6;
-   HTTPS;
-   cookies Secure;
-   proxy e forwarded protocol;
-   HSTS após validação de HTTPS;
-   domínio e origens confiáveis;
-   provedor de e-mail;
-   política de logs para URLs com tokens;
-   observabilidade;
-   backups;
-   teste de restauração;
-   servidor de aplicação;
-   static files;
-   secrets;
-   `check --deploy`;
-   fail-safe de produção;
-   auditoria atualizada de dependências;
-   regressão de autenticação e Axes;
-   política de senha;
-   integração financeira, quando existir.

## 43. Estado atual

A auditoria transversal permitiu eliminar vulnerabilidades e
configurações inconsistentes conhecidas no estágio atual, além de
registrar explicitamente o que depende do ambiente futuro.

O resultado pretendido não é declarar o sistema "seguro para sempre",
mas manter uma cadeia verificável:

``` text
ameaça identificada
→ controle implementado
ou
→ decisão justificada
ou
→ gate explícito antes de produção
```

Essa classificação deverá continuar sendo utilizada nas próximas fases
do TeachFlow.
