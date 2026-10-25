# Decisões Arquiteturais do TeachFlow

## 1. Propósito e escopo

Este documento registra **por que** o TeachFlow adotou suas principais soluções. Complementa a descrição técnica de `02-arquitetura.md`, o modelo de dados de `03-modelo-de-dados.md` e as regras funcionais de `04-modulos-e-regras-de-negocio.md`.

Cada registro apresenta contexto, alternativas consideradas, decisão, justificativa e consequências. As alternativas são apresentadas como opções de arquitetura relevantes para compreender a escolha, **não necessariamente como protótipos efetivamente implementados**. O histórico de auditorias é a fonte para as decisões descritas; este documento não substitui uma verificação da versão atual do repositório.

**Legenda:** `Adotada` = decisão incorporada ao MVP; `Planejada` = contrato ou direção aprovada, ainda dependente de implementação; `Gate` = condição obrigatória antes de produção.

## ADR-001 — Produto centrado no diário do professor

**Estado:** Adotada.

**Contexto:** A organização pedagógica precisa de estrutura e histórico, mas não necessariamente de mecanismos institucionais de aprovação e fiscalização.

**Alternativas:** (a) fluxo prescritivo e fiscalizador; (b) espaço pessoal com regras de integridade objetivas.

**Decisão:** Construir um diário de trabalho do professor. O sistema organiza, registra e protege o histórico sem bloquear escolhas pedagógicas legítimas apenas por serem incomuns.

**Justificativa:** A ferramenta deve apoiar o profissional, não substituir sua autonomia.

**Consequências:** Validações precisam distinguir inconsistências objetivas de decisões do usuário. Exemplo: impedir aula marcada como realizada em data futura, sem impor um processo de aprovação institucional.

## ADR-002 — Django com renderização no servidor

**Estado:** Adotada.

**Contexto:** O MVP exige autenticação, CRUDs, formulários, regras de domínio e telas administrativas, com uma equipe e operação enxutas.

**Alternativas:** SPA com API separada; aplicação Django renderizada no servidor com JavaScript progressivo.

**Decisão:** Django, Django Templates, Tailwind CSS e JavaScript localizado por funcionalidade.

**Justificativa:** Reduz complexidade de integração, preserva as proteções do framework e mantém um fluxo simples de desenvolvimento.

**Consequências:** O backend permanece a fonte de verdade. Interações assíncronas são usadas quando melhoram a experiência, não como requisito para toda a navegação.

## ADR-003 — Separar identidade de domínio pedagógico

**Estado:** Adotada.

**Contexto:** Credenciais, verificação de e-mail e assinatura pertencem ao ciclo da conta; turmas, aulas e exercícios pertencem ao trabalho do professor.

**Alternativas:** concentrar todos os dados em um usuário; separar `CustomUser` e `Teacher`.

**Decisão:** Manter `CustomUser` para identidade/autenticação e `Teacher` como perfil e raiz de ownership pedagógico.

**Justificativa:** Evita acoplamento indevido entre autenticação e domínio funcional.

**Consequências:** Views e formulários devem validar consistentemente a relação com o professor autenticado.

## ADR-004 — Isolamento de dados por ownership no backend

**Estado:** Adotada.

**Contexto:** O sistema atende múltiplos professores; IDs em URLs ou requisições não podem permitir acesso cruzado.

**Alternativas:** confiar na ocultação de IDs e filtros visuais; restringir consultas e associações no servidor.

**Decisão:** Aplicar ownership nos querysets, nas operações e na validação dos relacionamentos.

**Justificativa:** Autorização não pode depender do navegador.

**Consequências:** Testes devem incluir acesso indevido entre professores, inclusive em endpoints assíncronos e POSTs com IDs manipulados.

## ADR-005 — Histórico preservado por arquivamento

**Estado:** Adotada.

**Contexto:** Uma Tag, um Objetivo, uma turma ou um exercício pode deixar de ser usado sem perder valor histórico.

**Alternativas:** exclusão ampla; impedir toda exclusão; arquivar quando houver necessidade de preservação.

**Decisão:** Diferenciar recurso ativo, arquivado e exclusão definitiva conforme o relacionamento e a regra do domínio.

**Justificativa:** O histórico é um ativo central do produto.

**Consequências:** Recursos arquivados podem permanecer em vínculos antigos e normalmente não são oferecidos para novos vínculos. Editar registros históricos não deve apagá-los silenciosamente.

## ADR-006 — Relação explícita `LessonExercise`

**Estado:** Adotada; concorrência adicional é Gate PostgreSQL.

**Contexto:** Aplicar um exercício é um fato específico de determinada aula.

**Alternativas:** estado global no exercício; relação many-to-many simples; entidade intermediária com estado próprio.

**Decisão:** Utilizar `LessonExercise`, incluindo `is_applied` por associação e unicidade do par aula/exercício.

**Justificativa:** O mesmo exercício pode ser aplicado em uma aula e não em outra.

**Consequências:** O progresso é derivado dos vínculos. Cenários concorrentes de sincronização serão revisitados e testados em PostgreSQL antes da produção.

