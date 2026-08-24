# Aula 03 — Guia de Execução dos Laboratórios

## Engenharia de Contexto, Avaliação e Confiabilidade

Este documento explica o objetivo de cada laboratório, o papel de cada bloco de código e o que
deve ser observado durante a execução.

Notebooks relacionados:

- Aula03_Lab01_Engenharia_de_Contexto.ipynb
- Aula03_Lab02_Avaliacao_e_Confiabilidade.ipynb

## 1. Como usar este guia

Execute os notebooks de cima para baixo. As células dependem de variáveis, funções e objetos
criados nas células anteriores.

Para cada bloco, este guia apresenta:

- **O que o bloco faz:** objetivo técnico;
- **Como funciona:** componentes e decisões importantes;
- **O que observar:** evidências de que o comportamento está correto;
- **Saída esperada:** formato geral do resultado;
- **Erros comuns:** causas prováveis e correções.

## 2. Preparação

### Dependências

Os laboratórios usam:

- LangChain;
- integração do provedor de LLM;
- python-dotenv;
- Pydantic;
- pandas;
- HuggingFace Embeddings;
- sentence-transformers;
- InMemoryVectorStore.

### Provedores reconhecidos

O código aceita:

| Valor de LLM_PROVIDER | Integração | Chave |
|---|---|---|
| anthropic | langchain-anthropic | ANTHROPIC_API_KEY |
| openai | langchain-openai | OPENAI_API_KEY |
| google | langchain-google-genai | GOOGLE_API_KEY |
| xai | langchain-xai | XAI_API_KEY |
| deepseek | langchain-deepseek | DEEPSEEK_API_KEY |

Os nomes dos modelos podem ser definidos em:

- ANTHROPIC_MODEL;
- OPENAI_MODEL;
- GOOGLE_MODEL;
- XAI_MODEL;
- DEEPSEEK_MODEL.

### Cuidados antes de executar

- Não coloque chaves diretamente nas células.
- Confirme se o nome do modelo existe na conta usada.
- O download do modelo de embeddings ocorre na primeira execução.
- Células com várias chamadas estão desativadas para evitar custo acidental.
- Scores e textos produzidos por LLM podem variar.
- Reinicie o kernel depois de instalar ou atualizar dependências.

# Lab 01 — Engenharia de Contexto

## 3. O que o Lab 01 trata

O Lab 01 mostra como controlar o que chega ao modelo. O estudante parte de um prompt vago,
constrói um contrato de tarefa e implementa um RAG com recuperação seletiva.

O laboratório cobre:

- configuração multi-provedor;
- prompts orientados a tarefas;
- documentos e metadados;
- embeddings;
- banco vetorial em memória;
- roteamento por domínio;
- filtros e limiar de similaridade;
- orçamento de contexto;
- isolamento entre instruções e dados;
- resposta com fontes;
- recusa por contexto insuficiente;
- medição de tokens e latência;
- memória estruturada de tentativas.

## 4. Fluxo geral do Lab 01

Pergunta

→ detectar domínio

→ recuperar documentos

→ aplicar filtro e limiar

→ montar contexto dentro do orçamento

→ chamar o modelo

→ validar fontes

→ registrar tentativa

→ responder ou escalar

## 5. Bloco 1 — Instalação das dependências

### O que o bloco faz

Apresenta os comandos para instalar o LangChain, utilitários, embeddings locais e a integração do
provedor escolhido.

### Como funciona

Os comandos estão comentados para não reinstalar pacotes toda vez que o notebook for executado.

Há um grupo comum:

- LangChain;
- python-dotenv;
- pandas;
- langchain-huggingface;
- sentence-transformers.

Depois há uma linha para cada provedor.

### O que observar

- Instale somente as integrações necessárias.
- Verifique se não há conflito entre versões.
- Confirme que o kernel do notebook usa o mesmo ambiente onde os pacotes foram instalados.
- Reinicie o kernel após a instalação.

### Saída esperada

Logs do gerenciador de pacotes e conclusão sem erro.

### Erros comuns

**ModuleNotFoundError:** pacote instalado em outro ambiente.

**Versões incompatíveis:** atualize o conjunto ou recrie o ambiente virtual.

**Kernel antigo:** reinicie o kernel e execute novamente desde o início.

## 6. Bloco 2 — Configuração multi-provedor

### O que o bloco faz

Carrega o arquivo de ambiente, escolhe o provedor e cria o objeto de modelo por meio de
init_chat_model.

### Como funciona

O dicionário PROVIDERS associa cada provedor a:

- identificador usado pelo LangChain;
- variável da chave;
- variável do nome do modelo;
- modelo padrão.

O código tenta usar LLM_PROVIDER. Se ele não estiver definido, seleciona o primeiro provedor com
chave encontrada.

Quando a chave existe:

- cria o modelo;
- fixa temperatura em zero;
- limita tokens de saída;
- configura timeout;
- permite duas tentativas internas;
- define EXECUTAR_LLM como verdadeiro.

