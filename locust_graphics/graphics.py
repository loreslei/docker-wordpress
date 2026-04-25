import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def generate_graphs():
    # Diretório atual (locust_graphics) e diretório base do projeto
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(current_dir)
    scripts_dir = os.path.join(project_dir, "locust-scripts")

    levels = ["leve", "medio", "pesado"]
    data = []
    
    # Coletar dados dos 3 diretórios
    for level in levels:
        folder_name = f"resultado_{level}"
        csv_path = os.path.join(scripts_dir, folder_name, "resultado_users_stats.csv")
        
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            # Remover linha de 'Aggregated' (totalizadores)
            df = df[df["Name"] != "Aggregated"]
            # O locust pode ter linhas vazias ao final ou algo do tipo
            df = df.dropna(subset=["Name"])
            
            # Adicionar coluna indicando o nível de carga
            df["Level"] = level.capitalize()
            data.append(df)
        else:
            print(f"Aviso: Arquivo não encontrado - {csv_path}")
            
    if not data:
        print("Nenhum dado encontrado para gerar os gráficos.")
        return
        
    combined_df = pd.concat(data, ignore_index=True)
    
    # Definir quais métricas vamos plotar
    metrics = {
        "Average Response Time": "Tempo Médio de Resposta (ms)",
        "Requests/s": "Requisições por Segundo",
        "Failure Count": "Número de Falhas"
    }

    # Definir o estilo visual (sns fornece cores mais agradáveis)
    sns.set_theme(style="whitegrid")
    level_order = ["Leve", "Medio", "Pesado"]

    for metric, label in metrics.items():
        if metric in combined_df.columns:
            plt.figure(figsize=(10, 6))
            
            # Criar um gráfico de barras agrupado usando seaborn
            ax = sns.barplot(
                data=combined_df, 
                x="Name", 
                y=metric, 
                hue="Level",
                hue_order=[l for l in level_order if l in combined_df["Level"].unique()],
                palette="viridis"
            )
            
            plt.title(f"{label} por Cenário e Nível de Carga", fontsize=14, pad=15)
            plt.ylabel(label, fontsize=12)
            plt.xlabel("Cenários", fontsize=12)
            plt.xticks(rotation=45, ha='right')
            plt.legend(title="Nível de Carga")
            
            # Ajustar layout para não cortar labels
            plt.tight_layout()
            
            # Salvar imagem
            filename = f"grafico_{metric.replace(' ', '_').replace('/', '_').lower()}.png"
            output_file = os.path.join(current_dir, filename)
            plt.savefig(output_file, dpi=300)
            plt.close()
            print(f"Gráfico gerado com sucesso: {output_file}")

if __name__ == "__main__":
    generate_graphs()
