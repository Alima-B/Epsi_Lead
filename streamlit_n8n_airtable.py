## streamlit n8n - airtable

# connexion à airtable et récup des tables
import requests
import os
from dotenv import load_dotenv ,find_dotenv
from os.path import join, dirname
import pandas as pd
import matplotlib.pyplot as plt 
import seaborn as sns 


# --- CONFIGURATION ---
load_dotenv(find_dotenv("base.env"))
BASE_ID = os.getenv("BASE_ID")
PERSONAL_ACCESS_TOKEN = os.getenv("PERSONAL_ACCESS_TOKEN")

# def get_table_as_dataframe(base_id, table_name, token):
#     url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
#     headers = {"Authorization": f"Bearer {token}"}
#     params = {}
#     all_records = []

#     print(f"Récupération des données de la table : {table_name}...")

#     while True:
#         response = requests.get(url, headers=headers, params=params)
#         response.raise_for_status()
#         data = response.json()
        
#         # Extraire les champs (fields) de chaque enregistrement
#         records = [list_item['fields'] for list_item in data['records']]
#         all_records.extend(records)

#         # Gestion de la pagination (offset)
#         offset = data.get("offset")
#         if not offset:
#             break
#         params["offset"] = offset

#     # Création du DataFrame
#     df = pd.DataFrame(all_records)
#     return df

# # --- EXÉCUTION ---
# TABLE_NAME = "Resultat"  

# try:
#     # Récupérer les résultats hebdomadaires
#     df_results = get_table_as_dataframe(BASE_ID, TABLE_NAME, PERSONAL_ACCESS_TOKEN)
    
#     # Affichage des premières lignes et des types de colonnes
#     print("\n--- Aperçu du DataFrame ---")
#     print(df_results.head())
    
# except Exception as e:
#     print(f"Erreur : {e}")
    
    
# # --- EXÉCUTION ---
# TABLE_NAME = "Vertical"  

# try:
#     # Récupérer les résultats hebdomadaires
#     df_vertical = get_table_as_dataframe(BASE_ID, TABLE_NAME, PERSONAL_ACCESS_TOKEN)
    
#     # Affichage des premières lignes et des types de colonnes
#     print("\n--- Aperçu du DataFrame ---")
#     print(df_vertical.head())

# except Exception as e:
#     print(f"Erreur : {e}")
    
#### DASHBOARD STREAMLIT
import streamlit as st

st.write("""# Dashboard n8n_Airtable""")

#récup des df

@st.cache_data
def get_table_as_dataframe(base_id, table_name, token):
    url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
    headers = {"Authorization": f"Bearer {token}"}
    params = {}
    all_records = []

    print(f"Récupération des données de la table : {table_name}...")

    while True:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Extraire les champs (fields) de chaque enregistrement
        records = [list_item['fields'] for list_item in data['records']]
        all_records.extend(records)

        # Gestion de la pagination (offset)
        offset = data.get("offset")
        if not offset:
            break
        params["offset"] = offset

    # Création du DataFrame
    df = pd.DataFrame(all_records)
    return df


df_rst,df_vertical = get_table_as_dataframe(BASE_ID, "Resultat", PERSONAL_ACCESS_TOKEN),\
    get_table_as_dataframe(BASE_ID, "Vertical", PERSONAL_ACCESS_TOKEN)

# barres latérales de filtres
with st.sidebar :
    st.header("Filtre")
    clients = st.sidebar.multiselect("Sélectionner les clients",
                                  options = df_rst["clientName"].unique(),
                                  default = df_rst["clientName"].unique())
    date = st.sidebar.multiselect("Date"
                                  ,options = df_rst["weekStarting"].unique(),
                                  default = df_rst["weekStarting"].unique())


# filtre les dataframe
mask_rst = df_rst["clientName"].isin(clients)
mask_vert = df_vertical["client"].isin(clients)
df_filtered_rst = df_rst[mask_rst]
df_filtered_vert = df_vertical[mask_vert]