Sem chave:

- llm recebe None;
- EXECUTAR_LLM fica falso;
- o notebook continua nas partes determinísticas.

### O que observar

- Qual provedor foi selecionado.
- Qual modelo foi carregado.
- Se a escolha automática corresponde à chave esperada.
- Se modelos e chaves continuam fora do código.
- Temperatura zero reduz variabilidade, mas não garante respostas idênticas.

### Saída esperada

Com chave:

> Provedor: nome | modelo: identificador

Sem chave:

> Defina a variável da chave no arquivo de ambiente.

### Erros comuns

**LLM_PROVIDER inválido:** use anthropic, openai, google, xai ou deepseek.

**Pacote de integração ausente:** instale o pacote correspondente.

**Modelo inexistente:** altere a variável de modelo no arquivo de ambiente.

**Chave inválida:** gere ou copie novamente a credencial sem espaços.

## 7. Bloco 3 — Teste básico do LLM

### O que o bloco faz

Faz uma chamada curta para verificar credencial, modelo e integração.

### Como funciona

Se EXECUTAR_LLM for verdadeiro, o modelo recebe a instrução para responder com uma frase fixa.
Depois são exibidos conteúdo e usage_metadata.

### O que observar

- A resposta deve ser curta e próxima do texto solicitado.
- usage_metadata pode trazer tokens de entrada, saída e total.
- A estrutura dos metadados pode variar por provedor.
- Uma chamada simples valida conectividade, não qualidade do sistema.

### Saída esperada

Uma confirmação textual e um dicionário de uso.

### Erros comuns

**401 ou authentication error:** chave ausente ou inválida.

**404 ou model not found:** identificador do modelo incorreto.

**Rate limit:** aguarde ou troque de modelo/conta.

**Timeout:** verifique conectividade e disponibilidade do provedor.

## 8. Bloco 4 — Construção dos prompts

### O que o bloco faz

Cria uma versão vaga e uma versão orientada à tarefa usando ChatPromptTemplate.

Também define:

- a função executar_prompt;
- um incidente de exemplo;
- StrOutputParser para extrair apenas o texto.

### Como funciona

O prompt vago informa apenas que o modelo é um assistente útil.

O prompt orientado define:

- papel de analista SRE;
- objetivo;
- regras sobre fatos e hipóteses;
- limite de perguntas;
- proibição de ações destrutivas sem revisão;
- formato da resposta.

O operador de composição do LangChain conecta prompt, modelo e parser.

### O que observar

- A versão orientada torna o comportamento esperado mais verificável.
- O formato pode ser inspecionado visualmente.
- As regras reduzem ambiguidades, mas ainda precisam de validação por código quando forem críticas.
- O parser remove metadados da mensagem e retorna somente texto.

### Saída esperada

Este bloco apenas cria objetos e funções. Não há resposta do modelo ainda.

### Erros comuns

**llm é None:** configure uma chave antes de chamar executar_prompt.

**Variável ausente no template:** confirme que incidente foi fornecido.

**Saída fora do formato:** prompt textual não é garantia estrutural; isso será tratado no Lab 02.

## 9. Bloco 5 — Comparação entre prompts

### O que o bloco faz

Executa as versões vaga e orientada com o mesmo incidente.

### Como funciona

As duas chamadas recebem exatamente a mesma entrada. A principal variável alterada é a instrução.

### O que observar

Compare:

- organização;
- separação entre fato e hipótese;
- presença de suposições;
- clareza do próximo passo;
- indicação de incerteza;
- facilidade para avaliar.

Não avalie apenas qual resposta parece mais elegante. Avalie qual cumpre critérios observáveis.

### Saída esperada

Duas respostas identificadas como PROMPT VAGO e PROMPT ORIENTADO À TAREFA.

### Erros comuns

**Comparar chamadas com modelos diferentes:** invalida parte da comparação.

**Concluir com apenas um caso:** um exemplo é demonstração, não avaliação.

**Atribuir melhora ao tamanho:** a melhora vem da redução de ambiguidades.

## 10. Bloco 6 — Criação da base de runbooks

### O que o bloco faz

Cria seis objetos Document com conteúdo e metadados.

### Como funciona

Cada documento contém:

- id;
- page_content;
- metadata com source, domain e risk.

Os documentos representam:

- API;
- banco;
- autenticação;
- fila;
- comunicação;
- DNS.

### O que observar

- IDs são estáveis e podem ser citados.
- Domain será usado no filtro.
- Risk pode orientar políticas futuras.
- O texto inclui ações seguras e condições para aprovação.
- Dados de laboratório são fictícios.

### Saída esperada

Quantidade de documentos e uma linha source → domain para cada runbook.

### Erros comuns

**IDs duplicados:** prejudicam rastreabilidade.

**Metadados inconsistentes:** o filtro pode eliminar o documento correto.