## ADR-007 — Objetivos associados aos exercícios, não diretamente às aulas

**Estado:** Adotada.

**Contexto:** A relação direta de Objetivos com Aulas passou a duplicar informação já representada nos Exercícios.

**Alternativas:** manter duas associações; derivar Objetivos da aula por meio de seus Exercícios.

**Decisão:** Remover a relação direta Aula–Objetivo.

**Justificativa:** Reduz fontes de verdade conflitantes.

**Consequências:** A apresentação de Objetivos em uma aula deve considerar seus exercícios associados.

## ADR-008 — Remover `FutureIdea` do MVP

**Estado:** Adotada.

**Contexto:** O planejamento de aulas evoluiu e passou a cobrir a necessidade antes atendida pelo módulo de Ideias Futuras.

**Alternativas:** manter o módulo separado; integrar a necessidade ao fluxo de aulas.

**Decisão:** Remover `FutureIdea`.

**Justificativa:** Evitar redundância de produto e manutenção.

**Consequências:** Não apresentar Ideias Futuras como módulo atual no README, na navegação ou na documentação funcional.

## ADR-009 — Tags universais

**Estado:** Adotada.

**Contexto:** A classificação de Tags por tipo acrescentava rigidez e duplicação.

**Alternativas:** manter `Tag.type`; utilizar uma Tag reutilizável em contextos permitidos.

**Decisão:** Eliminar `Tag.type` e tornar Tags universais.

**Justificativa:** Flexibilidade com modelo mais simples.

**Consequências:** A identidade da Tag passa a depender de professor + nome, sem distinção por tipo.

## ADR-010 — Unicidade e normalização centralizadas

**Estado:** Adotada.

**Contexto:** Formulários tradicionais e criação rápida não devem aceitar grafias equivalentes como entidades distintas.

**Alternativas:** normalização em cada view; validação central e constraints para invariantes persistentes.

**Decisão:** Centralizar normalização e aplicar unicidade case-insensitive por professor para Tags e Objetivos.

**Justificativa:** Consistência entre fluxos e proteção contra condições de corrida na criação.

**Consequências:** Recursos arquivados continuam participando da identidade lógica; reativar pode ser preferível a duplicar.

## ADR-011 — Modelos de exercício como facilitadores independentes

**Estado:** Adotada.

**Contexto:** O professor usa modelos para acelerar a criação, não para manter cópias permanentemente subordinadas ao original.

**Alternativas:** vínculo rígido e exclusão bloqueada; cópias independentes com referência opcional à origem.

**Decisão:** `Exercise.source_template` com comportamento `SET_NULL` quando o modelo é removido.

**Justificativa:** Preservar cópias sem engessar a biblioteca.

**Consequências:** É permitido excluir modelo com cópias; exercícios já vinculados a aulas continuam protegidos contra exclusão indevida.

## ADR-012 — Constraints para invariantes objetivas

**Estado:** Adotada.

**Contexto:** Validações apenas de formulário não protegem escritas diretas no banco.

**Alternativas:** depender só do frontend; validar apenas na aplicação; combinar aplicação e banco.

**Decisão:** Usar constraints para invariantes estáveis, como `ClassGroup.year` entre 2000–2100 e `Exercise.duration` entre 1–1440 ou nulo.

**Justificativa:** Defesa em profundidade sem levar regras contextuais para constraints inadequadas.

**Consequências:** Testes devem incluir escrita direta inválida no banco.

## ADR-013 — Autenticação com confirmação de e-mail

**Estado:** Adotada.

**Contexto:** Contas reais e futura contratação exigem controle consistente da identidade de contato.

**Alternativas:** ativação imediata sem verificação; confirmação antes de uso normal.

**Decisão:** Contas comuns são ativadas após confirmação do e-mail, registrada por `email_verified_at`.

**Justificativa:** Evita tratar endereço não verificado como identidade confirmada.

**Consequências:** Cadastro, reenvio e ativação precisam tratar falhas de entrega e tokens expirados.

## ADR-014 — Login por username ou e-mail sem ambiguidade

**Estado:** Adotada.

**Contexto:** O login aceita dois identificadores.

**Alternativas:** aceitar qualquer caractere em username; reservar `@` para e-mail.

**Decisão:** Username não pode conter `@`; ambos os identificadores possuem unicidade case-insensitive.

**Justificativa:** Simplificar a resolução do identificador no backend.

**Consequências:** Cadastro, edição de perfil e autenticação devem compartilhar as regras.

## ADR-015 — Defesa em camadas contra abuso de autenticação

**Estado:** Adotada.

**Contexto:** Login e endpoints de envio de e-mail enfrentam abusos diferentes.

**Alternativas:** uma proteção genérica para todos; controles especializados.

**Decisão:** `django-axes` para tentativas de login e `django-ratelimit` para endpoints sensíveis selecionados.

**Justificativa:** Separar lockout de autenticação de limitação de requisições.

**Consequências:** Validar funcionalmente lockout, liberação e comportamento neutro de recuperação/reenvio.

## ADR-016 — CSP efetiva e bibliotecas JavaScript locais

