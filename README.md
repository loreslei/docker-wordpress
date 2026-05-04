# Análise de Testes de Carga - Locust

Este diretório contém os gráficos gerados a partir dos resultados dos testes de carga realizados com o Locust. Os gráficos ilustram o comportamento da aplicação sob três diferentes níveis de carga (**Leve**, **Médio** e **Pesado**) e infraestruturas com diferentes números de instâncias (**1, 2 e 3 instâncias**). 

Foram analisados três cenários distintos, baseados nos *endpoints* do WordPress:
- **Cenário 1:** Requisição ao Post contendo uma **Imagem de 1MB**.
- **Cenário 2:** Requisição ao Post contendo um **Texto longo de 400kb**.
- **Cenário 3:** Requisição ao Post contendo uma **Imagem de 300kb**.

A partir das execuções, foram monitorados dois tipos de métricas principais:
- **Percentil 95 (P95)**: Tempo máximo de resposta que 95% das requisições levaram para serem concluídas (em milissegundos).
- **Taxa de Falha (%)**: Porcentagem de requisições que resultaram em erro.

---

## 📊 Conclusões por Métrica

### 1. Tempo de Resposta (P95)
- **Cenários 1 e 3 (Páginas de Imagens)**: Apresentaram um comportamento bastante similar. Sob carga leve e média, os tempos de resposta mantiveram-se excelentes (abaixo de 100ms). Sob carga pesada, o tempo de resposta aumentou substancialmente (atingindo em torno de 500ms a 770ms). O aumento no número de instâncias (de 1 para 2 ou 3) **não reduziu** o tempo de resposta; em alguns casos, houve um leve aumento do P95, possivelmente devido ao *overhead* de balanceamento de carga ou gargalos em algum recurso compartilhado (como o banco de dados).
- **Cenário 2 (Página de Texto 400kb)**: Este provou ser o cenário mais crítico e exigente da aplicação. Mesmo sob carga leve, o P95 já beirava os 250-300ms. Sob cargas média e pesada, os tempos degradaram drasticamente, saltando para faixas entre 1600ms-1900ms e cerca de 4000ms, respectivamente. 

### 2. Taxa de Falha (%)
- **Cenários 1 e 3 (Páginas de Imagens)**: A aplicação demonstrou alta estabilidade e resiliência, registrando **0% de taxa de falha** em todas as combinações de carga e quantidade de instâncias. Isso indica que, nestes cenários, a aplicação consegue processar a estrutura da página com sucesso, mesmo que o tempo de resposta aumente durante picos de acesso.
- **Cenário 2 (Página de Texto 400kb)**: Mostrou ser a operação de maior risco de quebra. Sob carga pesada, a infraestrutura apresentou taxas de falhas expressivas de aproximadamente **14% a 15%** (especialmente visível nas configurações de 2 e 3 instâncias). Isso sugere que o gargalo neste cenário não é resolvido pela simples escalabilidade horizontal da aplicação.

---

## 🎯 Conclusão Geral

Com base na análise dos gráficos e na natureza dos scripts simulados, podemos concluir que:

1. **Processamento Dinâmico vs. Estático**: A gritante diferença de desempenho entre o Cenário 2 (Texto) e os Cenários 1/3 (Imagens) expõe o gargalo da arquitetura. O WordPress utiliza PHP e o Banco de Dados (MySQL) para processar e gerar textos dinamicamente. Retornar um texto massivo de 400kb gerado dinamicamente no banco causa uma forte sobrecarga nos *workers* do PHP e nas conexões do banco. Em contrapartida, as páginas de imagens geram um HTML muito menor na resposta inicial do servidor (deixando o peso real para o arquivo de imagem propriamente dito, que servidores como Nginx lidam com muito mais eficiência).
2. **Escalabilidade Horizontal Encontra Gargalos Externos**: Adicionar mais instâncias (replicar os containers do WordPress) não resultou em melhora linear de desempenho. Para o Cenário 2, o ganho de eficiência ao passar de 1 para 3 instâncias foi imperceptível ou até negativo. Isso sinaliza fortemente que o limite da arquitetura **não está no processamento da aplicação web isolada**, mas sim no **Banco de Dados**.
3. **Otimização Prioritária no Cenário 2**: A arquitetura precisa de otimização urgente voltada para o carregamento de textos pesados. Recomenda-se investigar a implementação de estratégias de **cache em memória** (como Redis ou Memcached) ou soluções como o *WP Super Cache / W3 Total Cache* para armazenar a versão HTML gerada e reduzir drasticamente a pressão no backend de dados e no processamento do PHP.
4. **Estabilidade em Fluxos Leves**: Para o perfil de uso dos Cenários 1 e 3, a infraestrutura está adequada sob cargas leves e médias. Ela garante respostas rápidas e retenção total das requisições sem falhas, cumprindo o seu papel satisfatoriamente.

> **Próximos Passos recomendados:** Investigar o consumo de CPU e concorrência no serviço de Banco de Dados (MySQL) durante o teste do Cenário 2 em carga pesada, e configurar um sistema de cache em nível de aplicação para evitar consultas repetidas à base.