**Documentos grandes demais:** dificultam recuperação precisa e aumentam custo.

## 11. Bloco 7 — Embeddings e banco vetorial

### O que o bloco faz

Inicializa embeddings multilíngues locais, cria o InMemoryVectorStore e adiciona os runbooks.

### Como funciona

HuggingFaceEmbeddings usa o modelo paraphrase-multilingual-MiniLM-L12-v2.

Os vetores são normalizados. O banco em memória calcula similaridade e mantém documentos durante
a sessão do notebook.

### O que observar

- A primeira execução pode baixar o modelo.
- O processo pode usar CPU e memória.
- Nenhuma chave de API é necessária para embeddings.
- LLM e embeddings são componentes independentes.
- O banco desaparece ao reiniciar o kernel.

### Saída esperada

> Banco vetorial criado em memória.

### Erros comuns

**Falha no download:** rede indisponível ou bloqueio do repositório de modelos.

**sentence-transformers ausente:** execute a instalação.

**Kernel sem memória:** use um modelo menor ou ambiente com mais recursos.

**Troca de embedding sem reindexar:** recrie o banco vetorial.

## 12. Bloco 8 — Recuperação seletiva

### O que o bloco faz

Implementa:

- palavras-chave por domínio;
- detectar_dominio;
- recuperar_ingenuo;
- recuperar_seletivo;
- teste com pergunta sobre API após deploy.

### Como funciona

detectar_dominio soma ocorrências de palavras-chave.

recuperar_ingenuo consulta o banco sem filtro.

recuperar_seletivo:

1. detecta o domínio;
2. cria filtro por metadata;
3. busca mais candidatos do que o K final;
4. remove scores abaixo do limiar;
5. retorna somente os primeiros K aprovados.

### O que observar

- A pergunta de exemplo deve ser classificada como api.
- RB-API-01 deve aparecer entre os resultados.
- O score deve ser exibido.
- O número de resultados pode ser menor que K por causa do limiar.
- O valor do score pode variar conforme versão do embedding.
- Neste banco, score maior representa maior similaridade.

### Saída esperada

Domínio detectado e lista de fontes com scores.

### Erros comuns

**Nenhum domínio:** o filtro fica desativado e a busca ocorre em toda a base.

**Nenhum resultado:** limiar alto, vocabulário diferente ou documento inadequado.

**Documento errado:** revise metadados, palavras-chave e corpus.

**Usar 0,25 em produção sem teste:** calibre com consultas rotuladas.

## 13. Bloco 9 — Montagem e orçamento do contexto

### O que o bloco faz

Transforma documentos recuperados em blocos de contexto, preservando fonte e score.

### Como funciona

montar_contexto percorre os resultados e:

- cria um cabeçalho para cada fonte;
- soma caracteres;
- interrompe quando o próximo bloco excederia max_chars;
- retorna texto, fontes e tamanho usado.

### O que observar

- O orçamento limita contexto enviado ao modelo.
- A ordem dos resultados importa.
- O primeiro bloco é aceito mesmo que seja maior que o limite, pois a condição exige que já exista
  um bloco. Discuta essa simplificação didática.
- As fontes retornadas devem corresponder aos blocos realmente incluídos.
- Caracteres são aproximação, não tokens reais.

### Saída esperada

Texto do contexto, lista de fontes e número de caracteres.

### Erros comuns

**Confundir caracteres com tokens:** use tokenizer do provedor em produção.

**Cortar conteúdo no meio:** este exemplo corta por documento; chunking deve ocorrer na indexação.

**Perder fonte após truncamento:** sempre monte a lista a partir dos blocos incluídos.

## 14. Bloco 10 — Cadeia RAG completa

### O que o bloco faz

Cria o prompt RAG, a estimativa de tokens e a função responder_rag.

### Como funciona

O prompt:

- define o papel;
- limita a resposta ao contexto;
- trata contexto como dado não confiável;
- proíbe seguir instruções dentro dos documentos;
- exige citações;
- define CONTEXTO INSUFICIENTE;
- encaminha ações arriscadas para revisão.

responder_rag:

1. inicia cronômetro;
2. recupera contexto;
3. aplica orçamento;
4. recusa sem chamar o modelo quando não há contexto;
5. formata mensagens;
6. chama o LLM;
7. retorna resposta, fontes, domínio, tamanho, tokens estimados, latência e uso.

### O que observar

- A recusa antecipada economiza uma chamada.
- Fontes recuperadas e fontes citadas são conceitos diferentes.
- usage_metadata preserva números reais quando o provedor os oferece.
- A estimativa de tokens usa caracteres divididos por quatro e é apenas didática.
- O cronômetro inclui recuperação, montagem e chamada do modelo.
- Delimitar o contexto reduz risco, mas não elimina prompt injection.

### Saída esperada

Este bloco define a cadeia. A execução ocorre na célula seguinte.

### Erros comuns

