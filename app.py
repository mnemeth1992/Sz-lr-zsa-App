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
@st.cache_data(show_spinner="Adatok szinkronizálása a Szélrózsa honlapjáról...", ttl=3600)
def get_scraped_programs():
    return scraper.scrape_programs()

# Force clear cache action helper
if 'clear_cache' in st.session_state and st.session_state.clear_cache:
    st.cache_data.clear()
    st.session_state.clear_cache = False

# --- 4. SESSION STATE INITIALIZATION ---
if 'programok' not in st.session_state:
    st.session_state.programok = get_scraped_programs()

# Fallback program list
if not st.session_state.programok:
    st.session_state.programok = [
        {"id": 1, "nev": "Nyitó áhítat (Szerverhiba esetén)", "idopont": "2026-07-08 17:00", "tartam_perc": 60, "helyszin": "Zajforrás", "cimkek": ["lelki alkalom"], "leiras": "Nem sikerült lekölteni az adatokat a szerverről."}
    ]

# Default family members list
if 'csaladtagok' not in st.session_state:
    st.session_state.csaladtagok = ["Anya", "Apa", "Gyerkőc 1", "Gyerkőc 2"]

# Selected program IDs
if 'valasztott' not in st.session_state:
    st.session_state.valasztott = {tag: [] for tag in st.session_state.csaladtagok}

# Custom durations overrides
if 'custom_durations' not in st.session_state:
    st.session_state.custom_durations = {}

# --- 5. HELPER FUNCTIONS ---

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
            duration = st.session_state.custom_durations.get(f"{tag}_{p_id}", p["tartam_perc"])
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
                duration = st.session_state.custom_durations.get(f"{tag}_{p_id}", p["tartam_perc"])
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
                st.rerun()
                
    # Add new family member
    st.write("---")
    uj_tag = st.text_input("Új családtag hozzáadása:", placeholder="Például: Nagymama")
    if st.button("Hozzáadás", use_container_width=True):
        if uj_tag and uj_tag not in st.session_state.csaladtagok:
            st.session_state.csaladtagok.append(uj_tag)
            st.session_state.valasztott[uj_tag] = []
            st.rerun()
            
    # Mobile Help Section
    st.write("---")
    with st.expander("📲 Futtatás Mobilon"):
        st.write("""
        Hogy a Szélrózsán minden családtag elérje a tervezőt a telefonján:
        
        **1. Streamlit Cloud (Ajánlott & Ingyenes)**
        Exponáld az appot publikus weboldalként:
        - Töltsd fel ezt a mappát **GitHubra**.
        - Nyisd meg a [share.streamlit.io](https://share.streamlit.io) oldalt és lépj be a GitHuboddal.
        - Kattints a **"Deploy an app"** gombra és válaszd ki a feltöltött repót.
        - Pár másodperc múlva kapsz egy linket, amit megoszthatsz a családdal mobilon!
        
        **2. Helyi Hotspot megosztás**
        Ha egy Wi-Fi hálózaton vagytok a fesztiválon (pl. egy telefonról megosztott hotspoton):
        - Futtasd az appot a gépeden.
        - A telefonod böngészőjében nyisd meg a géped IP-címét ezen a porton:
          `http://<GEP_IP_CIME>:8501`
        """)
        
    # Scraping utility actions
    st.write("---")
    st.caption(f"Összes szinkronizált program: {len(st.session_state.programok)}")
    if st.button("🔄 Adatok újratöltése", help="Programok frissítése az élő honlapról"):
        st.session_state.clear_cache = True
        st.session_state.programok = get_scraped_programs()
        st.rerun()

