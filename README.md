# Análise de Testes de Carga - Locust

Este diretório contém os gráficos gerados a partir dos resultados dos testes de carga realizados com o Locust. Os gráficos ilustram o comportamento da aplicação sob três diferentes níveis de carga (**Leve**, **Médio** e **Pesado**) e infraestruturas com diferentes números de instâncias (**1, 2 e 3 instâncias**). 

Cargas:
- **Leve:** 160 **usuários** 4 **req/s**
- **Média:** 240 **usuários** 10 **req/s**
- **Pesada:** 360 **usuários** 13 **req/s**
  
Foram analisados quatro cenários distintos, baseados nos *endpoints* do WordPress:
- **Cenário 1:** Requisição ao Post contendo uma **Imagem de 1MB**.
- **Cenário 2:** Requisição ao Post contendo um **Texto longo de 400kb**.
- **Cenário 3:** Requisição ao Post contendo uma **Imagem de 300kb**.
- **Cenário Todos:** Execução simultânea e randômica dos três cenários acima, simulando um padrão de tráfego real e diversificado.

A partir das execuções, foram monitorados dois tipos de métricas principais:
- **Percentil 95 (P95)**: Tempo máximo de resposta que 95% das requisições levaram para serem concluídas (em milissegundos).
- **Taxa de Falha (%)**: Porcentagem de requisições que resultaram em erro.

---

## 📊 Conclusões por Métrica

### 1. Tempo de Resposta (P95)
- **Cenários 1 e 3 (Páginas de Imagens)**: Apresentaram um comportamento bastante similar. Sob carga leve e média, os tempos de resposta mantiveram-se excelentes (abaixo de 100ms). Sob carga pesada, o tempo de resposta aumentou substancialmente (atingindo em torno de 500ms a 770ms). O aumento no número de instâncias (de 1 para 2 ou 3) **não reduziu** o tempo de resposta; em alguns casos, houve um leve aumento do P95, possivelmente devido ao *overhead* de balanceamento de carga ou gargalos em algum recurso compartilhado (como o banco de dados).
- **Cenário 2 (Página de Texto 400kb)**: Este provou ser o cenário mais crítico e exigente da aplicação. Mesmo sob carga leve, o P95 já beirava os 250-300ms. Sob cargas média e pesada, os tempos degradaram drasticamente, saltando para faixas entre 1600ms-1900ms e cerca de 4000ms, respectivamente. 
- **Cenário Todos (Carga Mista)**: Refletiu uma média do comportamento geral. A presença das requisições pesadas de texto (Cenário 2) puxou o tempo de resposta para cima durante os picos de concorrência, demonstrando que uma única funcionalidade pesada pode degradar a experiência de navegação de todo o site.

### 2. Taxa de Falha (%)
- **Cenários 1 e 3 (Páginas de Imagens)**: A aplicação demonstrou alta estabilidade e resiliência, registrando **0% de taxa de falha** em todas as combinações de carga e quantidade de instâncias. Isso indica que, nestes cenários, a aplicação consegue processar a estrutura da página com sucesso, mesmo que o tempo de resposta aumente.
- **Cenário 2 (Página de Texto 400kb)**: Mostrou ser a operação de maior risco de quebra. Sob carga pesada, a infraestrutura apresentou taxas de falhas expressivas de aproximadamente **14% a 15%**.
- **Cenário Todos (Carga Mista)**: Sob carga pesada, especialmente na configuração de 3 instâncias, a aplicação começou a ceder, registrando uma pequena taxa de falha (cerca de **0,1%**). O detalhamento dos logs revelou que **todas essas falhas foram erros `HTTP 500: Internal Server Error`**. Embora a porcentagem seja visualmente pequena quando comparada aos 15% do Cenário 2, ela é um termômetro vital: indica que a mistura de processamento de I/O de arquivos (imagens) com consultas pesadas (texto) leva os recursos do servidor (como limites de conexão do Banco de Dados ou *workers* do PHP) à exaustão em picos de concorrência.

---

## 🎯 Conclusão Geral

Com base na análise dos gráficos e na natureza dos scripts simulados, podemos concluir que:

1. **Processamento Dinâmico vs. Estático**: A gritante diferença de desempenho entre o Cenário 2 (Texto) e os Cenários 1/3 (Imagens) expõe o gargalo da arquitetura. O WordPress utiliza PHP e o Banco de Dados (MySQL) para processar e gerar textos dinamicamente. Retornar um texto massivo de 400kb gerado dinamicamente no banco causa uma forte sobrecarga nos *workers* do PHP e nas conexões do banco. Em contrapartida, as páginas de imagens geram um HTML muito menor na resposta inicial do servidor.
2. **Escalabilidade Horizontal Encontra Gargalos Externos**: Adicionar mais instâncias (replicar os containers do WordPress) não resultou em melhora linear de desempenho. No cenário misto ("Cenário Todos") com carga pesada, ter 3 instâncias de WordPress atacando simultaneamente um único Banco de Dados culminou em erros 500 (Internal Server Error). Isso sinaliza fortemente que o limite da arquitetura **não está no processamento da aplicação web isolada**, mas sim na camada de dados (MySQL).
3. **Otimização Prioritária no Cenário 2**: A arquitetura precisa de otimização urgente voltada para o carregamento de textos pesados. Recomenda-se investigar a implementação de estratégias de **cache em memória** (como Redis ou Memcached) ou soluções como o *WP Super Cache / W3 Total Cache* para armazenar a versão HTML gerada e reduzir drasticamente a pressão no backend de dados e no processamento do PHP.
4. **Estabilidade em Fluxos Leves**: Para o perfil de uso dos Cenários 1 e 3, a infraestrutura está adequada sob cargas leves e médias. Ela garante respostas rápidas e retenção total das requisições sem falhas, cumprindo o seu papel satisfatoriamente.

> **Próximos Passos recomendados:** Investigar o consumo de CPU e limite de conexões (`max_connections`) no serviço de Banco de Dados (MySQL) durante o teste do Cenário Todos em carga pesada. Configurar também um sistema de cache em nível de aplicação para evitar consultas repetidas à base.

## 📉 Gráficos

<br>
<img width="1200" height="700" alt="Image" src="https://github.com/user-attachments/assets/84d30215-c4b6-48a3-b6b4-aa19e623c2d0" />
<br><br>

<img width="1200" height="700" alt="Image" src="https://github.com/user-attachments/assets/2de6898f-9b8d-4511-866e-de678aa99798" />
<br><br>

<img width="1200" height="700" alt="Image" src="https://github.com/user-attachments/assets/98ab618e-6e16-48f1-a36d-147ae3e5b80c" />
<br><br>

<img width="1200" height="700" alt="Image" src="https://github.com/user-attachments/assets/db12347b-e3f2-4931-8019-9760f069f18f" />
<br><br>

<img width="1200" height="700" alt="Image" src="https://github.com/user-attachments/assets/09a954f9-8a03-4728-9ae7-9b488f76712a" />
<br><br>

<img width="1200" height="700" alt="Image" src="https://github.com/user-attachments/assets/db03c67d-0ca5-4e57-9fc6-ab3581622a79" />
<br><br>

<img width="1200" height="700" alt="Image" src="https://github.com/user-attachments/assets/3b0fd4a5-d3ac-411e-aafb-8b06894e9602" />
<br><br>

<img width="1200" height="700" alt="Image" src="https://github.com/user-attachments/assets/c0b2fe3f-67b6-46f8-b640-dc0ad2628808" />