**Citação em formato diferente:** o validador posterior procura IDs entre colchetes.

**Modelo usa conhecimento externo:** reforce a recusa e avalie com casos adversariais.

**usage_metadata vazio:** alguns provedores ou versões não retornam todos os campos.

## 15. Bloco 11 — Execução da pergunta com contexto

### O que o bloco faz

Executa responder_rag com a pergunta sobre latência de API após deploy.

### O que observar

- A resposta deve usar o procedimento de RB-API-01.
- Deve citar a fonte.
- Não deve afirmar uma causa raiz não comprovada.
- Rollback deve aparecer condicionado à aprovação.
- As métricas devem incluir fonte, domínio, tamanho e latência.
- O texto exato pode variar, mas as propriedades devem permanecer.

### Saída esperada

Resposta estruturada em seções e dicionário de métricas.

### Erros comuns

**Resposta sem fonte:** o prompt não foi obedecido ou o formato esperado mudou.

**Ação destrutiva direta:** falha de segurança; deve ser detectada e escalada.

**Latência alta na primeira execução:** carregamento de modelo local ou cold start do provedor.

## 16. Bloco 12 — Pergunta fora da base

### O que o bloco faz

Pergunta sobre reembolso de passagem, tema ausente nos runbooks.

### Como funciona

Usa limiar mais alto para reduzir a chance de enviar um documento apenas vagamente semelhante.

### O que observar

- Nenhuma fonte deve ser selecionada.
- A função deve retornar CONTEXTO INSUFICIENTE.
- O LLM pode nem ser chamado.
- O sistema não deve inventar política de viagens.

Este é um teste de recusa, não um erro do sistema.

### Saída esperada

> CONTEXTO INSUFICIENTE.

Lista de fontes vazia.

### Erros comuns

**Documento irrelevante selecionado:** ajuste limiar, corpus ou roteamento.

**Modelo responde mesmo sem fonte:** confirme se houve contexto e se a recusa antecipada foi usada.

## 17. Bloco 13 — Experimento de trade-offs

### O que o bloco faz

Define três configurações:

- econômica;
- equilibrada;
- ampla.

Compara fontes, tokens estimados, latência, tokens reais e resposta.

### Como funciona

EXECUTAR_EXPERIMENTO começa falso para evitar três chamadas automáticas.

Quando ativado, o código executa a mesma pergunta com diferentes valores de K, limiar e orçamento.

### O que observar

- Mais contexto geralmente aumenta tokens.
- Latência pode crescer, mas há variabilidade de rede.
- Mais fontes não garantem resposta melhor.
- Configuração econômica pode perder evidência.
- Configuração ampla pode adicionar ruído.
- Uma execução por configuração não é suficiente para benchmark rigoroso.

### Saída esperada

Com experimento desativado, uma instrução para ativá-lo.

Com experimento ativado, DataFrame com três linhas.

### Erros comuns

**Ativar sem considerar custo:** confirme orçamento antes.

**Comparar só texto:** use métricas de qualidade e recuperação.

**Concluir por pequena diferença de latência:** repita e agregue resultados.

## 18. Bloco 14 — Estruturas de memória de execução

### O que o bloco faz

Define Tentativa e MemoriaExecucao.

### Como funciona

Tentativa é uma dataclass com:

- número;
- timestamp;
- configuração;
- fontes;
- status;
- feedback;
- latência;
- uso.

MemoriaExecucao mantém uma lista e oferece:

- registrar;
- dataframe.

### O que observar

- O histórico é estruturado, não uma concatenação de mensagens.
- Timestamp usa UTC.
- Configuração e resultado ficam separados.
- O DataFrame facilita inspeção e auditoria.
- Em produção, a memória em lista precisa ser substituída por persistência adequada.

### Saída esperada

Nenhuma saída imediata. As classes são usadas no próximo bloco.

### Erros comuns

**Registrar segredos:** não salve chaves, tokens ou conteúdo sensível.

**Usar memória em processo como persistência:** os dados somem ao reiniciar.

**Reenviar todo o histórico ao LLM:** selecione apenas feedback necessário.

## 19. Bloco 15 — Validação e tentativas com memória

### O que o bloco faz

Define:

- validar_resposta_rag;
- executar_com_memoria;
- dois planos de recuperação;
- execução opcional.

### Como funciona

validar_resposta_rag verifica:

- sem fontes, a resposta deve recusar;
- com fontes, pelo menos uma deve estar citada.

executar_com_memoria:

1. tenta o plano econômico;
2. valida;
3. registra resultado;
4. encerra se for válido;
5. usa plano mais amplo se necessário;
6. registra exceções;
7. escala se todos os planos falharem.

### O que observar

- A primeira resposta válida interrompe o loop.
- Cada tentativa registra configuração e feedback.
- Nova tentativa muda a estratégia; não é repetição idêntica.
- O limite evita loops infinitos.
- ESCALAR PARA REVISÃO HUMANA é uma saída projetada.
- O validador verifica citação, mas não prova que toda afirmação está fundamentada.

