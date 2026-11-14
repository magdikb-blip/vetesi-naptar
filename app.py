import streamlit as st
from google import genai

st.set_page_config(page_title="MI Vetési Naptár", page_icon="🌱")

st.title("🌱 Intelligens Vetési Naptár")
st.write("Írd be a növény nevét, és máris mutatom a legfontosabb vetési tudnivalókat!")

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

noveny = st.text_input("Milyen növényt szeretnél elvetni?", placeholder="Pl.: borsó, paradicsom, bazsalikom...")

if st.button("Adatok lekérése", type="primary"):
    if not noveny:
        st.warning("Előbb írj be egy növénynevet!")
    else:
        with st.spinner("Keresés..."):
            try:
                # Rövid, közvetlen kérdés - pontosan olyan gyors, mint a normál chat
                kerdes = f"""
                Kertészmérnökként foglald össze röviden, átlátható pontokban a következő növény vetési adatait magyarul: {noveny}.
                Csak ezeket a pontokat írd le röviden:
                - **Kategória:**
                - **Vetési idő:**
                - **Csírázási idő:**
                - **Fényigény:**
                - **Öntözés és gondozás:**
                - **Jó szomszédok (társültetés):**
                """
                
                valasz = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=kerdes
                )
                
                st.success(f"🌿 {noveny.capitalize()}")
                st.markdown(valasz.text)
                
            except Exception as e:
                st.error(f"Hiba: {e}")
