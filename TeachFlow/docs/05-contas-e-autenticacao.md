# Contas e Autenticação do TeachFlow

## 1. Objetivo

Este documento descreve a arquitetura e os fluxos atuais de identidade,
cadastro, autenticação, recuperação de acesso e gerenciamento da conta
no TeachFlow.

A área de contas foi projetada para permitir que o professor crie e
mantenha sua própria conta utilizando fluxos tradicionais de uma
aplicação web por assinatura, sem delegar ao frontend decisões de
autenticação, verificação de e-mail ou estado financeiro.

As regras financeiras propriamente ditas são tratadas separadamente em
`11-assinaturas-e-pagamentos.md`.

## 2. Componentes principais

A implementação está concentrada no app `accounts`.

``` text
accounts/
├── models
├── forms
├── views
├── urls
├── backends
├── tokens
├── emails
├── utils
├── middleware
└── admin
```

A interface correspondente utiliza templates Django e JavaScript apenas
onde necessário para experiência de uso.

## 3. Identidade do usuário

O TeachFlow utiliza um `CustomUser`.

A identidade da conta é separada do perfil profissional:

``` text
CustomUser
    |
    └── 1:1 Teacher
```

`CustomUser` concentra autenticação e estado da conta.

`Teacher` representa o professor dentro do domínio da aplicação.

Essa separação evita misturar credenciais e atributos de autenticação
com as entidades pedagógicas pertencentes ao professor.

## 4. Username e e-mail

O usuário possui dois identificadores relevantes:

-   username;
-   e-mail.

Ambos possuem proteção de unicidade case-insensitive.

Além disso:

``` text
username não pode conter "@"
```

Essa regra é importante porque o login aceita tanto username quanto
e-mail. A ausência de `@` no namespace de usernames elimina uma fonte de
ambiguidade na interpretação do identificador informado.

Normalizações são centralizadas para que cadastro, login e demais fluxos
não implementem regras divergentes.

## 5. Cadastro

O cadastro cria a estrutura básica necessária para uma nova conta.

Fluxo conceitual:

``` mermaid
flowchart TD
    A[Usuário preenche cadastro] --> B[Validação dos dados]
    B -->|inválido| A
    B -->|válido| C[Criação transacional]
    C --> D[CustomUser]
    C --> E[Teacher]
    C --> F[Subscription Free]
    C --> G[Envio da ativação]
    G --> H[Tela de verificação de e-mail]
```

Toda conta comum nasce no plano Free.

A criação das entidades relacionadas faz parte do mesmo fluxo
transacional, evitando contas parcialmente inicializadas.

## 6. Estado inicial da conta

Uma conta comum recém-criada ainda não está pronta para autenticação
normal.

Conceitualmente:

``` text
cadastro concluído
→ conta ainda não verificada
→ e-mail de ativação
→ confirmação válida
→ conta ativa
```

O TeachFlow utiliza `email_verified_at` para registrar explicitamente
quando o endereço foi confirmado.

Isso separa o conceito de endereço verificado de inferências frágeis
baseadas apenas em outros campos.

## 7. Ativação por e-mail

A ativação utiliza token assinado e temporário.

O link é enviado para o endereço cadastrado e contém o token necessário
para validar a operação.

``` mermaid
sequenceDiagram
    participant U as Usuário
    participant T as TeachFlow
    participant E as E-mail

    U->>T: Realiza cadastro
    T->>E: Envia link de ativação
    E-->>U: Entrega link
    U->>T: Abre link com token
    T->>T: Valida token e estado da conta
    T-->>U: Ativa conta ou informa falha
```

O token de ativação é vinculado ao estado esperado da conta e possui
expiração.

Após confirmação válida:

-   a conta é ativada;
-   `email_verified_at` é preenchido;
-   o usuário pode seguir para autenticação normal.

## 8. Reenvio da ativação

Existe fluxo específico para reenvio do e-mail de ativação.

Esse endpoint foi projetado para evitar que o comportamento da interface
revele desnecessariamente se determinado endereço possui ou não uma
conta utilizável.

Também existem limites de requisição para reduzir abuso de envio de
e-mails.

A aplicação trata falhas de envio sem expor detalhes internos ao
usuário.

## 9. Falhas de e-mail

O envio de e-mail é uma operação externa e pode falhar.

O módulo diferencia:

``` text
estado persistido da conta
versus
entrega do e-mail
```

Falhas relevantes são registradas pelo backend para diagnóstico,
enquanto a resposta ao usuário evita exposição de stack traces,
credenciais ou detalhes internos.

A configuração real do provedor de e-mail será definida no ambiente de
produção.