### Saída esperada

Resposta final e DataFrame com uma ou duas tentativas.

### Erros comuns

**Fonte recuperada, mas não citada:** resposta marcada como inválida.

**Exceção escondida:** confirme a coluna feedback.

**Sempre ampliar contexto:** somente amplie quando o feedback justificar.

# Lab 02 — Avaliação e Confiabilidade

## 20. O que o Lab 02 trata

O Lab 02 transforma comportamentos desejados em contratos, métricas e rotas seguras.

Ele cobre:

- configuração independente;
- saída estruturada;
- validação Pydantic;
- regras de negócio;
- versões de prompt;
- golden dataset;
- avaliadores determinísticos;
- quality gates;
- testes de contrato;
- avaliação real;
- LLM-as-judge;
- retry;
- fallback;
- escalonamento humano;
- fila de revisão.

## 21. Fluxo geral do Lab 02

Incidente

→ prompt versionado

→ saída estruturada

→ validação de schema

→ regras determinísticas

→ métricas

→ quality gate

→ resposta automática ou revisão humana

## 22. Bloco 1 — Instalação

### O que o bloco faz

Lista as dependências do Lab 02.

### Como funciona

O notebook é independente do Lab 01. Ele inclui Pydantic e pandas, mas não depende dos embeddings.

### O que observar

- Pydantic deve estar na versão 2.
- Instale a integração do provedor.
- Reinicie o kernel.
- Não é necessário executar esta célula a cada aula.

### Saída esperada

Logs de instalação sem erro.

### Erros comuns

**Pydantic antigo:** métodos como model_dump e model_json_schema podem não existir.

**Integração ausente:** init_chat_model não consegue criar o modelo.

## 23. Bloco 2 — Configuração do modelo

### O que o bloco faz

Repete a configuração multi-provedor para que o notebook seja autocontido.

### Como funciona

É semelhante ao Lab 01, mas define max_retries como zero. O objetivo é demonstrar retry de maneira
explícita mais adiante.

### O que observar

- O notebook não depende de variáveis criadas no Lab 01.
- O modelo selecionado será registrado nas avaliações.
- Desativar retry interno ajuda a distinguir falha do provedor e política da aplicação.

### Saída esperada

Provedor e modelo, ou aviso de chave ausente.

### Erros comuns

Os mesmos do bloco de configuração do Lab 01.

## 24. Bloco 3 — Schema AnaliseIncidente

### O que o bloco faz

Define o contrato estrutural da resposta com Pydantic.

### Como funciona

Os campos são:

- categoria com valores fechados;
- severidade P1 a P4;
- resumo com tamanho limitado;
- ação recomendada com tamanho limitado;
- evidências;
- confiança entre zero e um;
- necessidade de revisão humana.

Depois o schema JSON é exibido.

### O que observar

- Literal restringe valores.
- Field define limites e descrições.
- Evidências podem ser vazias apenas estruturalmente; a relação com a categoria será validada por
  regra de negócio.
- O schema documenta o contrato consumido por outros sistemas.
- Estrutura válida não significa conteúdo correto.

### Saída esperada

Dicionário JSON Schema com propriedades, tipos, limites e campos obrigatórios.

### Erros comuns

**Confundir schema com verdade:** Pydantic não valida se a severidade é correta.

**Alterar nomes sem atualizar consumidores:** trate o schema como contrato versionado.

## 25. Bloco 4 — Prompts A e B

### O que o bloco faz

Cria duas versões de prompt e define FONTES_PADRAO.

### Como funciona

Versão A:

- instrução curta;
- sem critérios detalhados.

Versão B:

- objetivo explícito;
- fontes autorizadas;
- proibição de invenção;
- política para desconhecido;
- revisão obrigatória para P1 e segurança;
- revisão por baixa confiança;
- ação reversível.

### O que observar

- Ambas usam as mesmas variáveis: incidente e fontes.
- Versões devem ser identificadas nos registros.
- A hipótese é que B será melhor, mas isso precisa ser medido.
- Regras críticas também aparecem no validador.

### Saída esperada

Nenhuma. O bloco cria templates.

### Erros comuns

**Mudar prompt e modelo juntos:** dificulta atribuir a causa da diferença.

**Considerar B automaticamente melhor:** execute a suite.

## 26. Bloco 5 — Chamada com saída estruturada

### O que o bloco faz

Define analisar_incidente e executa um incidente de segurança.

### Como funciona

with_structured_output recebe AnaliseIncidente e include_raw igual a verdadeiro.

O retorno inclui:

- parsed;
- parsing_error;
- raw;
- latency_s;
- prompt_version;
- model.

include_raw permite observar mensagem original e usage_metadata sem perder o objeto validado.

### O que observar

