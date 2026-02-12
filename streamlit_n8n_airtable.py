## streamlit n8n - airtable

# connexion à airtable et récup des tables
import requests
import os
from dotenv import load_dotenv ,find_dotenv
from os.path import join, dirname
import pandas as pd

# --- CONFIGURATION ---
load_dotenv(find_dotenv("base.env"))
BASE_ID = os.getenv("BASE_ID")
PERSONAL_ACCESS_TOKEN = os.getenv("PERSONAL_ACCESS_TOKEN")

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

# --- EXÉCUTION ---
TABLE_NAME = "Resultat"  

try:
    # Récupérer les résultats hebdomadaires
    df_results = get_table_as_dataframe(BASE_ID, TABLE_NAME, PERSONAL_ACCESS_TOKEN)
    
    # Affichage des premières lignes et des types de colonnes
    print("\n--- Aperçu du DataFrame ---")
    print(df_results.head())
    
except Exception as e:
    print(f"Erreur : {e}")
    
    
# --- EXÉCUTION ---
TABLE_NAME = "Vertical"  

try:
    # Récupérer les résultats hebdomadaires
    df_vertical = get_table_as_dataframe(BASE_ID, TABLE_NAME, PERSONAL_ACCESS_TOKEN)
    
    # Affichage des premières lignes et des types de colonnes
    print("\n--- Aperçu du DataFrame ---")
    print(df_vertical.head())

except Exception as e:
    print(f"Erreur : {e}")
    
#### DASHBOARD STREAMLIT
import streamlit as st