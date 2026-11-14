import streamlit as st
from google import genai
from google.genai import types
import json
import requests

# 1. Weboldal alapbeállításai
st.set_page_config(page_title="MI Vetési Naptár", page_icon="🌱", layout="centered")

st.title("🌱 Intelligens Vetési Naptár")
st.write("Írd be a növény nevét, és a mesterséges intelligencia megadja a legfontosabb vetési és gondozási tudnivalókat!")

# 2. Kapcsolódás az MI-hez
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Gyorsítótárazott képkereső függvény
@st.cache_data(show_spinner=False)
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
        valasz = requests.get(url, params=params, headers=headers, timeout=3).json()
        oldalak = valasz.get("query", {}).get("pages", {})
        for oldal_id, adat in oldalak.items():
            if "thumbnail" in adat:
                return adat["thumbnail"]["source"]
    except Exception:
        return None
    return None

# Gyorsítótárazott MI lekérdezés (ha egyszer már kerested, azonnal betölti)
@st.cache_data(show_spinner=False)
def noveny_adatok_lekerese(noveny_nev):
    prompt = f"""
    Te egy tapasztalt kertészmérnök vagy. A felhasználó ezt a növényt szeretné termeszteni: '{noveny_nev}'.
    Add meg a növény adatait magyar nyelven, kizárólag az alábbi JSON formátumban:
    {{
        "nev": "Pontos magyar név",
        "latin_nev": "Tudományos latin név (pl. Solanum lycopersicum)",
        "kategoria": "Zöldség / Gyümölcs / Fűszernövény / Virág",
        "vetesi_ido": "Mikor kell elvetni (palántázás és szabadföld külön)",
        "csirazasi_ido": "Hány nap alatt csírázik ki és hány fokon",
        "fenyigeny": "Napos / Félárnyékos / Árnyékos (rövid magyarázat)",
        "ontozes": "Vízigény és öntözési javaslat",
        "tarsultetes": "Mit érdemes mellé ültetni, és mit tilos",
        "pro_tipp": "Egy hasznos kertészeti jótanács"
    }}
    """
    
    # A thinking_budget=0 kikapcsolja a lassú gondolkodási fázist, a response_mime_type pedig garantálja a tiszta JSON-t
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        thinking_config=types.ThinkingConfig(thinking_budget=0)
    )
    
    # Ha az első modell túlterhelt, azonnal átvált a tartalékra várakozás nélkül
    for modell_nev in ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-3.8-flash"]:
        try:
            response = client.models.generate_content(
                model=modell_nev,
                contents=prompt,
                config=config
            )
            return json.loads(response.text)
        except Exception:
            continue
    raise Exception("Minden szerver túlterhelt, próbáld újra pár másodperc múlva.")

# 3. Felhasználói beviteli mező
noveny = st.text_input("Milyen növényt szeretnél elvetni?", placeholder="Pl.: koktélparadicsom, sárgarépa, bazsalikom...")

# 4. Gombnyomásra induló folyamat
if st.button("Adatok lekérése", type="primary"):
    if not noveny:
        st.warning("Kérlek, előbb írd be egy növény nevét!")
    else:
        with st.spinner("Villámgyors elemzés folyamatban..."):
            try:
                adatok = noveny_adatok_lekerese(noveny.strip().lower())
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
                st.error(f"Hiba történt: {e}")