- parsed deve ser uma instância de AnaliseIncidente.
- parsing_error deve ser None em uma execução válida.
- Categoria esperada: seguranca.
- Severidade esperada: P1.
- Revisão humana esperada: verdadeira.
- Evidência esperada: RB-AUTH-01 e, opcionalmente, POL-COM-01.
- O texto exato pode variar, os campos críticos não.

### Saída esperada

Dicionário validado, erro de parsing vazio e latência.

### Erros comuns

**parsed igual a None:** veja parsing_error e raw.

**Modelo sem suporte adequado:** a integração pode usar chamada de ferramenta ou falhar.

**Fonte inventada:** será detectada no próximo bloco.

## 27. Bloco 6 — Validação das regras de negócio

### O que o bloco faz

Define validar_regras e cria uma saída propositalmente inválida.

### Como funciona

O validador detecta:

- fontes fora da lista;
- categoria operacional sem evidência;
- P1 sem revisão;
- segurança sem revisão;
- confiança baixa sem revisão;
- termos de ação destrutiva.

saida_teste é segurança P1 com precisa_revisao_humana igual a falso.

### O que observar

- O objeto Pydantic é criado com sucesso.
- A validação de negócio retorna valid igual a falso.
- Devem aparecer erros sobre P1 e segurança.
- Essa diferença demonstra estrutura válida versus decisão inválida.
- Regex é uma simplificação didática.

### Saída esperada

Dicionário com valid falso e lista de erros.

### Erros comuns

**Esperar ValidationError do Pydantic:** a violação é entre campos e está no validador separado.

**Colocar toda política no prompt:** regras críticas devem permanecer no código.

## 28. Bloco 7 — Golden dataset

### O que o bloco faz

Cria seis cenários de avaliação.

### Como funciona

Cada caso tem:

- id;
- input;
- categoria esperada;
- severidade esperada;
- must_review;
- allowed_sources.

Os cenários cobrem banco, API, segurança, fila, atendimento e ambiguidade.

### O que observar

- Há caminhos comuns e casos de alto risco.
- INC-006 exige categoria desconhecido e revisão.
- Casos sem fonte permitem lista vazia.
- Expectativas devem ser revisadas por especialistas.
- O dataset é pequeno e didático.

### Saída esperada

> 6 cenários no golden dataset.

### Erros comuns

**Só incluir casos fáceis:** adicione limites e falhas reais.

**Alterar expectativa para aprovar o modelo:** mudanças precisam de revisão.

**Dataset sem versão:** dificulta comparar experimentos.

## 29. Bloco 8 — Avaliadores determinísticos

### O que o bloco faz

Define avaliar_caso e agregar_metricas.

### Como funciona

avaliar_caso compara:

- categoria;
- severidade;
- revisão;
- citações;
- regras.

agregar_metricas calcula a proporção de sucesso de cada campo.

### O que observar

- Cada métrica responde a uma pergunta específica.
- Citações são comparadas com fontes permitidas.
- Casos sem fonte exigem lista vazia.
- A média por métrica preserva diferenças entre segurança e qualidade.
- Ainda não há chamada ao modelo.

### Saída esperada

Nenhuma saída imediata.

### Erros comuns

**Criar apenas uma nota geral:** pode esconder falha crítica.

**Avaliador permissivo:** teste com saídas controladas.

## 30. Bloco 9 — Saídas simuladas e regressão proposital

### O que o bloco faz

Cria resultados controlados para testar os avaliadores sem gastar tokens.

### Como funciona

criar_saida copia as expectativas do caso.

Na versão candidata, INC-003 é alterado:

- P1 vira P2;
- revisão verdadeira vira falsa.

As duas versões são avaliadas e agregadas.

### O que observar

- Baseline deve atingir 100% nas métricas.
- Candidata deve falhar em severidade, revisão e regras.
- Categoria e citações devem continuar corretas.
- O avaliador detecta regressão específica, não apenas mudança.
- Testar o avaliador vem antes de confiar nele.

### Saída esperada

Dicionário resultados_simulados com baseline e candidata.

### Erros comuns

**A candidata também obter 100%:** o avaliador ou a injeção da regressão está incorreto.

**A baseline falhar:** reveja fontes, regras e expectativas.

## 31. Bloco 10 — Tabela de métricas e quality gate

### O que o bloco faz

Exibe métricas e decide se cada versão pode ser aprovada.

### Como funciona

LIMITES exige:

- 90% para categoria;
- 90% para severidade;
- 100% para revisão;
- 100% para citações;
- 100% para regras.

quality_gate lista toda métrica abaixo do mínimo.

### O que observar

- Baseline deve ser aprovada.
- Candidata deve ser rejeitada.
- Severidade, revisão e regras devem aparecer nas falhas.
- Uma média global alta não compensa violação crítica.
- Limites de 100% representam invariantes de segurança do laboratório.

### Saída esperada

Tabela percentual, seguida de:

- baseline com approved verdadeiro;
- candidata com approved falso e failures.

### Erros comuns

