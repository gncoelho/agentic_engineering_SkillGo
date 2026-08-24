# Formulário para Criação de um Agente 

Preencha as 15 perguntas antes de iniciar a implementação. Use respostas curtas e objetivas.

## 1. Qual será o nome do agente e como ele pode ser descrito em uma frase?

**Resposta:**

> O agente __________________ ajuda __________________ a __________________.

## 2. Qual problema o agente resolverá e quem será seu usuário?

**Resposta:**

> Preencher:

## 3. Qual é o objetivo principal e como saberemos que a tarefa foi concluída com sucesso?

**Resposta:**

> Preencher:

## 4. O que o agente não deve fazer?

**Resposta:**

1. Preencher:
2. Preencher:
3. Preencher:

## 5. Quais entradas o agente receberá e qual saída deverá produzir?

| Entradas | Formato da saída |
|---|---|
| Preencher | Preencher |

## 6. Quais instruções e regras obrigatórias devem aparecer no prompt do agente?

**Resposta:**

1. Preencher:
2. Preencher:
3. Preencher:

## 7. Qual modelo e provedor serão utilizados e por que foram escolhidos?

| Provedor | Modelo | Justificativa |
|---|---|---|
| Preencher | Preencher | Preencher |

## 8. De quais informações de contexto o agente precisa para tomar boas decisões?

**Resposta:**

> Preencher instruções, dados do usuário, documentos, permissões ou histórico necessários:

## 9. O agente precisará de RAG ou de uma base de conhecimento?

**Resposta:**

- [ ] Não
- [ ] Sim

**Fontes e estratégia de recuperação:**

> Preencher ou escrever N/A:

## 10. Quais ferramentas estarão disponíveis e quando cada uma deverá ser usada?

| Ferramenta | Finalidade | Quando usar | Entrada e saída | Possui efeito externo |
|---|---|---|---|---|
| Preencher | Preencher | Preencher | Preencher | Sim/Não |
| Preencher | Preencher | Preencher | Preencher | Sim/Não |
| Preencher | Preencher | Preencher | Preencher | Sim/Não |

## 11. Qual protocolo ou sequência de passos o agente deverá seguir?

**Resposta:**

> Entrada → __________________ → __________________ → __________________ → Resposta

**Critério de parada e limite de passos:**

> Preencher:

## 12. O agente precisará de memória e o que deverá ser lembrado ou esquecido?

**Resposta:**

- [ ] Não precisa de memória
- [ ] Memória durante a conversa
- [ ] Memória entre conversas

**Informações que podem ser armazenadas:**

> Preencher:

## 13. Como a resposta e as ações do agente serão validadas antes de serem aceitas?

**Resposta:**

> Preencher formato esperado, regras de negócio, fontes, permissões e ações proibidas:

## 14. O que acontecerá quando houver erro, contexto insuficiente ou uma decisão de alto risco?

| Situação | Retry | Fallback | Revisão humana |
|---|---|---|---|
| Erro temporário | Preencher | Preencher | Preencher |
| Contexto insuficiente | Preencher | Preencher | Preencher |
| Ação de alto risco | Preencher | Preencher | Preencher |

## 15. Quais cenários serão usados para testar se o agente está pronto?

| Cenário | Entrada | Resultado esperado |
|---|---|---|
| Caminho feliz | Preencher | Preencher |
| Entrada ambígua | Preencher | Preencher |
| Ferramenta indisponível | Preencher | Preencher |
| Contexto insuficiente | Preencher | Preencher |
| Ação de alto risco | Preencher | Preencher |

**Métrica principal e valor mínimo para aprovação:**

> Preencher:
