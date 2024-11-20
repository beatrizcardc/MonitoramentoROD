import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import glob

# Configuração do Streamlit
st.set_page_config(layout="wide", page_title="Monitoramento de Logs em Tempo Real")

# Função para carregar os logs
def load_logs(log_dir):
    log_files = glob.glob(log_dir + "/*/logs.txt")
    all_logs = []
    for file in log_files:
        category = file.split("/")[-2]
        with open(file, "r") as f:
            for line in f.readlines():
                try:
                    timestamp, _, log_level, message = line.strip().split(" - ", maxsplit=3)
                    log_time = datetime.strptime(timestamp.strip("[]"), "%Y-%m-%d %H:%M:%S")
                    all_logs.append({"Timestamp": log_time, "Category": category, "Level": log_level, "Message": message})
                except ValueError:
                    continue
    return pd.DataFrame(all_logs)

# Configurar o diretório de logs
log_dir = "logs_demo"  # Certifique-se de que a pasta está no mesmo nível do script
all_logs = load_logs(log_dir)

# Processar dados se existirem logs
if not all_logs.empty:
    all_logs["Date"] = all_logs["Timestamp"].dt.date
    all_logs["Hour"] = all_logs["Timestamp"].dt.hour

    # Exibir estatísticas principais
    st.title("Monitoramento de Logs - Tempo Real")
    st.subheader("Estatísticas Gerais")
    st.write(f"Total de Logs: {len(all_logs)}")
    st.write(f"Logs Críticos (ERROR): {len(all_logs[all_logs['Level'] == 'ERROR'])}")

    # Gráfico de barras: Logs por categoria
    st.subheader("Logs por Categoria")
    category_counts = all_logs["Category"].value_counts()
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    category_counts.plot(kind="bar", ax=ax1)
    ax1.set_title("Logs por Categoria")
    ax1.set_xlabel("Categoria")
    ax1.set_ylabel("Número de Logs")
    st.pyplot(fig1)

     # Heatmap: Ocorrências por hora
    st.subheader("Ocorrências de Logs por Hora")
    hourly_logs = all_logs.groupby(["Hour", "Category"]).size().unstack(fill_value=0)
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    sns.heatmap(hourly_logs, cmap="coolwarm", ax=ax2)
    ax2.set_title("Heatmap de Ocorrências por Hora")
    st.pyplot(fig2)

    # Destaques de eventos críticos
    st.subheader("Eventos Críticos")
    critical_events = all_logs[all_logs["Level"] == "ERROR"].sort_values("Timestamp", ascending=False).head(10)
    st.write(critical_events)

# Mensagem caso não existam logs
else:
    st.title("Monitoramento de Logs - Tempo Real")
    st.write("Nenhum log encontrado. Por favor, verifique o diretório de logs.")