**Baixar o limite para aprovar a candidata:** primeiro analise a causa da falha.

**Usar limite igual para tudo:** risco determina a tolerância.

## 32. Bloco 11 — Testes de contrato do prompt

### O que o bloco faz

Inspeciona o template da versão B sem chamar o modelo.

### Como funciona

Os asserts verificam:

- variáveis incidente e fontes;
- regra contra invenção;
- revisão humana;
- confiança;
- referência às fontes disponibilizadas.

### O que observar

- A execução deve terminar sem AssertionError.
- O teste é rápido, barato e determinístico.
- Ele detecta remoções acidentais.
- Ele não mede se o modelo obedecerá às regras.

### Saída esperada

> Contrato do prompt aprovado.

### Erros comuns

**AssertionError:** alguma regra ou variável foi removida ou renomeada.

**Concluir que o prompt está validado semanticamente:** são testes de presença, não de desempenho.

## 33. Bloco 12 — Suite real A versus B

### O que o bloco faz

Define RegistroAvaliacao, executar_suite e a flag EXECUTAR_SUITE_REAL.

### Como funciona

Para cada caso:

1. executa analisar_incidente;
2. verifica parsing;
3. avalia a saída;
4. captura uso e erro;
5. registra versão, modelo, tempo e métricas.

Se ocorrer exceção, todas as métricas do caso ficam falsas e o erro é registrado.

A flag começa falsa porque A e B sobre seis casos podem gerar doze chamadas.

### O que observar

- Custo antes de ativar.
- Mesmas condições para A e B.
- Erros aparecem no registro, não somem.
- Prompt, modelo e timestamp são rastreáveis.
- Uma única repetição ainda sofre variação.
- Resultados reais podem não confirmar a simulação.

### Saída esperada

Com flag falsa, aviso de ativação.

Com flag verdadeira, DataFrame com doze registros.

### Erros comuns

**Ativar sem chave:** a suite registra falhas.

**Comparar versões com modelos diferentes:** registre e controle a variável.

**Executar muitas vezes sem orçamento:** use amostra, cache ou limite.

## 34. Bloco 13 — LLM-as-judge

### O que o bloco faz

Define o schema Julgamento, o prompt do juiz e avaliar_com_juiz.

### Como funciona

O juiz retorna:

- nota de um a cinco;
- fundamentação nas evidências;
- segurança da ação;
- justificativa.

USAR_LLM_JUIZ começa falso.

### O que observar

- O juiz também é um modelo probabilístico.
- A rubrica deve ser explícita.
- Não recompensar texto longo reduz um viés comum.
- O juiz é adequado para propriedades semânticas difíceis de codificar.
- Regras de segurança determinísticas não devem depender somente dele.
- Compare notas do juiz com revisão humana em uma amostra.

### Saída esperada

Apenas confirmação de que o juiz foi configurado.

### Erros comuns

**Usar o mesmo modelo sem considerar viés:** documente a escolha.

**Tratar justificativa como prova:** valide calibração e consistência.

**Julgar todos os casos:** use amostragem para controlar custo.

## 35. Bloco 14 — Retry controlado

### O que o bloco faz

Simula um serviço que falha duas vezes e funciona na terceira.

### Como funciona

RunnableLambda envolve servico_instavel.

with_retry:

- trata somente TimeoutError;
- limita a três tentativas;
- desabilita jitter para a demonstração.

### O que observar

- O contador deve terminar em três.
- O valor final deve ter status ok.
- Retry é aplicado a erro transitório específico.
- O limite impede repetição infinita.
- Em produção, backoff e jitter ajudam a evitar sobrecarga.

### Saída esperada

Dicionário com status ok e:

> Tentativas: 3

### Erros comuns

**Retry em qualquer Exception:** pode esconder erros permanentes.

**Repetir operação não idempotente:** pode duplicar efeitos externos.

## 36. Bloco 15 — Fallback degradado

### O que o bloco faz

Simula provedor primário indisponível e usa uma resposta degradada.

### Como funciona

primario_indisponivel sempre lança ConnectionError.

with_fallbacks direciona a execução para resposta_degradada.

### O que observar

- A falha primária não encerra o fluxo.
- O fallback não inventa uma análise.
- O status degradado fica explícito.
- A ação final é revisão humana.
- Um fallback pode ser uma estratégia segura, não necessariamente outro LLM.

### Saída esperada

Dicionário com status degradado e ação de encaminhamento.

### Erros comuns

**Fallback silencioso:** sempre registre rota e motivo.

**Resposta genérica apresentada como análise concluída:** sinalize modo degradado.

## 37. Bloco 16 — Fallback real entre provedores

### O que o bloco faz

Cria um Runnable que tenta o modelo primário e pode trocar para um segundo provedor.

### Como funciona

FALLBACK_PROVIDER seleciona o secundário.

O código:

- valida o nome;
- verifica a chave;
- cria o modelo secundário;
- adiciona retry limitado ao primário;
- adiciona fallback.