# --- 8. TABS DEFINITION ---
tab_kereso, tab_naptar, tab_csalad = st.tabs([
    "🔍 Program Kereső & Kínálat", 
    "📅 Személyes Naptárak", 
    "👨‍👩‍👧‍👦 Családi Összesített Menetrend"
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
    
    # Filter columns
    col_day, col_loc, col_tag, col_search = st.columns([1, 1, 1, 2])
    
    all_days = sorted(list(set(p["idopont"].split(" ")[0] for p in st.session_state.programok if p.get("idopont"))))
    day_options = ["Mind"] + all_days
    day_labels = {d: map_day_name(d + " 00:00") for d in all_days}
    day_labels["Mind"] = "Mindegyik nap"
    
    all_locations = sorted(list(set(p["helyszin"] for p in st.session_state.programok if p.get("helyszin"))))
    loc_options = ["Mind"] + all_locations
    
    all_tags = set()
    for p in st.session_state.programok:
        all_tags.update(p.get("cimkek", []))
    tag_options = ["Mind"] + sorted(list(all_tags))
    
    with col_day:
        selected_day = st.selectbox("Fesztiválnap:", day_options, format_func=lambda x: day_labels.get(x, x))
    with col_loc:
        selected_location = st.selectbox("Helyszín:", loc_options)
    with col_tag:
        selected_tag = st.selectbox("Kategória/Címke:", tag_options)
    with col_search:
        search_query = st.text_input("Keresés névben vagy leírásban:", placeholder="Keresett szó...")

    # Filtering data
    szurt_programok = []
    for p in st.session_state.programok:
        if selected_day != "Mind" and (not p["idopont"] or not p["idopont"].startswith(selected_day)):
            continue
        if selected_location != "Mind" and p["helyszin"] != selected_location:
            continue
        if selected_tag != "Mind" and selected_tag not in p.get("cimkek", []):
            continue
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
        duration = st.session_state.custom_durations.get(f"{kivalasztott_tag}_{p_id}", p["tartam_perc"])
        
        with st.container():
            col_info, col_chk = st.columns([4, 1])
            with col_info:
                # Title
                st.markdown(f'<div class="program-title">{p["nev"]}</div>', unsafe_allow_html=True)
                
                # Badges row
                day_name = map_day_name(p["idopont"])
                time_only = p["idopont"][-5:] if p["idopont"] else "Időpont nélkül"
                
                badges_html = f"""
                <div class="badge-container">
                    <span class="badge badge-time">🕒 {day_name} {time_only}</span>
                    <span class="badge badge-location">📍 {p['helyszin']}</span>
                    <span class="badge badge-duration">⏱️ {duration} perc</span>
                """
                for tag in p.get("cimkek", []):
                    badges_html += f'<span class="badge badge-tag">#{tag}</span>'
                badges_html += "</div>"
                
                st.markdown(badges_html, unsafe_allow_html=True)
                
                # Expandable description
                if p["leiras"]:
                    with st.expander("Részletes leírás megtekintése"):
                        st.write(p["leiras"])
                
                # Show conflict warning in red box
                if van_utkozes:
                    st.error(f"⚠️ **Átfedés van a következő programokkal:**  \n" + "  \n".join([f"- {u}" for u in utkozesek[p_id]]))
                    
            with col_chk:
                checkbox_key = f"chk_{kivalasztott_tag}_{p_id}"
                checked = st.checkbox("Érdekel", key=checkbox_key, value=be_van_jelolve)
                
                if checked and p_id not in st.session_state.valasztott[kivalasztott_tag]:
                    st.session_state.valasztott[kivalasztott_tag].append(p_id)
                    st.rerun()
                elif not checked and p_id in st.session_state.valasztott[kivalasztott_tag]:
                    st.session_state.valasztott[kivalasztott_tag].remove(p_id)
                    if f"{kivalasztott_tag}_{p_id}" in st.session_state.custom_durations:
                        del st.session_state.custom_durations[f"{kivalasztott_tag}_{p_id}"]
                    st.rerun()
                
                if checked:
                    # Slider to customize duration
                    dur_key = f"slider_{kivalasztott_tag}_{p_id}"
                    custom_dur = st.number_input(
                        "Hossz (perc):", 
                        min_value=15, 
                        max_value=360, 
                        value=int(duration),
                        step=15,
                        key=dur_key
                    )
                    if custom_dur != duration:
                        st.session_state.custom_durations[f"{kivalasztott_tag}_{p_id}"] = custom_dur
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
            duration = st.session_state.custom_durations.get(f"{naptar_tag}_{p_id}", p["tartam_perc"])
            
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
                    
                    badges_html = f"""
                    <div class="badge-container">
                        <span class="badge badge-time">🕒 {idopont_megjeleno}</span>
                        <span class="badge badge-location">📍 {p['helyszin']}</span>
                    </div>
                    """
                    st.markdown(badges_html, unsafe_allow_html=True)
                    
                    if p["leiras"]:
                        st.caption(p["leiras"][:180] + ("..." if len(p["leiras"]) > 180 else ""))
                    
                    if van_utkozes:
                        st.error(f"⚠️ **Ütközés a következő naptárbejegyzésekkel:**  \n" + "  \n".join([f"- {u}" for u in utkozesek[p_id]]))
                        
                with col_crm:
                    if st.button("❌ Törlés", key=f"rm_{naptar_tag}_{p_id}", use_container_width=True):
                        st.session_state.valasztott[naptar_tag].remove(p_id)
                        if f"{naptar_tag}_{p_id}" in st.session_state.custom_durations:
                            del st.session_state.custom_durations[f"{naptar_tag}_{p_id}"]
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
                
                if is_together:
                    # Highlight joint family program
                    st.markdown(f"""
                    <div class="family-together-card">
                        <strong>👨‍👩‍👧‍👦 KÖZÖS CSALÁDI PROGRAM: {p['nev']}</strong><br/>
                        📍 <em>Helyszín: {p['helyszin']}</em><br/>
                        👥 Résztvevők: {", ".join(members)}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    with st.container():
                        col_card_info, col_card_members = st.columns([3, 1])
                        with col_card_info:
                            st.markdown(f'<div class="program-title">{p["nev"]}</div>', unsafe_allow_html=True)
                            st.caption(f"📍 {p['helyszin']} | 🏷️ {', '.join(p.get('cimkek', []))}")
                        with col_card_members:
                            st.markdown("**Résztvevők:**")
                            for m in members:
                                st.markdown(f"- 👤 {m}")
