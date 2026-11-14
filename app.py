import streamlit as st
from google import genai
import json

# 1. Weboldal alapbeállításai
st.set_page_config(page_title="MI Vetési Naptár", page_icon="🌱", layout="centered")

st.title("🌱 Intelligens Vetési Naptár")
st.write("Írd be a növény nevét, és a mesterséges intelligencia megadja a legfontosabb vetési és gondozási tudnivalókat!")

# 2. Kapcsolódás az MI-hez (az API kulcsot a biztonságos tárolóból olvassa ki)
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# 3. Felhasználói beviteli mező
noveny = st.text_input("Milyen növényt szeretnél elvetni?", placeholder="Pl.: koktélparadicsom, sárgarépa, bazsalikom...")

# 4. Gombnyomásra induló folyamat
if st.button("Adatok lekérése", type="primary"):
    if not noveny:
        st.warning("Kérlek, előbb írd be egy növény nevét!")
    else:
        with st.spinner("Az MI elemzi a növény igényeit..."):
            try:
                # Szigorú utasítás (Prompt), hogy mindig ugyanolyan szerkezetben válaszoljon
                prompt = f"""
                Te egy tapasztalt kertészmérnök vagy. A felhasználó a következő növényt szeretné termeszteni: '{noveny}'.
                Add meg a növény legfontosabb adatait magyar nyelven, kizárólag az alábbi JSON formátumban, mindenféle extra szöveg nélkül:
                {{
                    "nev": "A növény pontos magyar neve",
                    "kategoria": "Zöldség / Gyümölcs / Fűszernövény / Virág",
                    "vetesi_ido": "Mikor kell elvetni (palántázás és szabadföld külön jelölve)",
                    "csirazasi_ido": "Hány nap alatt csírázik ki és hány fokon",
                    "fenyigeny": "Napos / Félárnyékos / Árnyékos (rövid magyarázattal)",
                    "ontozes": "Vízigény és öntözési javaslat",
                    "tarsultetes": "Mit érdemes mellé ültetni, és mit tilos",
                    "pro_tipp": "Egy hasznos kertészeti jótanács ehhez a növényhez"
                }}
                """
                
                # Válasz kérése a Gemini modelltől
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                )
                
                # A kapott szöveg megtisztítása és átalakítása Python szótárrá
                tiszta_szoveg = response.text.replace("```json", "").replace("```", "").strip()
                adatok = json.loads(tiszta_szoveg)
                
                # 5. Eredmények látványos megjelenítése a felületen
                st.success(f"Sikeres elemzés: **{adatok['nev']}** ({adatok['kategoria']})")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"📅 **Vetési idő:**\n\n{adatok['vetesi_ido']}")
                    st.warning(f"☀️ **Fényigény:**\n\n{adatok['fenyigeny']}")
                with col2:
                    st.info(f"⏱️ **Csírázási idő:**\n\n{adatok['csirazasi_ido']}")
                    st.warning(f"💧 **Öntözés:**\n\n{adatok['ontozes']}")
                
                st.markdown("---")
                st.write(f"🤝 **Társültetés:** {adatok['tarsultetes']}")
                st.write(f"💡 **Kertész tipp:** {adatok['pro_tipp']}")
                
            except Exception as e:
                st.error("Hiba történt az adatok feldolgozása közben. Kérlek, próbáld újra egy másik növénnyel!")