**Estado:** Adotada; exceção CSS é consciente.

**Contexto:** Scripts externos e inline ampliam a superfície de execução.

**Alternativas:** manter CDNs e scripts inline; servir scripts localmente com política restritiva.

**Decisão:** CSP efetiva com `script-src 'self'`; Lucide e Flatpickr locais; inicialização inline externalizada.

**Justificativa:** Menor dependência de execução remota.

**Consequências:** Novas integrações devem justificar origens adicionais. `style-src 'unsafe-inline'` permanece conscientemente para estilos dinâmicos; Google Fonts/Poppins continua permitido.

## ADR-017 — Cache restritivo em HTML autenticado

**Estado:** Adotada.

**Contexto:** Informações privadas podem permanecer em caches após uso da aplicação.

**Alternativas:** headers padrão; middleware dedicado.

**Decisão:** Aplicar `private`, `no-store`, `no-cache` e `must-revalidate` a respostas HTML autenticadas.

**Justificativa:** Reduzir exposição em caches e dispositivos compartilhados.

**Consequências:** Revalidar comportamento em navegadores e infraestrutura real.

## ADR-018 — SQLite local e PostgreSQL em produção

**Estado:** SQLite adotado no desenvolvimento; PostgreSQL é Gate.

**Contexto:** SQLite simplifica o ambiente local, mas a produção exige revalidação transacional e de concorrência.

**Alternativas:** manter SQLite em todos os ambientes; migrar para PostgreSQL no deploy.

**Decisão:** PostgreSQL é obrigatório para produção.

**Justificativa:** Alinhar persistência e testes ao ambiente multiusuário definitivo.

**Consequências:** Reabrir concorrência de `LessonExercise` e corrida entre exclusão de Tag/Objetivo e criação de associações; não introduzir soluções provisórias específicas para SQLite.

## ADR-019 — Free e Pro, sem plano intermediário

**Estado:** Modelo de planos aprovado; operação comercial planejada.

**Contexto:** O produto precisa permitir experimentação e apresentar valor de assinatura sem complexidade excessiva de catálogo.

**Alternativas:** múltiplos níveis; Free e Pro.

**Decisão:** Manter Free e Pro; toda conta nasce Free.

**Justificativa:** Posicionamento comercial simples e expansão controlada.

**Consequências:** Limites e benefícios específicos ainda exigem definição. A interface pode apresentar o valor do Pro, mas não fingir que checkout já existe.

## ADR-020 — Gateway como autoridade externa financeira

**Estado:** Contrato planejado; implementação futura.

**Contexto:** Cobrança e dados de pagamento requerem um provedor especializado.

**Alternativas:** processar pagamentos diretamente; delegar ao gateway e validar notificações.

**Decisão:** Gateway/webhook autenticado será a fonte externa de verdade para pagamento. Frontend e redirecionamento de checkout nunca promovem uma conta a Pro.

**Justificativa:** Reduzir risco e responsabilidade sobre dados financeiros.

**Consequências:** Webhooks devem ser idempotentes, transacionais e tolerar eventos fora de ordem; secrets ficam no ambiente; cartões não são armazenados. O provedor ainda não foi escolhido.

## ADR-021 — Hardening dependente do ambiente como gate, não promessa

**Estado:** Gate.

**Contexto:** HTTPS, proxy, domínio, SMTP, logs, backups e servidor dependem da infraestrutura definitiva.

**Alternativas:** inventar configuração de produção antecipada; parametrizar e exigir validação real antes do lançamento.

**Decisão:** Registrar gates explícitos de pré-produção.

**Justificativa:** Segurança precisa ser testada no ambiente real.

**Consequências:** Validar HTTPS, cookies Secure, HSTS gradual, SMTP, PostgreSQL, backup/restauração, observabilidade, `check --deploy` e fail-safe contra configurações inseguras.

## ADR-022 — Auditoria por fluxo e implementação em etapas

**Estado:** Adotada como prática de desenvolvimento.

**Contexto:** Revisões grandes e mudanças simultâneas dificultam identificar regressões.

**Alternativas:** refatoração ampla; auditoria modular com decisões explícitas e commits de checkpoint.

**Decisão:** Auditar por fluxo, distinguir fato de hipótese, registrar decisões e executar correções em etapas pequenas.

**Justificativa:** Rastreabilidade e redução de risco.

**Consequências:** Cada nova mudança relevante deve indicar arquivo afetado, comportamento esperado, teste e impacto nas decisões anteriores.

## 2. Como manter este registro

Ao mudar uma decisão, registrar a nova escolha e marcar a anterior como substituída; não reescrever a história como se a alternativa nunca tivesse existido. Para decisões ainda planejadas, atualizar o estado somente após implementação e validação no repositório.

## 3. Referências internas

- `01-visao-geral.md` — filosofia do produto e escopo.
- `02-arquitetura.md` — componentes e fronteiras.
- `03-modelo-de-dados.md` — entidades e integridade.
- `04-modulos-e-regras-de-negocio.md` — regras funcionais.
- `05-contas-e-autenticacao.md` — ciclo da conta.
- `06-seguranca.md` — controles e gates.