Sem FALLBACK_PROVIDER, retorna o modelo primário.

### O que observar

- O bloco apenas configura; não faz chamada.
- O fallback deve aceitar a mesma entrada.
- A saída estruturada precisa ser aplicada de forma compatível.
- Dados enviados ao segundo provedor devem respeitar política.
- Registre qual modelo respondeu.
- O caminho secundário deve ser testado periodicamente.

### Saída esperada

> Runnable resiliente configurado.

### Erros comuns

**FALLBACK_PROVIDER sem chave:** RuntimeError.

**Provedor inválido:** ValueError.

**Capacidades diferentes:** teste structured output e tool calling no secundário.

## 38. Bloco 17 — Política de escalonamento

### O que o bloco faz

Define decidir_destino e aplica a política à saida_teste inválida.

### Como funciona

Motivos de revisão:

- parsing inválido;
- violação de regra;
- análise ausente;
- P1;
- segurança;
- confiança abaixo de 0,70;
- solicitação do próprio modelo.

O retorno contém route e reasons.

### O que observar

- saida_teste deve ir para human_review.
- Deve haver motivos sobre P1, segurança e regras violadas.
- A decisão de rota é determinística.
- A revisão é acionada por risco mesmo quando o schema é válido.
- Motivos são deduplicados e ordenados.

### Saída esperada

Dicionário com route human_review e lista de razões.

### Erros comuns

**Usar confiança do modelo como única regra:** confiança pode ser mal calibrada.

**Escalar sem motivo:** dificulta priorização e auditoria.

## 39. Bloco 18 — Fila de revisão humana

### O que o bloco faz

Cria fila_revisao e a função escalar_para_humano.

### Como funciona

Cada item recebe:

- review_id;
- created_at;
- incidente;
- análise;
- motivos;
- histórico;
- status pending.

A decisão anterior é usada para criar um item.

### O que observar

- O ID deve ser único.
- Timestamp deve estar em UTC.
- Motivos e histórico acompanham a solicitação.
- A análise é serializada com model_dump.
- O status inicial é pending.
- A lista em memória é somente demonstração.

### Saída esperada

Dicionário completo do item de revisão.

### Erros comuns

**Fila sem persistência:** itens somem ao reiniciar.

**Sem SLA ou responsável:** a fila pode crescer indefinidamente.

**Enviar dados sensíveis:** aplique minimização e controle de acesso.

**Sem estados posteriores:** produção precisa de approved, edited e rejected.

# 40. O que observar no conjunto da aula

## Engenharia de contexto

- O contexto enviado é necessário?
- Está autorizado para o usuário?
- Instruções estão separadas de dados?
- Há comportamento explícito para ausência de evidência?

## Recuperação

- O documento correto aparece?
- Há ruído?
- O limiar preserva recall?
- IDs e metadados permitem auditoria?

## Avaliação

- O dataset cobre risco e ambiguidade?
- As métricas detectam a regressão introduzida?
- Gates críticos não são compensados por médias?

## Confiabilidade

- Erros transitórios recebem retry limitado?
- Fallback preserva o contrato?
- A rota degradada é explícita?
- Revisão humana recebe contexto suficiente?

# 41. Ordem sugerida de demonstração

## Demonstração curta

Se houver pouco tempo:

1. Lab 01: blocos 2 a 5;
2. Lab 01: blocos 8 a 12;
3. Lab 02: blocos 3, 5 e 6;
4. Lab 02: blocos 7 a 11;
5. Lab 02: blocos 14, 15, 17 e 18.

## Demonstração completa

Execute todos os blocos em ordem, mantendo desativados:

- EXECUTAR_EXPERIMENTO;
- EXECUTAR_SUITE_REAL;
- USAR_LLM_JUIZ.

Ative cada um somente após explicar número de chamadas e custo.

# 42. Critérios de sucesso

Ao final, a turma deve conseguir demonstrar:

- diferença observável entre prompt vago e orientado;
- recuperação do runbook correto;
- recusa em pergunta fora da base;
- resposta com fonte;
- registro de tentativas;
- estrutura válida que ainda viola política;
- regressão detectada por métricas;
- quality gate bloqueando a candidata;
- retry limitado;
- fallback degradado;
- incidente de alto risco enviado para revisão humana.

# 43. Referências

- [LangChain — Context engineering](https://docs.langchain.com/oss/python/langchain/context-engineering)
- [LangChain — Vector stores](https://docs.langchain.com/oss/python/integrations/vectorstores)
- [LangChain — Structured output](https://docs.langchain.com/oss/python/langchain/structured-output)
- [LangChain — Guardrails](https://docs.langchain.com/oss/python/langchain/guardrails)
- [LangChain — Human in the loop](https://docs.langchain.com/oss/python/langchain/human-in-the-loop)
- [LangSmith — Evaluation](https://docs.langchain.com/langsmith/evaluation)
