import streamlit as st
import pandas as pd
from datetime import datetime
import scraper

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Szélrózsa Családi Tervező",
    page_icon="🏹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. PREMIUM BRANDED STYLE INJECTION ---
# Using strict high-contrast styling with explicit colors
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400;1,600&family=Quicksand:wght@400;500;600;700&display=swap');

    /* Global settings overrides */
    .stApp {
        font-family: 'Quicksand', sans-serif !important;
    }
    
    /* Global heading overrides */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Barlow', sans-serif !important;
        font-weight: 700 !important;
        color: #0d5c94 !important; /* Deep Blue for visibility */
    }

    /* Branded Header Banner */
    .header-banner {
        background: linear-gradient(135deg, #0e76bc 0%, #1b4d6e 100%);
        padding: 24px;
        border-radius: 12px;
        color: #ffffff !important;
        margin-bottom: 20px;
        box-shadow: 0 4px 10px rgba(14, 118, 188, 0.15);
        border: 2px solid #0e76bc;
    }
    .header-banner h1 {
        color: #ffffff !important;
        margin: 0 !important;
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    .header-banner p {
        color: #f1f5f9 !important;
        font-size: 1.05rem !important;
        margin-top: 6px !important;
        margin-bottom: 0 !important;
    }

    /* Card styling */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff !important;
        border: 2px solid #cbd5e1 !important;
        border-radius: 12px !important;
        padding: 18px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05) !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #0e76bc !important;
        box-shadow: 0 4px 12px rgba(14, 118, 188, 0.12) !important;
    }
    
    /* Clean text color overrides for readability inside Streamlit */
    .program-title {
        color: #0f172a !important;
        font-family: 'Barlow', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1.3rem !important;
        margin-bottom: 8px !important;
    }
    
    /* High contrast custom metadata badges */
    .badge-container {
        margin: 8px 0;
    }
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        margin-right: 6px;
        margin-bottom: 6px;
        border: 1px solid transparent;
    }
    .badge-time { background-color: #e0f2fe; color: #0369a1; border-color: #bae6fd; }
    .badge-location { background-color: #f3e8ff; color: #6b21a8; border-color: #e9d5ff; }
    .badge-duration { background-color: #fef3c7; color: #92400e; border-color: #fde68a; }
    .badge-tag { background-color: #f1f5f9; color: #334155; border-color: #e2e8f0; }

    /* Timeline slot grouping */
    .timeline-time {
        font-family: 'Barlow', sans-serif !important;
        font-weight: 800 !important;
        color: #1e293b !important;
        font-size: 1.25rem !important;
        border-bottom: 3px solid #cbd5e1;
        padding-bottom: 6px;
        margin-top: 24px;
        margin-bottom: 12px;
    }

    .family-together-card {
        background-color: #ecfdf5 !important;
        border: 2px solid #10b981 !important;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.1);
    }
    .family-together-card strong {
        color: #065f46 !important;
        font-size: 1.15rem;
    }
    .family-together-card em {
        color: #047857 !important;
    }
    .family-together-card span {
        color: #065f46 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. SCRAPER DATA LOAD & CACHING ---
import os
import json
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
PROGRAMS_FILE = os.path.join(ROOT_PATH, "programs_database.json")
GITHUB_RAW_URL = "https://raw.githubusercontent.com/mnemeth1992/Sz-lr-zsa-App/main/programs_database.json"

@st.cache_resource
def _load_programs_once():
    """Loads programs exactly once per server lifetime."""
    import requests

    # 1. Try local file first (fastest)
    if os.path.exists(PROGRAMS_FILE):
        try:
            print(f"[CACHE] Helyi JSON betöltése: {PROGRAMS_FILE}")
            with open(PROGRAMS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data:
                print(f"[CACHE] {len(data)} program betöltve helyileg.")
                return data
        except Exception as e:
            print(f"[CACHE] Helyi JSON hiba: {e}")

    # 2. Download from GitHub raw URL (works on Streamlit Cloud regardless of path)
    try:
        print(f"[CACHE] GitHub-ról töltés: {GITHUB_RAW_URL}")
        r = requests.get(GITHUB_RAW_URL, timeout=15)
        if r.status_code == 200:
            data = r.json()
            print(f"[CACHE] {len(data)} program letöltve GitHub-ról.")
            return data
        else:
            print(f"[CACHE] GitHub hiba: {r.status_code}")
    except Exception as e:
        print(f"[CACHE] GitHub letöltési hiba: {e}")

    # 3. Last resort: run the scraper
    print(f"[CACHE] Scraper futtatása végső esetként...")
    programs = scraper.scrape_programs()
    print(f"[CACHE] Scraper lefutott: {len(programs)} program.")
    return programs

def get_scraped_programs():
    return _load_programs_once()

# Force clear cache action helper
if 'clear_cache' in st.session_state and st.session_state.clear_cache:
    st.cache_resource.clear()
    st.session_state.clear_cache = False


# --- 4. SESSION STATE INITIALIZATION ---
if 'programok' not in st.session_state:
    st.session_state.programok = get_scraped_programs()

# Fallback program list
if not st.session_state.programok:
    st.session_state.programok = [
        {"id": 1, "nev": "Nyitó áhítat (Szerverhiba esetén)", "idopont": "2026-07-08 17:00", "tartam_perc": 60, "helyszin": "Zajforrás", "cimkek": ["lelki alkalom"], "leiras": "Nem sikerült lekölteni az adatokat a szerverről."}
    ]

import json
import os

# Absolute path resolution
SELECTIONS_FILE = os.path.join(ROOT_PATH, "csalad_selections.json")

def load_selections():
    if not os.path.exists(SELECTIONS_FILE):
        return {
            "csaladtagok": ["Anya", "Apa", "Gyerkőc 1", "Gyerkőc 2"],
            "valasztott": {"Anya": [], "Apa": [], "Gyerkőc 1": [], "Gyerkőc 2": []},
            "custom_durations": {}
        }
    try:
        with open(SELECTIONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "csaladtagok" not in data:
                data["csaladtagok"] = ["Anya", "Apa", "Gyerkőc 1", "Gyerkőc 2"]
            if "valasztott" not in data:
                data["valasztott"] = {tag: [] for tag in data["csaladtagok"]}
            if "custom_durations" not in data:
                data["custom_durations"] = {}
            return data
    except Exception:
        return {
            "csaladtagok": ["Anya", "Apa", "Gyerkőc 1", "Gyerkőc 2"],
            "valasztott": {"Anya": [], "Apa": [], "Gyerkőc 1": [], "Gyerkőc 2": []},
            "custom_durations": {}
        }

def save_selections():
    try:
        data = {
            "csaladtagok": st.session_state.csaladtagok,
            "valasztott": st.session_state.valasztott,
            "custom_durations": st.session_state.custom_durations
        }
        with open(SELECTIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"Hiba a mentéskor: {e}")

# Load saved selections
saved_data = load_selections()

if 'csaladtagok' not in st.session_state:
    st.session_state.csaladtagok = saved_data["csaladtagok"]

if 'valasztott' not in st.session_state:
    st.session_state.valasztott = saved_data["valasztott"]

# Ensure all current members exist in valasztott
for tag in st.session_state.csaladtagok:
    if tag not in st.session_state.valasztott:
        st.session_state.valasztott[tag] = []

if 'custom_durations' not in st.session_state:
    st.session_state.custom_durations = saved_data["custom_durations"]

# --- 5. HELPER FUNCTIONS ---

LOCATION_NUMBERS = {
    "Színházterem (Winkler terem - GYIK)": 1,
    "Színházterem (Winkler terem)": 1,
    "Borostyán terem (GYIK)": 2,
    "Borostyán terem": 2,
    "ODÚ": 3,
    "Baba-mama szoba": 4,
    "Kuckó (GYIK)": 4,
    "Mevisz": 5,
    "MEVISZ": 5,
    "Wycliffe Bibliafordítók | Ébenkert": 6,
    "Csillagpont Fesztivál": 7,
    "Ifjúságépítők": 8,
    "Fridays for Future": 9,
    "Winddogs sportegyesület": 10,
    "Diakónia MENTA": 11,
    "NOO-EPSZTI": 12,
    "Egyházmegyei sátor": 13,
    "HEL-O Sátor": 14,
    "HEL-O sátor": 14,
    "Külügy Café": 15,
    "Luther Kiadó": 16,
    "Magyar Bibliatársulat Alapítvány": 17,
    "Magyar Bibliatársulat": 17,
    "KözösPont (ÖKI)": 18,
    "MBH Bank Zenepavilon": 19,
    "BIGI's | Kincses": 20,
    "Alkotóház (Kötcse)": 21,
    "Játékliget": 22,
    "Ökosátor": 23,
    "UNIverzum": 24,
    "KÖSZI Koktélbár": 25,
    "KÖSZI koktélbár": 25,
    "TEKI Kávéház": 26,
    "TEKI kávéház": 26,
    "EHE+Melanchthon": 27,
    "EHE + Melanchthon sátor": 27,
    "FunFészek": 28,
    "Kézműves sátor": 29,
    "Kézművessátor": 29,
    "Zajforrás": 30,
    "MÖS": 31,
    "Szélrózsa 30": 32,
    "E-hangműhely sátor": 33,
    "E-Hangműhely sátor": 33,
    "International Tent": 34,
    "Küldetés sátor": 35,
    "KIE sátor": 36,
    "KIE-sátor": 36,
    "Aula": 37,
    "Kiállítások (Aula és folyosó - P épület)": 37,
    "Csendkuckó (P-118-3)": 38,
    "Csendkuckó": 38,
    "Csendkuckó (P-139)": 39,
    "Fórum (P-109)": 40,
    "Filmklub (P-109)": 40,
    "Fórum, filmklub": 40,
    "Személyiségvédelem": 41,
    "Lelkigondozói sátor": 42,
    "Szabadulószoba": 43,
    "Szabadulószoba I.": 43,
    "Szabadulószoba II.": 44,
    "Szabadulószoba III.": 45,
    "Szélrózsa Ovi": 46,
    "Szélrózsa ovi": 46
}

def get_location_number(loc_name):
    if not loc_name:
        return ""
    if loc_name in LOCATION_NUMBERS:
        return f"#{LOCATION_NUMBERS[loc_name]}"
    for k, v in LOCATION_NUMBERS.items():
        if k.lower() in loc_name.lower() or loc_name.lower() in k.lower():
            return f"#{v}"
    return ""

def save_uploaded_file(uploaded_file):
    try:
        import os
        target_path = os.path.join(ROOT_PATH, "uploaded_map.png")
        with open(target_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return True
    except Exception as e:
        st.error(f"Hiba a fájl mentésekor: {e}")
        return False

def map_day_name(dt_str):
    if not dt_str:
        return "Nincs megadva nap"
    try:
        date_part = dt_str.split(" ")[0]
        mapping = {
            "2026-07-08": "Szerda (07.08)",
            "2026-07-09": "Csütörtök (07.09)",
            "2026-07-10": "Péntek (07.10)",
            "2026-07-11": "Szombat (07.11)",
            "2026-07-12": "Vasárnap (07.12)"
        }
        return mapping.get(date_part, date_part)
    except Exception:
        return dt_str

# Dialog compatibility layer for mapping helper
if hasattr(st, "dialog"):
    @st.dialog("📍 Helyszín Kereső")
    def mutasd_terkepet(helyszin, szam):
        render_map_modal_content(helyszin, szam)
else:
    def mutasd_terkepet(helyszin, szam):
        with st.expander(f"🗺️ Helyszín Kereső: {helyszin} (#{szam})", expanded=True):
            render_map_modal_content(helyszin, szam)

def render_map_modal_content(helyszin, szam):
    st.markdown(f"### 📍 Helyszín: {helyszin} (Szám: **#{szam}**)")
    
    part_img = None
    part_name = ""
    try:
        num_int = int(szam)
        if 31 <= num_int <= 46:
            part_img = "map_part1.jpg"
            part_name = "1. rész (Baloldal: Helyszínlista és P épület)"
        elif 18 <= num_int <= 30:
            part_img = "map_part2.jpg"
            part_name = "2. rész (Középső terület: Erzsébet-kert)"
        elif 1 <= num_int <= 17:
            part_img = "map_part3.jpg"
            part_name = "3. rész (Jobboldal: GYIK & Bánfalvi út)"
    except Exception:
        pass
        
    import os
    if part_img and os.path.exists(os.path.join(ROOT_PATH, part_img)):
        st.image(os.path.join(ROOT_PATH, part_img), caption=part_name, use_container_width=True)
    elif os.path.exists(os.path.join(ROOT_PATH, "full_map.jpg")):
        st.image(os.path.join(ROOT_PATH, "full_map.jpg"), caption="Egyesített térkép", use_container_width=True)
    else:
        st.warning("Térkép kép nem érhető el.")

def ellenoriz_utkozeseket_reszletes(tag):
    valasztott_ids = st.session_state.valasztott.get(tag, [])
    if not valasztott_ids:
        return {}
        
    intervals = []
    for p_id in valasztott_ids:
        p = next((prog for prog in st.session_state.programok if prog["id"] == p_id), None)
        if not p or not p["idopont"]:
            continue
        try:
            kezdete = datetime.strptime(p["idopont"], "%Y-%m-%d %H:%M")
            duration = st.session_state.custom_durations.get(f"{tag}_{p_id}", p["tartam_perc"] or 60)
            vege = kezdete + pd.Timedelta(minutes=duration)
            intervals.append({
                "id": p_id,
                "nev": p["nev"],
                "kezdete": kezdete,
                "vege": vege,
                "idopont_str": p["idopont"][-5:]
            })
        except Exception:
            continue
            
    utkozesek = {}
    for i in range(len(intervals)):
        p1 = intervals[i]
        for j in range(i + 1, len(intervals)):
            p2 = intervals[j]
            # Check for overlap
            if p1["kezdete"] < p2["vege"] and p2["kezdete"] < p1["vege"]:
                if p1["id"] not in utkozesek:
                    utkozesek[p1["id"]] = []
                if p2["id"] not in utkozesek:
                    utkozesek[p2["id"]] = []
                utkozesek[p1["id"]].append(f"{p2['nev']} ({p2['idopont_str']} - {p2['vege'].strftime('%H:%M')})")
                utkozesek[p2["id"]].append(f"{p1['nev']} ({p1['idopont_str']} - {p1['vege'].strftime('%H:%M')})")
                
    return utkozesek

def generate_ics_data(tag):
    valasztott_ids = st.session_state.valasztott.get(tag, [])
    if not valasztott_ids:
        return ""
        
    ics_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Szelrozsa Csalad//HU",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH"
    ]
    
    for p_id in valasztott_ids:
        p = next((prog for prog in st.session_state.programok if prog["id"] == p_id), None)
        if p and p["idopont"]:
            try:
                kezdete = datetime.strptime(p["idopont"], "%Y-%m-%d %H:%M")
                duration = st.session_state.custom_durations.get(f"{tag}_{p_id}", p["tartam_perc"] or 60)
                vege = kezdete + pd.Timedelta(minutes=duration)
                
                start_str = kezdete.strftime("%Y%m%dT%H%M%S")
                end_str = vege.strftime("%Y%m%dT%H%M%S")
                
                desc = p.get("leiras", "").replace("\n", " ").replace(",", "\\,").replace(";", "\\;")
                
                ics_lines.extend([
                    "BEGIN:VEVENT",
                    f"UID:szelrozsa_26_{p_id}_{tag}@szelrozsatalalkozo.hu",
                    f"DTSTART;TZID=Europe/Budapest:{start_str}",
                    f"DTEND;TZID=Europe/Budapest:{end_str}",
                    f"SUMMARY:{p['nev']}",
                    f"LOCATION:{p['helyszin']}",
                    f"DESCRIPTION:{desc}",
                    "END:VEVENT"
                ])
            except Exception:
                pass
                
    ics_lines.append("END:VCALENDAR")
    return "\n".join(ics_lines)

# --- 6. APP HEADER BANNER ---
st.markdown("""
<div class="header-banner">
    <h1>🏹 Szélrózsa Családi Tervező</h1>
    <p>Tervezzétek meg közösen a programotokat! A fesztivál valós programjainak élő szinkronizálásával.</p>
</div>
""", unsafe_allow_html=True)

# --- 7. SIDEBAR MANAGEMENT ---
with st.sidebar:
    st.image("https://www.szelrozsatalalkozo.hu/images/szr26_feszt_webhez_lapos_logo_fejlecbe_2.svg", width=180)
    
    st.header("👥 Családtagok")
    for index, tag in enumerate(st.session_state.csaladtagok):
        col_tag, col_del = st.columns([4, 1])
        with col_tag:
            st.markdown(f"**👤 {tag}** ({len(st.session_state.valasztott.get(tag, []))} program)")
        with col_del:
            if st.button("❌", key=f"del_{tag}", help=f"{tag} eltávolítása"):
                st.session_state.csaladtagok.remove(tag)
                if tag in st.session_state.valasztott:
                    del st.session_state.valasztott[tag]
                save_selections()
                st.rerun()
                
    # Add new family member
    st.write("---")
    uj_tag = st.text_input("Új családtag hozzáadása:", placeholder="Például: Nagymama")
    if st.button("Hozzáadás", use_container_width=True):
        if uj_tag and uj_tag not in st.session_state.csaladtagok:
            st.session_state.csaladtagok.append(uj_tag)
            st.session_state.valasztott[uj_tag] = []
            save_selections()
            st.rerun()
            
    # --- SIMULATED TIME DETERMINATION ---
    import datetime
    current_dt = datetime.datetime.now()
    use_simulated_time = False
        
    # Scraping utility actions
    st.write("---")
    st.caption(f"Összes szinkronizált program: {len(st.session_state.programok)}")
    if st.button("🔄 Adatok újratöltése", help="Programok frissítése az élő honlapról és mentett tervek szinkronizálása"):
        # Clear the resource cache so _load_programs_once() runs again
        st.cache_resource.clear()
        # Force reload programs from GitHub/scraper on next run
        if 'programok' in st.session_state:
            del st.session_state.programok
        st.rerun()

# --- 8. TABS DEFINITION ---
tab_kereso, tab_naptar, tab_csalad, tab_elo, tab_terkep = st.tabs([
    "🔍 Program Kereső & Kínálat", 
    "📅 Személyes Naptárak", 
    "👨‍👩‍👧‍👦 Családi Összesített Menetrend",
    "⏱️ Élő Fesztiválkövető",
    "🗺️ Fesztivál Térkép"
])

# --- TAB 1: PROGRAMEXPLORER ---
with tab_kereso:
    st.subheader("Programok Böngészése")
    
    kivalasztott_tag = st.selectbox(
        "Ki számára választasz most programot?", 
        st.session_state.csaladtagok,
        key="active_planner"
    )
    
    utkozesek = ellenoriz_utkozeseket_reszletes(kivalasztott_tag)
    
    # Filter controls
    col_day, col_time = st.columns([1, 2])
    
    all_days = sorted(list(set(p["idopont"].split(" ")[0] for p in st.session_state.programok if p.get("idopont"))))
    day_options = ["Mind"] + all_days
    day_labels = {d: map_day_name(d + " 00:00") for d in all_days}
    day_labels["Mind"] = "Összes nap"
    
    all_locations = sorted(list(set(p["helyszin"] for p in st.session_state.programok if p.get("helyszin"))))
    
    all_tags = set()
    for p in st.session_state.programok:
        all_tags.update(p.get("cimkek", []))
    hashtag_options = [f"#{t}" for t in sorted(list(all_tags))]
    
    with col_day:
        selected_day = st.selectbox("📅 Fesztiválnap:", day_options, format_func=lambda x: day_labels.get(x, x))
    with col_time:
        selected_hours = st.slider(
            "🕒 Idősáv (kezdési óra):",
            min_value=0,
            max_value=24,
            value=(0, 24),
            step=1,
            help="Csak az ebben a tartományban kezdődő programok jelennek meg."
        )

    col_loc, col_tag, col_search = st.columns([1, 1, 2])
    with col_loc:
        selected_locations = st.multiselect("📍 Helyszínek:", all_locations, placeholder="Összes helyszín")
    with col_tag:
        selected_hashtags = st.multiselect("🏷️ Hashtagek:", hashtag_options, placeholder="Összes hashtag")
    with col_search:
        search_query = st.text_input("🔍 Keresés névben vagy leírásban:", placeholder="Keresett kifejezés...")

    # Filtering data
    szurt_programok = []
    for p in st.session_state.programok:
        # Day filter
        if selected_day != "Mind" and (not p["idopont"] or not p["idopont"].startswith(selected_day)):
            continue
            
        # Time filter (by hour of start time)
        if p["idopont"]:
            try:
                time_part = p["idopont"].split(" ")[1] # "15:30"
                hour = int(time_part.split(":")[0])
                if not (selected_hours[0] <= hour < selected_hours[1]):
                    continue
            except Exception:
                pass
                
        # Location filter
        if selected_locations and p["helyszin"] not in selected_locations:
            continue
            
        # Tag/Hashtag filter
        if selected_hashtags:
            # Strip '#' from selected hashtags for comparison
            requested_tags = [t[1:] for t in selected_hashtags]
            if not any(t in p.get("cimkek", []) for t in requested_tags):
                continue
                
        # Search query filter
        if search_query:
            query = search_query.lower()
            text_pool = f"{p['nev']} {p['leiras']} {' '.join(p.get('cimkek', []))}".lower()
            if query not in text_pool:
                continue
                
        szurt_programok.append(p)
        
    st.write(f"Találatok száma: **{len(szurt_programok)}** program")
    
    # Sort
    szurt_programok = sorted(szurt_programok, key=lambda x: x.get("idopont", ""))
    
    for p in szurt_programok:
        p_id = p["id"]
        be_van_jelolve = p_id in st.session_state.valasztott.get(kivalasztott_tag, [])
        van_utkozes = be_van_jelolve and p_id in utkozesek
        duration = st.session_state.custom_durations.get(f"{kivalasztott_tag}_{p_id}", p["tartam_perc"] or 60)
        
        with st.container():
            col_info, col_chk = st.columns([4, 1])
            with col_info:
                # Title
                st.markdown(f'<div class="program-title">{p["nev"]}</div>', unsafe_allow_html=True)
                
                # Badges row
                day_name = map_day_name(p["idopont"])
                time_only = p["idopont"][-5:] if p["idopont"] else "Időpont nélkül"
                loc_num = get_location_number(p["helyszin"])
                loc_display = f"{p['helyszin']} ({loc_num})" if loc_num else p['helyszin']
                
                badges_html = f"""
                <div class="badge-container">
                    <span class="badge badge-time">🕒 {day_name} {time_only}</span>
                    <span class="badge badge-location">📍 {loc_display}</span>
                    <span class="badge badge-duration">⏱️ {duration} perc</span>
                """
                for tag in p.get("cimkek", []):
                    badges_html += f'<span class="badge badge-tag">#{tag}</span>'
                badges_html += "</div>"
                
                col_badges, col_map = st.columns([5, 1])
                with col_badges:
                    st.markdown(badges_html, unsafe_allow_html=True)
                with col_map:
                    if loc_num:
                        if st.button("🗺️ Mutasd", key=f"map_btn_{p_id}_{kivalasztott_tag}_search", help="Helyszín megmutatása a térképen", use_container_width=True):
                            mutasd_terkepet(p["helyszin"], loc_num[1:])
                
                # Expandable description
                if p["leiras"]:
                    with st.expander("Részletes leírás megtekintése"):
                        full_desc_key = f"full_desc_{p_id}"
                        if full_desc_key not in st.session_state:
                            with st.spinner("Részletes leírás betöltése..."):
                                full_desc = scraper.scrape_full_description(p.get("urlpath", ""))
                                if not full_desc or "Hiba" in full_desc or "Nem sikerült" in full_desc:
                                    full_desc = p["leiras"]
                                st.session_state[full_desc_key] = full_desc
                        
                        # Show image if available and not a placeholder
                        kep = p.get("kep", "")
                        if kep and "placeholder_fest" not in kep:
                            st.image(kep, use_container_width=True)
                        st.write(st.session_state[full_desc_key])
                
                # Show conflict warning in red box
                if van_utkozes:
                    st.error(f"⚠️ **Átfedés van a következő programokkal:**  \n" + "  \n".join([f"- {u}" for u in utkozesek[p_id]]))
                    
            with col_chk:
                checkbox_key = f"chk_{kivalasztott_tag}_{p_id}"
                checked = st.checkbox("Érdekel", key=checkbox_key, value=be_van_jelolve)
                
                if checked and p_id not in st.session_state.valasztott[kivalasztott_tag]:
                    st.session_state.valasztott[kivalasztott_tag].append(p_id)
                    save_selections()
                    st.rerun()
                elif not checked and p_id in st.session_state.valasztott[kivalasztott_tag]:
                    st.session_state.valasztott[kivalasztott_tag].remove(p_id)
                    if f"{kivalasztott_tag}_{p_id}" in st.session_state.custom_durations:
                        del st.session_state.custom_durations[f"{kivalasztott_tag}_{p_id}"]
                    save_selections()
                    st.rerun()
                
                if checked:
                    # Slider to customize duration
                    dur_key = f"slider_{kivalasztott_tag}_{p_id}"
                    safe_duration = int(duration) if duration is not None else 60
                    custom_dur = st.number_input(
                        "Hossz (perc):", 
                        min_value=15, 
                        max_value=360, 
                        value=safe_duration,
                        step=15,
                        key=dur_key
                    )
                    if custom_dur != duration:
                        st.session_state.custom_durations[f"{kivalasztott_tag}_{p_id}"] = custom_dur
                        save_selections()
                        st.rerun()

# --- TAB 2: PERSONAL CALENDARS ---
with tab_naptar:
    st.subheader("Családtagok Egyéni Naptára")
    
    col_sel_member, col_export = st.columns([3, 2])
    with col_sel_member:
        naptar_tag = st.selectbox("Válassz családtagot a naptár megtekintéséhez:", st.session_state.csaladtagok, key="view_cal_member")
    
    valasztott_ids = st.session_state.valasztott.get(naptar_tag, [])
    
    if not valasztott_ids:
        st.info(f"{naptar_tag} naptára még üres. Jelölj be programokat az első fülön!")
    else:
        ics_data = generate_ics_data(naptar_tag)
        
        with col_export:
            st.write("") # Spacing
            st.write("")
            st.download_button(
                label=f"📥 {naptar_tag} naptárának letöltése (.ics)",
                data=ics_data,
                file_name=f"szelrozsa_2026_{naptar_tag}.ics",
                mime="text/calendar",
                use_container_width=True
            )
            
        st.write("---")
        
        naptar_progs = []
        for p_id in valasztott_ids:
            p = next((prog for prog in st.session_state.programok if prog["id"] == p_id), None)
            if p:
                naptar_progs.append(p)
                
        naptar_progs = sorted(naptar_progs, key=lambda x: x.get("idopont", ""))
        utkozesek = ellenoriz_utkozeseket_reszletes(naptar_tag)
        
        for p in naptar_progs:
            p_id = p["id"]
            van_utkozes = p_id in utkozesek
            duration = st.session_state.custom_durations.get(f"{naptar_tag}_{p_id}", p["tartam_perc"] or 60)
            
            try:
                kezdete = datetime.strptime(p["idopont"], "%Y-%m-%d %H:%M")
                vege = kezdete + pd.Timedelta(minutes=duration)
                idopont_megjeleno = f"{map_day_name(p['idopont'])} {kezdete.strftime('%H:%M')} - {vege.strftime('%H:%M')}"
            except Exception:
                idopont_megjeleno = f"{p['idopont']} (⏱️ {duration} perc)"
                
            with st.container():
                col_cinfo, col_crm = st.columns([4, 1])
                with col_cinfo:
                    st.markdown(f'<div class="program-title">{p["nev"]}</div>', unsafe_allow_html=True)
                    
                    loc_num = get_location_number(p["helyszin"])
                    loc_display = f"{p['helyszin']} ({loc_num})" if loc_num else p['helyszin']
                    
                    badges_html = f"""
                    <div class="badge-container">
                        <span class="badge badge-time">🕒 {idopont_megjeleno}</span>
                        <span class="badge badge-location">📍 {loc_display}</span>
                    </div>
                    """
                    
                    col_cbadges, col_cmap = st.columns([5, 1])
                    with col_cbadges:
                        st.markdown(badges_html, unsafe_allow_html=True)
                    with col_cmap:
                        if loc_num:
                            if st.button("🗺️ Mutasd", key=f"map_btn_{p_id}_{naptar_tag}_cal", help="Helyszín megmutatása a térképen", use_container_width=True):
                                mutasd_terkepet(p["helyszin"], loc_num[1:])
                    
                    if p["leiras"]:
                        with st.expander("Részletes leírás megtekintése"):
                            full_desc_key = f"full_desc_{p_id}"
                            if full_desc_key not in st.session_state:
                                with st.spinner("Részletes leírás betöltése..."):
                                    full_desc = scraper.scrape_full_description(p.get("urlpath", ""))
                                    if not full_desc or "Hiba" in full_desc or "Nem sikerült" in full_desc:
                                        full_desc = p["leiras"]
                                    st.session_state[full_desc_key] = full_desc
                            
                            # Show image if available and not a placeholder
                            kep = p.get("kep", "")
                            if kep and "placeholder_fest" not in kep:
                                st.image(kep, use_container_width=True)
                            st.write(st.session_state[full_desc_key])
                    
                    if van_utkozes:
                        st.error(f"⚠️ **Ütközés a következő naptárbejegyzésekkel:**  \n" + "  \n".join([f"- {u}" for u in utkozesek[p_id]]))
                        
                with col_crm:
                    if st.button("❌ Törlés", key=f"rm_{naptar_tag}_{p_id}", use_container_width=True):
                        st.session_state.valasztott[naptar_tag].remove(p_id)
                        if f"{naptar_tag}_{p_id}" in st.session_state.custom_durations:
                            del st.session_state.custom_durations[f"{naptar_tag}_{p_id}"]
                        save_selections()
                        st.rerun()

# --- TAB 3: FAMILY TIMELINE OVERVIEW ---
with tab_csalad:
    st.subheader("Családi Összesített Idővonal")
    st.write("Segít megnézni, hogy a családtagok hol vannak az egyes időpontokban, és hol vannak közös programok.")
    
    timeline_slots = {}
    
    for member in st.session_state.csaladtagok:
        for p_id in st.session_state.valasztott.get(member, []):
            p = next((prog for prog in st.session_state.programok if prog["id"] == p_id), None)
            if not p or not p["idopont"]:
                continue
                
            dt_str = p["idopont"]
            if dt_str not in timeline_slots:
                timeline_slots[dt_str] = {}
            if p_id not in timeline_slots[dt_str]:
                timeline_slots[dt_str][p_id] = {
                    "program": p,
                    "members": []
                }
            timeline_slots[dt_str][p_id]["members"].append(member)
            
    if not timeline_slots:
        st.info("A családtagok naptára még üres. Kezdjetek el programokat kiválasztani a keresőben!")
    else:
        sorted_slots = sorted(timeline_slots.keys())
        
        # Day segment selector
        family_days = sorted(list(set(d.split(" ")[0] for d in sorted_slots)))
        selected_family_day = st.segmented_control(
            "Idővonal szűrése nap szerint:", 
            options=["Mind"] + family_days, 
            format_func=lambda x: map_day_name(x + " 00:00") if x != "Mind" else "Összes nap",
            default="Mind"
        )
        
        for slot in sorted_slots:
            slot_day = slot.split(" ")[0]
            if selected_family_day != "Mind" and slot_day != selected_family_day:
                continue
                
            day_mapped = map_day_name(slot)
            time_formatted = slot[-5:]
            
            st.markdown(f'<div class="timeline-time">📅 {day_mapped} {time_formatted}</div>', unsafe_allow_html=True)
            
            for p_id, data in timeline_slots[slot].items():
                p = data["program"]
                members = data["members"]
                
                is_together = set(members) == set(st.session_state.csaladtagok)
                loc_num = get_location_number(p["helyszin"])
                loc_display = f"{p['helyszin']} (Térkép: {loc_num})" if loc_num else p['helyszin']
                
                if is_together:
                    col_tg_card, col_tg_map = st.columns([5, 1])
                    with col_tg_card:
                        st.markdown(f"""
                        <div class="family-together-card">
                            <strong>👨‍👩‍👧‍👦 KÖZÖS CSALÁDI PROGRAM: {p['nev']}</strong><br/>
                            📍 <em>Helyszín: {loc_display}</em><br/>
                            👥 Résztvevők: {", ".join(members)}
                        </div>
                        """, unsafe_allow_html=True)
                    with col_tg_map:
                        st.write("") # spacing
                        if loc_num:
                            if st.button("🗺️", key=f"map_btn_{p_id}_tg_timeline", help="Helyszín megmutatása a térképen", use_container_width=True):
                                mutasd_terkepet(p["helyszin"], loc_num[1:])
                else:
                    with st.container():
                        col_card_info, col_card_members = st.columns([3, 1])
                        with col_card_info:
                            st.markdown(f'<div class="program-title">{p["nev"]}</div>', unsafe_allow_html=True)
                            
                            col_cap, col_tmap = st.columns([5, 1])
                            with col_cap:
                                st.caption(f"📍 {loc_display} | 🏷️ {', '.join(p.get('cimkek', []))}")
                            with col_tmap:
                                if loc_num:
                                    if st.button("🗺️", key=f"map_btn_{p_id}_timeline", help="Helyszín megmutatása a térképen", use_container_width=True):
                                        mutasd_terkepet(p["helyszin"], loc_num[1:])
                        with col_card_members:
                            st.markdown("**Résztvevők:**")
                            for m in members:
                                st.markdown(f"- 👤 {m}")

# --- TAB 4: LIVE TRACKER ---
with tab_elo:
    st.subheader("⏱️ Élő Fesztiválkövető")
    
    festival_start_dt = datetime.datetime(2026, 7, 8, 17, 0)
    
    if not use_simulated_time and current_dt < festival_start_dt:
        st.write(f"Jelenlegi időpont: **{map_day_name(current_dt.strftime('%Y-%m-%d %H:%M'))} {current_dt.strftime('%H:%M')}**")
        
        # Show a beautiful countdown
        diff = festival_start_dt - current_dt
        days = diff.days
        hours, rem = divmod(diff.seconds, 3600)
        minutes, _ = divmod(rem, 60)
        
        st.info("### ⏳ A Szélrózsa találkozó hamarosan kezdődik!")
        st.write("A fesztivál első programja (Nyitó áhítat) **2026. július 8-án 17:00-kor** kezdődik.")
        
        # Display countdown cards
        st.markdown(f"""<div style="display: flex; gap: 15px; margin-top: 15px; margin-bottom: 20px;">
<div style="background-color: #0e76bc; color: white; padding: 15px; border-radius: 8px; text-align: center; flex: 1;">
    <div style="font-size: 2rem; font-weight: bold;">{days}</div>
    <div style="font-size: 0.8rem; text-transform: uppercase;">nap</div>
</div>
<div style="background-color: #0e76bc; color: white; padding: 15px; border-radius: 8px; text-align: center; flex: 1;">
    <div style="font-size: 2rem; font-weight: bold;">{hours}</div>
    <div style="font-size: 0.8rem; text-transform: uppercase;">óra</div>
</div>
<div style="background-color: #0e76bc; color: white; padding: 15px; border-radius: 8px; text-align: center; flex: 1;">
    <div style="font-size: 2rem; font-weight: bold;">{minutes}</div>
    <div style="font-size: 0.8rem; text-transform: uppercase;">perc</div>
</div>
</div>""", unsafe_allow_html=True)
        st.write("Az **Élő Fesztiválkövető** automatikusan bekapcsol és mutatja a futó programokat, amint elindul a találkozó!")
    else:
        st.write(f"Jelenlegi időpont: **{map_day_name(current_dt.strftime('%Y-%m-%d %H:%M'))} {current_dt.strftime('%H:%M')}**")
        
        # Calculate running programs
        fut_programok = []
        kovetkezo_programok = []
        
        for p in st.session_state.programok:
            if not p["idopont"]:
                continue
            try:
                p_start = datetime.datetime.strptime(p["idopont"], "%Y-%m-%d %H:%M")
                # Get customized or default duration
                duration = st.session_state.custom_durations.get(f"Anya_{p['id']}", p["tartam_perc"] or 60)
                p_end = p_start + datetime.timedelta(minutes=duration)
                
                if p_start <= current_dt <= p_end:
                    elapsed = (current_dt - p_start).total_seconds() / 60
                    remaining = (p_end - current_dt).total_seconds() / 60
                    progress = min(1.0, max(0.0, elapsed / duration))
                    fut_programok.append({
                        "program": p,
                        "start": p_start,
                        "end": p_end,
                        "duration": duration,
                        "elapsed": elapsed,
                        "remaining": remaining,
                        "progress": progress
                    })
                elif p_start > current_dt and (p_start - current_dt).total_seconds() / 60 <= 60:
                    starts_in = (p_start - current_dt).total_seconds() / 60
                    kovetkezo_programok.append({
                        "program": p,
                        "start": p_start,
                        "starts_in": starts_in
                    })
            except Exception:
                pass
                
        if not fut_programok:
            st.info("Jelenleg nem fut egyetlen program sem ezen az időponton. Válasz ki egy másik időpontot az Időszimulátorban a bal oldalon!")
        else:
            st.write("### 🟢 Éppen futó programok")
            
            # Group running programs by location
            grouped_running = {}
            for item in fut_programok:
                loc = item["program"]["helyszin"]
                if loc not in grouped_running:
                    grouped_running[loc] = []
                grouped_running[loc].append(item)
                
            active_locations = sorted(list(grouped_running.keys()))
            
            # Display columns
            cols = st.columns(min(3, len(active_locations)))
            for idx, loc in enumerate(active_locations):
                col_obj = cols[idx % len(cols)]
                with col_obj:
                    loc_num = get_location_number(loc)
                    loc_title = f"{loc} (Térkép: {loc_num})" if loc_num else loc
                    
                    st.markdown(f"""
                    <div style="background-color: #0e76bc10; border-left: 5px solid #0e76bc; padding: 8px 12px; border-radius: 6px; margin-bottom: 12px; margin-top: 10px;">
                        <h5 style="margin: 0; color: #0e76bc; font-weight: bold;">📍 {loc_title}</h5>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    for item in grouped_running[loc]:
                        p = item["program"]
                        
                        # Check selection status for family members
                        reszvevok = []
                        for member in st.session_state.csaladtagok:
                            if p["id"] in st.session_state.valasztott.get(member, []):
                                reszvevok.append(member)
                                
                        card_bg = "#ffffff"
                        border_color = "#e2e8f0"
                        if reszvevok:
                            card_bg = "#ecfdf5" # soft green for selected
                            border_color = "#10b981"
                            
                        st.markdown(f"""<div style="background-color: {card_bg}; border: 1px solid {border_color}; padding: 10px; border-radius: 6px; margin-bottom: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
<div style="font-weight: bold; font-size: 0.95rem; color: #0f172a;">{p['nev']}</div>
<div style="font-size: 0.8rem; color: #64748b; margin-top: 2px;">
    🕒 {item['start'].strftime('%H:%M')} - {item['end'].strftime('%H:%M')} ({int(item['duration'])} perc)
</div>
<div style="font-size: 0.8rem; color: #334155; margin-top: 4px; font-style: italic;">
    Lement: {int(item['elapsed'])} perc | Vissza van: {int(item['remaining'])} perc
</div>
</div>""", unsafe_allow_html=True)
                        
                        st.progress(item["progress"])
                        
                        if loc_num:
                            if st.button("🗺️ Térkép megnyitása", key=f"map_btn_{p['id']}_live", help="Helyszín megmutatása a térképen", use_container_width=True):
                                mutasd_terkepet(p["helyszin"], loc_num[1:])
                                
                        if reszvevok:
                            st.markdown(f"<div style='color: #047857; font-size: 0.75rem; margin-bottom: 12px; font-weight: 500;'>👥 Résztvevők: {', '.join(reszvevok)}</div>", unsafe_allow_html=True)
                            
        if kovetkezo_programok:
            st.write("---")
            st.write("### ⏳ A következő 60 percben kezdődő programok")
            
            kovetkezo_programok = sorted(kovetkezo_programok, key=lambda x: x["starts_in"])
            
            for item in kovetkezo_programok[:8]:
                p = item["program"]
                loc_num = get_location_number(p["helyszin"])
                loc_display = f"{p['helyszin']} (Térkép: {loc_num})" if loc_num else p['helyszin']
                
                reszvevok = []
                for member in st.session_state.csaladtagok:
                    if p["id"] in st.session_state.valasztott.get(member, []):
                        reszvevok.append(member)
                        
                badge_style = "background-color: #f1f5f9; color: #475569;"
                if reszvevok:
                    badge_style = "background-color: #d1fae5; color: #065f46; font-weight: bold;"
                    
                st.markdown(f"""<div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background-color: #ffffff; border-radius: 6px; margin-bottom: 6px; border: 1px solid #e2e8f0; box-shadow: 0 1px 2px rgba(0,0,0,0.01);">
<div>
    <strong style="color: #0f172a; font-size: 0.9rem;">{p['nev']}</strong><br/>
    <span style="font-size: 0.75rem; color: #64748b;">📍 {loc_display}</span>
</div>
<div style="text-align: right;">
    <span style="{badge_style} padding: 3px 6px; border-radius: 12px; font-size: 0.75rem; display: inline-block;">
        {int(item['starts_in'])} perc múlva ({item['start'].strftime('%H:%M')})
    </span>
    {"<br/><span style='font-size: 0.7rem; color: #047857; font-weight: 500;'>👥 " + ", ".join(reszvevok) + "</span>" if reszvevok else ""}
</div>
</div>""", unsafe_allow_html=True)

# --- TAB 5: FESTIVAL MAP ---
with tab_terkep:
    st.subheader("🗺️ Fesztivál Térkép & Helyszín Kódok")
    st.write("A 2026-os soproni Szélrózsa találkozó hivatalos helyszínrajza:")
    
    # Display map parts using absolute paths
    import os
    full_map_path = os.path.join(ROOT_PATH, "full_map.jpg")
    p1_path = os.path.join(ROOT_PATH, "map_part1.jpg")
    p2_path = os.path.join(ROOT_PATH, "map_part2.jpg")
    p3_path = os.path.join(ROOT_PATH, "map_part3.jpg")
    uploaded_path = os.path.join(ROOT_PATH, "uploaded_map.png")
    
    if os.path.exists(full_map_path):
        st.image(full_map_path, caption="Egyesített Szélrósa Helyszínrajz (kattints a nagyításhoz)", use_container_width=True)
    elif os.path.exists(p1_path) and os.path.exists(p2_path) and os.path.exists(p3_path):
        try:
            from PIL import Image
            img1 = Image.open(p1_path)
            img2 = Image.open(p2_path)
            img3 = Image.open(p3_path)
            combined_img = Image.new("RGB", (img1.width + img2.width + img3.width, img1.height))
            combined_img.paste(img1, (0, 0))
            combined_img.paste(img2, (img1.width, 0))
            combined_img.paste(img3, (img1.width + img2.width, 0))
            combined_img.save(full_map_path, "JPEG", quality=90)
            st.image(full_map_path, caption="Egyesített Szélrósa Helyszínrajz (kattints a nagyításhoz)", use_container_width=True)
        except Exception:
            # Fallback to separate columns if PIL fails
            col1, col2, col3 = st.columns(3)
            with col1:
                st.image(p1_path, caption="1. rész: Helyszínlista és P épület", use_container_width=True)
            with col2:
                st.image(p2_path, caption="2. rész: Erzsébet-kert (Középső terület)", use_container_width=True)
            with col3:
                st.image(p3_path, caption="3. rész: GYIK & Bánfalvi út", use_container_width=True)
    elif os.path.exists(uploaded_path):
        st.image(uploaded_path, caption="Feltöltött Szélrósa Helyszínrajz", use_container_width=True)
    else:
        st.info("Még nincs térkép kép elhelyezve a projektben.")
        
    # Option to upload custom map screenshot
    with st.expander("Saját térkép kép feltöltése/cseréje"):
        uploaded_file = st.file_uploader("Válassz egy képernyőképet (PNG, JPG, JPEG):", type=["png", "jpg", "jpeg"])
        if uploaded_file is not None:
            # Avoid infinite rerun loop
            file_key = f"uploaded_{uploaded_file.name}_{uploaded_file.size}"
            if file_key not in st.session_state:
                if save_uploaded_file(uploaded_file):
                    st.session_state[file_key] = True
                    st.success("Térkép sikeresen feltöltve és mentve! Az app frissülni fog.")
                    st.rerun()

    # Table of location numbers
    st.write("---")
    st.subheader("📍 Helyszínek és Térkép Számok")
    st.write("A programoknál megjelenő kódok az alábbi hivatalos térkép-számok alapján segítik a tájékozódást:")
    
    loc_table_data = []
    seen = set()
    for loc_name, num in sorted(LOCATION_NUMBERS.items(), key=lambda item: item[1]):
        if (loc_name, num) not in seen:
            loc_table_data.append({
                "Térkép Szám": f"#{num}",
                "Helyszín megnevezése": loc_name
            })
            seen.add((loc_name, num))
            
    df_loc = pd.DataFrame(loc_table_data)
    st.dataframe(df_loc, use_container_width=True, hide_index=True)
