import streamlit as st
import pandas as pd

st.set_page_config(page_title="Consigliere Fantacalcio", page_icon="⚽", layout="wide")

st.title("⚽ Il Mio Consigliere Fantacalcio")
st.write("Modifica la tua rosa e calcola i titolari per la giornata.")

# Algoritmo di calcolo dell'indice di schierabilità
def calcola_indice(g):
    f_storico = min(max(((g['fantamedia'] - 3.0) / 7.0) * 100 + (5 if g['rigorista'] else 0), 0), 100)
    f_forma = min(max(((g['fantamedia_ultime_3'] - 3.0) / 7.0) * 100, 0), 100)
    f_partita = min(g['difficolta_partita'] + (10 if g['in_casa'] else 0), 100)
    f_titolare = g['probabilita_titolarita']
    return round((0.35 * f_storico) + (0.25 * f_forma) + (0.25 * f_partita) + (0.15 * f_titolare), 1)

# Lista iniziale di giocatori di esempio
if 'rosa' not in st.session_state:
    st.session_state.rosa = [
        {"nome": "Lautaro Martinez", "squadra": "Inter", "ruolo": "A", "fantamedia": 8.5, "fantamedia_ultime_3": 9.0, "rigorista": True, "probabilita_titolarita": 90, "difficolta_partita": 80, "in_casa": True},
        {"nome": "Barella", "squadra": "Inter", "ruolo": "C", "fantamedia": 7.2, "fantamedia_ultime_3": 7.5, "rigorista": False, "probabilita_titolarita": 85, "difficolta_partita": 75, "in_casa": True},
        {"nome": "Dimarco", "squadra": "Inter", "ruolo": "D", "fantamedia": 6.8, "fantamedia_ultime_3": 7.0, "rigorista": False, "probabilita_titolarita": 90, "difficolta_partita": 75, "in_casa": True},
        {"nome": "Sommer", "squadra": "Inter", "ruolo": "P", "fantamedia": 6.0, "fantamedia_ultime_3": 6.0, "rigorista": False, "probabilita_titolarita": 95, "difficolta_partita": 85, "in_casa": True},
    ]

modulo = st.sidebar.selectbox("Modulo:", ["3-4-3", "4-3-3", "4-4-2", "3-5-2"])

st.subheader("📋 Gestisci la tua Rosa")
df_rosa = pd.DataFrame(st.session_state.rosa)

df_modificato = st.data_editor(
    df_rosa,
    num_rows="dynamic",
    column_config={
        "ruolo": st.column_config.SelectboxColumn("Ruolo", options=["P", "D", "C", "A"]),
        "rigorista": st.column_config.CheckboxColumn("Rigorista"),
        "in_casa": st.column_config.CheckboxColumn("Casa"),
    },
    use_container_width=True
)

if st.button("🚀 Calcola Formazione Migliore"):
    dati = df_modificato.to_dict(orient="records")
    for g in dati:
        g['punteggio'] = calcola_indice(g)
    
    df_res = pd.DataFrame(dati)
    
    portieri = df_res[df_res['ruolo'] == 'P'].sort_values(by='punteggio', ascending=False)
    difensori = df_res[df_res['ruolo'] == 'D'].sort_values(by='punteggio', ascending=False)
    centrocampisti = df_res[df_res['ruolo'] == 'C'].sort_values(by='punteggio', ascending=False)
    attaccanti = df_res[df_res['ruolo'] == 'A'].sort_values(by='punteggio', ascending=False)

    num_d, num_c, num_a = map(int, modulo.split('-'))

    titolari = pd.concat([portieri.head(1), difensori.head(num_d), centrocampisti.head(num_c), attaccanti.head(num_a)])

    st.success(f"Formazione Titolare Consigliata ({modulo}):")
    st.dataframe(titolari[['nome', 'ruolo', 'squadra', 'punteggio']], use_container_width=True)
