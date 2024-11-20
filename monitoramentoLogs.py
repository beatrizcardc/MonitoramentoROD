import requests
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# Configuração do Streamlit
st.set_page_config(layout="wide", page_title="Monitoramento de Logs em Tempo Real")

# Base URL para os logs no GitHub
base_url = "https://raw.githubusercontent.com/beatrizcardc/MonitoramentoROD/main/logs_demo"
categories = ["Performance", "Memoria", "Erro_de_Sincronizacao", "Acesso_a_Plano_de_Venda", 
              "Autenticacao", "Erro_de_Sistema", "Logs_de_API", "Logs_de_Banco_de_Dados", 
              "Logs_de_Transacoes_Financeiras", "Atividades_Suspeitas"]

# Gerar URLs completas para os arquivos de log
log_files_urls = [f"{base_url}/{category}/logs.txt" for category in categories]

# Função para carregar logs de uma URL
def load_logs_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = []
        for line in response.text.splitlines():
            try:
                timestamp, _, level, message = line.split(" - ", maxsplit=3)
                data.append({"Timestamp": timestamp.strip("[]"), "Level": level, "Message": message, "Category": url.split("/")[-2]})
            except ValueError:
                continue
        return pd.DataFrame(data)
    else:
        st.error(f"Erro ao acessar {url}: {response.status_code}")
        return pd.DataFrame()

# Carregar todos os logs
all_logs = pd.concat([load_logs_from_url(url) for url in log_files_urls], ignore_index=True)

# Verificar se há logs carregados
if all_logs.empty:
    st.warning("Nenhum log foi carregado. Verifique as URLs ou a conectividade.")
else:
    # Processar os dados
    all_logs["Timestamp"] = pd.to_datetime(all_logs["Timestamp"], errors="coerce")
    all_logs.dropna(subset=["Timestamp"], inplace=True)
    all_logs["Date"] = all_logs["Timestamp"].dt.date
    all_logs["Hour"] = all_logs["Timestamp"].dt.hour

    # Menu lateral
    st.sidebar.header("Configurações de Filtro")
    mode = st.sidebar.radio("Modo de Análise", ["Rastreamento Online", "Análise por Intervalo de Tempo"])
    
    # Configurações de filtros
    selected_category = st.sidebar.multiselect("Selecionar Categorias", categories, default=categories)
    selected_level = st.sidebar.multiselect("Selecionar Níveis", ["INFO", "WARNING", "ERROR"], default=["INFO", "WARNING", "ERROR"])

    if mode == "Análise por Intervalo de Tempo":
        start_date = st.sidebar.date_input("Data Inicial", value=all_logs["Date"].min())
        end_date = st.sidebar.date_input("Data Final", value=all_logs["Date"].max())
        filtered_logs = all_logs[
            (all_logs["Category"].isin(selected_category)) &
            (all_logs["Level"].isin(selected_level)) &
            (all_logs["Date"] >= start_date) &
            (all_logs["Date"] <= end_date)
        ]
        st.info(f"Mostrando logs de {start_date} até {end_date}.")
    else:
        filtered_logs = all_logs[
            (all_logs["Category"].isin(selected_category)) &
            (all_logs["Level"].isin(selected_level))
        ]
        st.info("Rastreamento online ativado.")

    # Estatísticas gerais
    st.title("Monitoramento de Logs - Tempo Real")
    st.subheader("Estatísticas Gerais")
    st.write(f"Total de Logs Filtrados: {len(filtered_logs)}")
    st.write(f"Logs Críticos (ERROR): {len(filtered_logs[filtered_logs['Level'] == 'ERROR'])}")

    # Gráfico de barras: Logs por categoria
    st.subheader("Logs por Categoria")
    category_counts = filtered_logs["Category"].value_counts()
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    category_counts.plot(kind="bar", ax=ax1)
    ax1.set_title("Logs por Categoria")
    ax1.set_xlabel("Categoria")
    ax1.set_ylabel("Número de Logs")
    st.pyplot(fig1)

    # Heatmap: Ocorrências por hora
    st.subheader("Ocorrências de Logs por Hora")
    hourly_logs = filtered_logs.groupby(["Hour", "Level"]).size().unstack(fill_value=0)
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    sns.heatmap(hourly_logs, cmap="coolwarm", ax=ax2)
    ax2.set_title("Heatmap de Ocorrências por Hora")
    st.pyplot(fig2)

    # Destaques de eventos críticos
    st.subheader("Eventos Críticos")
    critical_events = filtered_logs[filtered_logs["Level"] == "ERROR"].sort_values("Timestamp", ascending=False).head(10)
    st.write(critical_events)

    # Exportar logs filtrados
    st.subheader("Exportar Dados Filtrados")
    csv = filtered_logs.to_csv(index=False)
    st.download_button(
        label="Baixar Logs Filtrados",
        data=csv,
        file_name="logs_filtrados.csv",
        mime="text/csv"
    )


