import streamlit as st
from google import genai

st.set_page_config(page_title="MI Vetési Naptár", page_icon="🌱")

st.title("🌱 Intelligens Vetési Naptár")
st.write("Írd be a növény nevét, és máris mutatom a legfontosabb vetési tudnivalókat!")

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Automatikusan kikeresi a fiókodhoz elérhető legjobb modellt
@st.cache_resource
def elerheto_modell_keresese():
    try:
        modellek = [m.name for m in client.models.list() if "generateContent" in (m.supported_actions or [])]
        for kulcsszo in ["flash-lite", "flash", "gemini"]:
            for m in modellek:
                if kulcsszo in m and "vision" not in m and "image" not in m:
                    return m
        if modellek:
            return modellek[0]
    except Exception:
        pass
    return "gemini-3.8-flash"

modell_nev = elerheto_modell_keresese()

noveny = st.text_input("Milyen növényt szeretnél elvetni?", placeholder="Pl.: borsó, paradicsom, bazsalikom...")

if st.button("Adatok lekérése", type="primary"):
    if not noveny:
        st.warning("Előbb írj be egy növénynevet!")
    else:
        with st.spinner("Keresés..."):
            try:
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
                    model=modell_nev,
                    contents=kerdes
                )
                
                st.success(f"🌿 {noveny.capitalize()}")
                st.markdown(valasz.text)
                
            except Exception as e:
                st.error(f"Hiba ({modell_nev}): {e}")
