import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def generate_graphs():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_results_path = os.path.join(current_dir, "..", "locust-scripts", "resultados")

    instancias = ["1_instancias", "2_instancias", "3_instancias"]
    cenarios = ["cenario_1", "cenario_2", "cenario_3"]
    levels = ["leve", "medio", "pesado"]
    
    all_data = []

    for inst in instancias:
        for cen in cenarios:
            for lvl in levels:
                file_name = f"resultado_{lvl}_stats.csv"
                csv_path = os.path.join(base_results_path, inst, cen, file_name)
                
                if os.path.exists(csv_path):
                    try:
                        df = pd.read_csv(csv_path)
                        df_agg = df[df["Name"] == "Aggregated"].copy()
                        
                        if not df_agg.empty:
                            df_agg["Instâncias"] = inst.replace("_", " ").capitalize()
                            df_agg["Cenário"] = cen.replace("_", " ").capitalize()
                            df_agg["Carga"] = lvl.capitalize()
                            df_agg["Taxa de Falha (%)"] = (df_agg["Failure Count"] / df_agg["Request Count"]) * 100
                            
                            all_data.append(df_agg)
                    except Exception as e:
                        print(f"Erro ao ler {csv_path}: {e}")
                else:
                    print(f"Aviso: Arquivo não encontrado: {csv_path}")

    if not all_data:
        print("Nenhum dado encontrado. Verifique se os arquivos CSV estão nos diretórios corretos.")
        return

    combined_df = pd.concat(all_data, ignore_index=True)
    sns.set_theme(style="whitegrid")
    
    carga_order = ["Leve", "Medio", "Pesado"]

    for cen_name in combined_df["Cenário"].unique():
        df_cenario = combined_df[combined_df["Cenário"] == cen_name]

        plt.figure(figsize=(12, 7))
        ax = sns.barplot(
            data=df_cenario, 
            x="Carga", 
            y="95%", 
            hue="Instâncias",
            order=carga_order,
            palette="viridis"
        )
        plt.title(f"Percentil 95 (P95) - {cen_name}", fontsize=15)
        plt.ylabel("Tempo de Resposta (ms)")
        plt.legend(title="Infraestrutura", bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        
        plt.savefig(os.path.join(current_dir, f"p95_{cen_name.lower().replace(' ', '_')}.png"))
        plt.close()

        plt.figure(figsize=(12, 7))
        ax = sns.barplot(
            data=df_cenario, 
            x="Carga", 
            y="Taxa de Falha (%)", 
            hue="Instâncias",
            order=carga_order,
            palette="magma"
        )
        plt.title(f"Taxa de Falha (%) - {cen_name}", fontsize=15)
        plt.ylabel("Falhas (%)")
        plt.ylim(0, max(combined_df["Taxa de Falha (%)"].max() * 1.2, 5))  
        plt.legend(title="Infraestrutura", bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()

        plt.savefig(os.path.join(current_dir, f"falhas_{cen_name.lower().replace(' ', '_')}.png"))
        plt.close()

    print(f"Processamento concluído. Gráficos salvos em: {current_dir}")

if __name__ == "__main__":
    generate_graphs()