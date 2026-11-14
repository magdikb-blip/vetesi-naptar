import streamlit as st
from google import genai
import json
import requests

# 1. Weboldal alapbeállításai
st.set_page_config(page_title="MI Vetési Naptár", page_icon="🌱", layout="centered")

st.title("🌱 Intelligens Vetési Naptár")
st.write("Írd be a növény nevét, és a mesterséges intelligencia megadja a legfontosabb vetési és gondozási tudnivalókat!")

# 2. Kapcsolódás az MI-hez
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Segédfüggvény a növény fotójának lekéréséhez a Wikipédiáról
def noveny_kep_keresese(latin_nev):
    url = "https://wikipedia.org"
    params = {
        "action": "query",
        "format": "json",
        "titles": latin_nev,
        "prop": "pageimages",
        "pithumbsize": 600,
        "redirects": 1
    }
    headers = {"User-Agent": "VetesiNaptarApp/1.0"}
    try:
        valasz = requests.get(url, params=params, headers=headers, timeout=5).json()
        oldalak = valasz.get("query", {}).get("pages", {})
        for oldal_id, adat in oldalak.items():
            if "thumbnail" in adat:
                return adat["thumbnail"]["source"]
    except Exception:
        return None
    return None

# 3. Felhasználói beviteli mező
noveny = st.text_input("Milyen növényt szeretnél elvetni?", placeholder="Pl.: koktélparadicsom, sárgarépa, bazsalikom...")

# 4. Gombnyomásra induló folyamat
if st.button("Adatok lekérése", type="primary"):
    if not noveny:
        st.warning("Kérlek, előbb írd be egy növény nevét!")
    else:
        with st.spinner("Az MI elemzi a növény igényeit és keresi a fotót..."):
            try:
                prompt = f"""
                Te egy tapasztalt kertészmérnök vagy. A felhasználó a következő növényt szeretné termeszteni: '{noveny}'.
                Add meg a növény legfontosabb adatait magyar nyelven, kizárólag az alábbi JSON formátumban, mindenféle extra szöveg nélkül:
                {{
                    "nev": "A növény pontos magyar neve",
                    "latin_nev": "A növény tudományos latin neve (pl. Solanum lycopersicum)",
                    "kategoria": "Zöldség / Gyümölcs / Fűszernövény / Virág",
                    "vetesi_ido": "Mikor kell elvetni (palántázás és szabadföld külön jelölve)",
                    "csirazasi_ido": "Hány nap alatt csírázik ki és hány fokon",
                    "fenyigeny": "Napos / Félárnyékos / Árnyékos (rövid magyarázattal)",
                    "ontozes": "Vízigény és öntözési javaslat",
                    "tarsultetes": "Mit érdemes mellé ültetni, és mit tilos",
                    "pro_tipp": "Egy hasznos kertészeti jótanács ehhez a növényhez"
                }}
                """
                
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=prompt,
                )
                
                tiszta_szoveg = response.text.replace("```json", "").replace("```", "").strip()
                adatok = json.loads(tiszta_szoveg)
                
                kep_url = noveny_kep_keresese(adatok['latin_nev'])
                
                st.success(f"Sikeres elemzés: **{adatok['nev']}** (*{adatok['latin_nev']}*) – {adatok['kategoria']}")
                
                if kep_url:
                    col_bal, col_kozep, col_jobb = st.columns([1, 2, 1])
                    with col_kozep:
                        st.image(kep_url, caption=f"{adatok['nev']} ({adatok['latin_nev']})", use_container_width=True)
                
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
                st.error(f"Részletes hibaüzenet: {e}")