st.dataframe(df_filtered_vert)
st.dataframe(df_filtered_rst)

#KPI
total_revenue = df_filtered_rst["totalRevenue"].sum()
total_profit = df_filtered_rst["totalProfit"].sum()
avg_pace = "Ahead" if (df_filtered_rst["projected"].sum() > df_filtered_rst["weeklyTarget"].sum()) else "Behind"

col1, col2, col3 = st.columns(3)
col1.metric("Chiffre d'Affaires Total", f"{total_revenue:,.2f} $",border = True)
col2.metric("Profit Total", f"{total_profit:,.2f} $", f"{ (total_profit/total_revenue)*100:.1f}% de marge",border = True)
col3.metric("Tendance Globale", avg_pace,border = True)

st.divider()


# 4. Visualisations
st.subheader("📊 Analyses Comparatives")
left_col, right_col = st.columns(2)

# Graphique 1 : Ventes vs Objectifs (Seaborn)
with left_col:
    st.write("**Ventes Réelles vs Objectifs**")
    
    # Transformation des données pour Seaborn (format long)
    df_melted = df_filtered_rst.melt(
        id_vars="clientName", 
        value_vars=["totalSold", "weeklyTarget"],
        var_name="Type", 
        value_name="Unités"
    )
    
    # Création du plot
    fig_bar, ax_bar = plt.subplots(figsize=(10, 6))
    sns.barplot(
        data=df_melted, 
        x="clientName", 
        y="Unités", 
        hue="Type", 
        palette=["#00CC96", "#EF553B"],
        ax=ax_bar
    )
    ax_bar.set_xticklabels(ax_bar.get_xticklabels(), rotation=45, ha='right')
    ax_bar.set_title("Comparaison Performance Hebdomadaire")
    ax_bar.set_xlabel("")
    
    st.pyplot(fig_bar)

# Graphique 2 : Répartition du Profit (Matplotlib)
with right_col:
    st.write("**Répartition du Profit par Client**")
    
    # Préparation des données
    labels = df_filtered_rst['clientName']
    sizes = df_filtered_rst['totalProfit']
    
    fig_pie, ax_pie = plt.subplots(figsize=(8, 8))
    
    # Création du Pie Chart (Donut)
    wedges, texts, autotexts = ax_pie.pie(
        sizes, 
        labels=labels, 
        autopct='%1.1f%%', 
        startangle=140,
        colors=sns.color_palette("viridis", len(labels)),
        wedgeprops=dict(width=1) # Effet Donut
    )
    
    # Style des étiquettes
    plt.setp(autotexts, size=10, weight="bold", color="white")
    ax_pie.set_title("Part du Profit Total")
    
    st.pyplot(fig_pie)

st.divider()

st.subheader("Détails par Dimension (Vertical/State)")
dimension_type = st.selectbox("Filtrer par type de vue", options=df_filtered_vert["type"].unique())
df_dim_view = df_filtered_vert[df_filtered_vert["type"] == dimension_type]

st.dataframe(df_dim_view.style.highlight_max(axis=0, subset=['tpRevenue']), use_container_width=True)


# taux de perte global
waste_rate = (df_filtered_rst['gwUnsold'].sum() / df_filtered_rst['gwGenerated'].sum()) * 100 if df_filtered_rst['gwGenerated'].sum() > 0 else 0

# 2. Section "Analyse du Mix"
st.subheader("🎯 Analyse du Mix Produit & Efficacité")
c1, c2 = st.columns(2)

with c1:
    st.metric("Taux de Perte Global", f"{waste_rate:.1f}%", delta="-5%" if waste_rate < 20 else "+2%", delta_color="inverse")
    

    
# 3. Tableau d'alerte (Action Items)
st.subheader("⚠️ Actions Requises Immédiates")
actions = df_filtered_rst[df_filtered_rst['action'] != "OK"][['clientName', 'action', 'pace']]
if not actions.empty:
    st.table(actions)
else:
    st.success("Toutes les lignes sont 'OK' ou 'On Track' !")
