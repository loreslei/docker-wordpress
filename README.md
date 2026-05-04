# Análise de Testes de Carga - Locust

Este diretório contém os gráficos gerados a partir dos resultados dos testes de carga realizados com o Locust. Os gráficos ilustram o comportamento da aplicação sob três diferentes níveis de carga (**Leve**, **Médio** e **Pesado**) e infraestruturas com diferentes números de instâncias (**1, 2 e 3 instâncias**). 

Foram analisados três cenários distintos, gerando dois tipos de métricas principais:
- **Percentil 95 (P95)**: Tempo máximo de resposta que 95% das requisições levaram para serem concluídas (em milissegundos).
- **Taxa de Falha (%)**: Porcentagem de requisições que resultaram em erro.

---

## 📊 Conclusões por Métrica

### 1. Tempo de Resposta (P95)
- **Cenários 1 e 3**: Apresentaram um comportamento bastante similar. Sob carga leve e média, os tempos de resposta mantiveram-se excelentes (abaixo de 100ms). Sob carga pesada, o tempo de resposta aumentou substancialmente (atingindo em torno de 500ms a 770ms). Curiosamente, o aumento no número de instâncias (de 1 para 2 ou 3) **não reduziu** o tempo de resposta; em alguns casos, houve um leve aumento do P95, possivelmente devido ao *overhead* de balanceamento de carga ou gargalos em algum recurso compartilhado (como o banco de dados).
- **Cenário 2**: Este provou ser o cenário mais crítico e exigente da aplicação. Mesmo sob carga leve, o P95 já beirava os 250-300ms. Sob cargas média e pesada, os tempos degradaram drasticamente, saltando para faixas entre 1600ms-1900ms e cerca de 4000ms, respectivamente. 

### 2. Taxa de Falha (%)
- **Cenários 1 e 3**: A aplicação demonstrou alta estabilidade e resiliência, registrando **0% de taxa de falha** em todas as combinações de carga e quantidade de instâncias. Isso indica que, nestes cenários, a aplicação consegue processar as requisições com sucesso, mesmo que o tempo de resposta aumente durante picos de acesso.
- **Cenário 2**: Mostrou ser a operação de maior risco de quebra. Sob carga pesada, a infraestrutura apresentou taxas de falhas expressivas de aproximadamente **14% a 15%** (especialmente visível nas configurações de 2 e 3 instâncias). Isso sugere que o gargalo neste cenário não é resolvido pela simples escalabilidade horizontal da aplicação.

---

## 🎯 Conclusão Geral

Com base na análise dos gráficos gerados (`falhas_*.png` e `p95_*.png`), podemos concluir que:

1. **Escalabilidade Horizontal Encontra Gargalos Externos**: Adicionar mais instâncias (replicar os containers da aplicação) não resultou em melhora linear de desempenho. Para os cenários testados, o ganho de eficiência ao passar de 1 para 3 instâncias foi imperceptível ou até negativo. Isso sinaliza fortemente que o limite da arquitetura **não está no processamento da aplicação**, mas sim em recursos de infraestrutura compartilhados — muito possivelmente o **Banco de Dados** (falta de índices, *locks*, ou limite de conexões simultâneas) ou o próprio *Load Balancer* de entrada.
2. **Otimização Prioritária no Cenário 2**: A arquitetura precisa de otimização urgente voltada para as operações simuladas no Cenário 2. Recomenda-se investigar as *queries* disparadas nesse fluxo e considerar fortemente a implementação de estratégias de **cache em memória** (como Redis ou Memcached) para reduzir a pressão no backend de dados.
3. **Estabilidade em Fluxos Comuns**: Para o perfil de uso dos Cenários 1 e 3, a infraestrutura está adequada sob cargas leves e médias. Ela garante respostas rápidas e retenção total das requisições sem falhas, cumprindo o seu papel satisfatoriamente até o limite testado.

> **Próximos Passos recomendados:** Investigar o consumo de CPU, Memória e concorrência no serviço de Banco de Dados (ex: MySQL/MariaDB) durante as execuções do Cenário 2 em carga pesada.