## 10. Login

O login aceita:

``` text
username
ou
e-mail
```

O backend próprio de autenticação interpreta e normaliza o identificador
informado.

A senha continua sendo validada pelos mecanismos de autenticação do
Django.

O sistema não implementa autenticação no frontend nem mantém credenciais
em JavaScript.

## 11. Sessões

O TeachFlow utiliza autenticação baseada em sessão do Django.

Após login válido:

``` text
credenciais
→ autenticação no backend
→ sessão Django
→ cookie de sessão
```

Não existe dependência de JWT ou token de autenticação persistido em
`localStorage` para a navegação normal da aplicação.

A configuração definitiva dos cookies para produção faz parte dos gates
de deploy e deverá utilizar HTTPS e atributos seguros apropriados.

## 12. Proteção contra brute force

O fluxo de login é protegido por `django-axes`.

A proteção foi validada funcionalmente durante a auditoria:

-   tentativas inválidas são contabilizadas;
-   o lockout é efetivamente aplicado;
-   senha correta não contorna um lockout ainda vigente;
-   após o período de liberação, o login volta a funcionar normalmente.

A resposta de lockout utiliza uma tela controlada pelo TeachFlow em vez
de expor comportamento interno da biblioteca.

## 13. Rate limiting de fluxos sensíveis

Além do Axes no login, `django-ratelimit` é utilizado em operações
específicas sujeitas a abuso.

Entre os fluxos protegidos estão operações como:

-   cadastro;
-   reenvio de ativação;
-   recuperação de senha;
-   solicitação de troca de e-mail.

Os limites podem considerar IP, e-mail normalizado ou usuário
autenticado conforme a natureza da operação.

A finalidade não é substituir autenticação ou autorização, mas reduzir
automação abusiva e uso indevido de recursos como envio de e-mail.

## 14. Recuperação de senha

A recuperação utiliza o fluxo seguro de reset de senha do ecossistema
Django, com customizações do TeachFlow para interface e controles
adicionais.

Fluxo:

``` mermaid
flowchart LR
    A[Solicitação] --> B[Resposta neutra]
    B --> C[E-mail de recuperação]
    C --> D[Link temporário]
    D --> E[Definição da nova senha]
    E --> F[Conclusão]
```

A resposta ao pedido de recuperação evita transformar o endpoint em
mecanismo simples de enumeração de contas.

O envio também possui proteção contra abuso.

## 15. Perfil

A área de perfil permite ao professor administrar informações da própria
conta.

Ela concentra atualmente responsabilidades como:

-   dados pessoais utilizados pelo produto;
-   username;
-   visualização do e-mail;
-   alteração de senha;
-   acesso ao fluxo de troca de e-mail;
-   apresentação do plano atual.

Dados que não possuíam função real no TeachFlow foram removidos do
modelo em vez de serem mantidos preventivamente.

## 16. Alteração de dados do perfil

Mudanças de perfil passam por formulários do backend.

As regras de username e demais identidades são reaproveitadas em vez de
duplicadas na interface.

A view também diferencia os formulários submetidos na página, permitindo
que cada operação seja validada segundo sua responsabilidade.

## 17. Alteração de senha

A troca de senha de um usuário autenticado utiliza os mecanismos de
validação de senha do Django.

A operação exige conhecimento da senha atual conforme o fluxo
configurado e mantém a sessão de maneira controlada após alteração
válida.

As políticas gerais de senha pertencem à configuração de autenticação do
projeto e devem continuar sendo revisadas antes da exposição pública.

## 18. Troca de e-mail

Trocar o endereço de e-mail é tratado como operação sensível.

O novo endereço não substitui imediatamente o endereço confirmado atual.

Fluxo conceitual:

``` mermaid
flowchart TD
    A[Usuário autenticado] --> B[Informa novo e-mail]
    B --> C[Confirma senha atual]
    C --> D[Validação de unicidade]
    D --> E[Token para o novo endereço]
    E --> F[Usuário abre confirmação]
    F --> G[Backend valida token e estado atual]
    G --> H[E-mail da conta é alterado]
    H --> I[Endereço anterior é notificado]
```

A confirmação exige que o usuário esteja autenticado.

## 19. Proteção contra token antigo na troca de e-mail

O token de troca não representa autorização eterna para substituir o
endereço.

Ele carrega informação suficiente para verificar o estado da conta
esperado no momento da solicitação.

Se o estado relevante já tiver mudado, uma confirmação antiga não deve
sobrescrever silenciosamente uma alteração mais recente.

Isso reduz riscos de links antigos ou fluxos concorrentes alterarem a
conta para um estado inesperado.

## 20. Confirmação por GET

Ativação de conta e confirmação de troca de e-mail atualmente alteram
estado ao acessar links contendo tokens secretos.

Essa decisão foi aceita conscientemente para o MVP.

Não existe neste momento uma etapa POST intermediária apenas para
confirmar a operação.

O padrão deverá ser reavaliado se scanners, sistemas de segurança ou
prefetchers de clientes de e-mail demonstrarem causar efeitos
indesejados.

## 21. Tokens em URLs

Tokens de:

-   ativação;
-   recuperação de senha;
-   troca de e-mail

aparecem em URLs como parte normal desses fluxos.

Isso cria requisitos operacionais importantes para produção:

-   HTTPS obrigatório;
-   evitar logging indiscriminado de URLs sensíveis;
-   revisar access logs de proxy;
-   revisar ferramentas de observabilidade;
-   evitar analytics de terceiros nessas páginas.

A segurança do fluxo não termina na validação criptográfica do token.

## 22. Logout

Logout é tratado como operação explícita de encerramento da sessão.

O fluxo foi revisado durante a auditoria para manter a semântica correta
da operação e as proteções esperadas contra requisições indevidas.

Após o logout, o usuário deixa de possuir a sessão autenticada utilizada
pelas áreas privadas do sistema.

## 23. Superusuários

Superusuários possuem finalidade administrativa.

Ao entrar pelo fluxo da aplicação, são direcionados ao Django Admin em
vez de serem tratados como professores comuns sem perfil pedagógico
correspondente.

Isso separa administração técnica do produto da experiência normal do
professor.

## 24. Django Admin

Os modelos relevantes da área de contas são integrados ao Django Admin
de maneira compatível com o `CustomUser`.

O Admin é uma ferramenta administrativa, não uma interface alternativa
destinada ao usuário final.

## 25. Proteção CSRF

Formulários e operações mutáveis seguem as proteções CSRF do Django.

Views sensíveis que recebem POST mantêm proteção explícita ou inerente à
pilha padrão do framework.

JavaScript não é tratado como fronteira de confiança.

## 26. Cache de páginas autenticadas

Respostas HTML autenticadas recebem política restritiva de cache por
middleware.

A intenção é reduzir a permanência de conteúdo privado em caches
intermediários ou no navegador, especialmente em dispositivos
compartilhados.

A política inclui diretivas equivalentes a:

``` text
private
no-store
no-cache
must-revalidate
```

## 27. Relação com o plano Free/Pro

Conta e assinatura são conceitos relacionados, mas possuem autoridades
diferentes.

No cadastro:

``` text
nova conta → Free
```

O frontend não pode enviar um parâmetro capaz de criar diretamente uma
conta Pro.

No futuro:

``` text
conta com e-mail confirmado
→ checkout
→ gateway
→ webhook autenticado
→ atualização do estado financeiro
```

A confirmação do pagamento não será derivada de redirect do navegador.

## 28. Dados de pagamento

O módulo de conta não armazena dados de cartão.

Quando o fluxo financeiro for implementado, informações sensíveis de
pagamento permanecerão sob responsabilidade do provedor especializado.

O TeachFlow armazenará apenas os identificadores e estados estritamente
necessários à integração.

## 29. Configuração de e-mail por ambiente

O backend de e-mail não é fixado no código para todos os ambientes.

Em desenvolvimento, o projeto pode utilizar backend de console.

Produção deverá fornecer por variáveis de ambiente:

-   backend;
-   host;
-   porta;
-   TLS/SSL;
-   usuário;
-   senha;
-   remetente.

Credenciais reais não pertencem ao repositório.

## 30. Responsabilidades adiadas

Os seguintes itens dependem de fases futuras e não devem ser confundidos
com funcionalidades atuais:

-   gateway de pagamento;
-   checkout;
-   webhooks financeiros;
-   máquina definitiva de estados da assinatura;
-   política definitiva de exclusão da conta associada a
    retenção/cancelamento;
-   configuração do provedor real de e-mail;
-   parâmetros finais de sessão e cookies de produção;
-   domínio público definitivo.

## 31. Garantias pretendidas

O módulo procura garantir que:

``` text
identidade seja normalizada
e-mail seja verificável
credenciais sejam processadas pelo backend
brute force seja limitado
operações de e-mail não sejam facilmente abusáveis
mudanças sensíveis exijam prova apropriada
tokens sejam temporários
dados financeiros não sejam confiados ao navegador
```

Essas garantias são complementadas pelos controles transversais
descritos em `06-seguranca.md`.
