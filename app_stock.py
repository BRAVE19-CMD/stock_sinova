import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
import json
import os

st.set_page_config(page_title="STOCKS_SINOVA", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); }
    .stTabs [data-baseweb="tab-list"] { background: rgba(255,255,255,0.05); border-radius: 12px; padding: 5px; }
    .stTabs [data-baseweb="tab"] { color: #e0e0ff !important; font-weight: 600; font-size: 14px; }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; border-radius: 8px !important; color: #fff !important; }
    .stMetric { background: rgba(255,255,255,0.08); border-radius: 12px; padding: 15px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); }
    .stMetric label { color: #a5b4fc !important; font-weight: 500; }
    .stMetric [data-testid="stMetricValue"] { color: #fff !important; font-size: 1.8rem !important; font-weight: 700; }
    .stDataFrame { background: rgba(255,255,255,0.05); border-radius: 12px; color: #fff; }
    .stDataFrame table { color: #e0e0ff !important; }
    .stDataFrame th { background: rgba(99,102,241,0.3) !important; color: #fff !important; }
    .stDataFrame td { background: rgba(255,255,255,0.03) !important; color: #e0e0ff !important; }
    .stSelectbox label, .stMultiSelect label, .stRadio label, .stNumberInput label { color: #a5b4fc !important; font-weight: 500; }
    .stSelectbox div[data-baseweb="select"] { background: rgba(255,255,255,0.08); border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); color: #fff; }
    .stButton button { background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; color: #fff !important; border: none !important; border-radius: 10px !important; font-weight: 600 !important; padding: 10px 25px !important; transition: all 0.3s !important; }
    .stButton button:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(99,102,241,0.4) !important; }
    h1, h2, h3, .stSubheader { color: #f0f0ff !important; font-weight: 700; }
    .stSidebar { background: rgba(255,255,255,0.03) !important; }
    .stSidebar label { color: #a5b4fc !important; }
    .stSidebar .stSelectbox div[data-baseweb="select"] { background: rgba(255,255,255,0.08); border-radius: 8px; }
    .stExpander { background: rgba(255,255,255,0.05); border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); }
    .stExpander summary { color: #e0e0ff !important; font-weight: 600; }
    .stAlert { border-radius: 12px; color: #fff; }
    .stSuccess { background: rgba(34,197,94,0.2) !important; border: 1px solid rgba(34,197,94,0.3) !important; color: #86efac !important; }
    .stError { background: rgba(239,68,68,0.2) !important; border: 1px solid rgba(239,68,68,0.3) !important; color: #fca5a5 !important; }
    .stWarning { background: rgba(234,179,8,0.2) !important; border: 1px solid rgba(234,179,8,0.3) !important; color: #fde68a !important; }
    .stInfo { background: rgba(59,130,246,0.2) !important; border: 1px solid rgba(59,130,246,0.3) !important; color: #93c5fd !important; }
    div[data-testid="stDataFrame"] { border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; }
    .stCaption { color: rgba(255,255,255,0.5) !important; }
    p, li, span:not([class]) { color: #e0e0ff; }
    .stTextInput label, .stDateInput label { color: #a5b4fc !important; font-weight: 500; }
    .stTextInput input, .stDateInput input { background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; color: #fff; }
    .stNumberInput input { background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; color: #fff; }
    .stRadio div[role="radiogroup"] { background: rgba(255,255,255,0.05); border-radius: 8px; padding: 5px; }
    .stRadio div[role="radio"] { color: #e0e0ff !important; }
    .stCheckbox label { color: #e0e0ff !important; }
    .stDownloadButton button { background: linear-gradient(135deg, #10b981, #059669) !important; color: #fff !important; border: none !important; border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(BASE_DIR, "resultat_consolide.csv")
MAPPING_FILE = os.path.join(BASE_DIR, "designation_mapping.json")

def get_designation(ref):
    ref = str(ref)
    if ref.startswith('AR') or ref.startswith('TAC-') or ref.startswith('CL-') or ref.startswith('SACM-'):
        return 'AC'
    elif ref.startswith('WA') or ref.startswith('WW') or ref.startswith('WD') or ref.startswith('DW'):
        return 'WMM'
    elif any(ref.startswith(p) for p in ['UA', 'QA', '32', '43', '50', '55', '65', '75', '85', '98']):
        return 'TV'
    elif ref.startswith('RT') or ref.startswith('SR') or ref.startswith('RS') or ref.startswith('RL') or ref.startswith('RB') or ref.startswith('RR'):
        return 'REFF'
    elif ref.startswith('SK-WM') or ref.startswith('SKY'):
        return 'WM'
    elif ref.startswith('MS') or ref.startswith('SMC') or ref.startswith('SMWM') or ref.startswith('SMWS'):
        return 'PEM'
    elif any(ref.startswith(p) for p in ['C21', 'C5', 'C512', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8']):
        return 'CHF'
    elif any(ref.startswith(p) for p in ['SH', 'ST', 'SF', 'SLV', 'SBL', 'SBM', 'SBT', 'SBTP', 'SPT', 'SPTM']):
        return 'COO'
    elif ref.startswith('VC') or ref.startswith('VS'):
        return 'VC'
    elif ref.startswith('DB97'):
        return 'REF'
    else:
        return 'AUTRE'

def parse_two_row_header(filepath):
    df_h = pd.read_csv(filepath, sep=';', encoding='latin-1', header=None, nrows=2)
    n = len(df_h.columns)
    names = []
    for c in range(n):
        s = str(df_h.iloc[0, c]).strip()
        d = str(df_h.iloc[1, c]).strip()
        names.append(s if c < 2 else f"{s} / {d}")
    df = pd.read_csv(filepath, sep=';', encoding='latin-1', skiprows=2, header=None)
    df.columns = names
    for c in names[2:]:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
    return df, names

def consolidate_all():
    sources = {
        "extraction sinova.csv": {
            2: "PF_El_Eulma", 3: "Oued_Smar", 4: "Oued_Smar2", 5: "CBU",
            10: "UNITE AC_DECLASSER_A", 11: "UNITE AC_DECLASSER_B", 12: "UNITE AC_DECLASSER_C",
            18: "UNITE CHF_DECLASSER_A", 19: "UNITE CHF_DECLASSER_B", 20: "UNITE CHF_DECLASSER_C",
            25: "UNITE COO_DECLASSER_A", 30: "UNITE DW_DECLASSER_A", 33: "UNITE MWO_DECLASSER_A",
            40: "UNITE REF_DECLASSER_A", 41: "UNITE REF_DECLASSER_B", 42: "UNITE REF_DECLASSER_C",
            49: "UNITE TV_DECLASSER_A", 50: "UNITE TV_DECLASSER_B", 51: "UNITE TV_DECLASSER_C",
            58: "UNITE VC_DECLASSER_A", 60: "UNITE WM_DECLASSER_A",
            "usine": [14, 16, 22, 27, 32, 35, 37, 44, 54, 57, 59, 62],
            "export": [47, 65],
        },
        "extraction usine bisma.csv": {
            2: "Depot_PF_OUED_SMAR_Bisma", 3: "USINE_BISMA",
        },
        "extraction rdc sinova.csv": {
            2: "RDC_ALGER", 3: "RDC_ANNABA", 4: "RDC_EULMA", 5: "RDC_ORAN",
        },
        "extraction rdc bisma.csv": {
            2: "RDC_ALGER_BISMA", 4: "RDC_ANNABA_BISMA", 5: "RDC_EULMA_BISMA", 6: "RDC_ORAN_BISMA",
        },
    }
    parts = []
    for fname, mapping in sources.items():
        if not os.path.exists(fname):
            return False
        df_s, cols = parse_two_row_header(fname)
        prod_col = cols[0]
        indiv = {k: v for k, v in mapping.items() if isinstance(k, int)}
        usine_cols = mapping.get("usine", [])
        export_cols = mapping.get("export", [])
        max_col = len(cols) - 1
        indiv_valid = {i: v for i, v in indiv.items() if isinstance(i, int) and 0 <= i <= max_col}
        if not indiv_valid:
            pass  # Skip if no valid individual columns
        else:
            names_list = [cols[i] for i in sorted(indiv_valid.keys())]
            idx_map = {cols[i]: depot for i, depot in indiv_valid.items()}
            dm = df_s.melt(id_vars=[prod_col], value_vars=names_list, var_name='_col', value_name='Stock Final')
            dm['Dépôt'] = dm['_col'].map(idx_map)
            dm = dm.rename(columns={prod_col: 'Référence'})
            parts.append(dm[['Dépôt', 'Référence', 'Stock Final']])
        if usine_cols:
            unames = [cols[i] for i in usine_cols if 0 <= i <= max_col]
            if unames:
                du = df_s[[prod_col] + unames].copy()
                du['Stock Final'] = du[unames].sum(axis=1)
                du['Dépôt'] = 'Usine'
                du = du.rename(columns={prod_col: 'Référence'})
                parts.append(du[['Dépôt', 'Référence', 'Stock Final']])
        if export_cols:
            xnames = [cols[i] for i in export_cols if 0 <= i <= max_col]
            if xnames:
                dx = df_s[[prod_col] + xnames].copy()
                dx['Stock Final'] = dx[xnames].sum(axis=1)
                dx['Dépôt'] = 'EXPORT'
                dx = dx.rename(columns={prod_col: 'Référence'})
                parts.append(dx[['Dépôt', 'Référence', 'Stock Final']])
    all_df = pd.concat(parts, ignore_index=True)
    all_df['Stock Final'] = pd.to_numeric(all_df['Stock Final'], errors='coerce').fillna(0).astype(int)
    all_df[['Référence', 'Dépôt']] = all_df[['Référence', 'Dépôt']].astype(str).apply(lambda c: c.str.strip())

    ref_desig = {}
    if os.path.exists(CSV) and os.path.getsize(CSV) >= 100:
        try:
            old_csv = pd.read_csv(CSV, sep=';', encoding='utf-8-sig', skipinitialspace=True)
            old_csv.columns = old_csv.columns.str.strip()
            if 'Référence' in old_csv.columns and 'Désignation' in old_csv.columns:
                old_csv['Référence'] = old_csv['Référence'].astype(str).str.strip()
                old_csv['Désignation'] = old_csv['Désignation'].astype(str).str.strip()
                ref_desig = dict(zip(old_csv['Référence'], old_csv['Désignation']))
        except Exception:
            pass
    if os.path.exists(MAPPING_FILE):
        try:
            with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
                ref_desig.update(json.load(f))
        except Exception:
            pass

    all_df['Désignation'] = all_df['Référence'].map(ref_desig).fillna(all_df['Référence'].apply(get_designation))
    result = all_df[['Dépôt', 'Désignation', 'Référence', 'Stock Final']].sort_values(['Référence', 'Dépôt']).reset_index(drop=True)
    result.to_csv(CSV, sep=';', index=False, encoding='utf-8-sig')
    return True

@st.cache_data(ttl=600)
def load_data():
    if not os.path.exists(CSV) or os.path.getsize(CSV) < 100:
        consolidate_all()
    df = pd.read_csv(CSV, sep=';', encoding='utf-8-sig', skipinitialspace=True)
    df.columns = df.columns.str.strip()
    needed = ['Dépôt', 'Désignation', 'Référence', 'Stock Final']
    df = df[[c for c in needed if c in df.columns]]
    df = df.dropna(subset=['Dépôt', 'Désignation', 'Référence'])
    df = df[df['Désignation'] != 'AUTRE']
    for col in ['Dépôt', 'Désignation', 'Référence']:
        df[col] = df[col].astype(str).str.strip()
    for col in ['Stock Final', 'V MENSUELLE MOYENNE']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.replace(' ', '').replace('-', '0')
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    return df

df = load_data()

# Auto-refresh page toutes les 10 minutes
st.markdown('<meta http-equiv="refresh" content="600">', unsafe_allow_html=True)

depots = sorted(df['Dépôt'].unique())

st.sidebar.header("Filtres")

if st.sidebar.button("🔄 Rafraîchir les données"):
    st.cache_data.clear()
    st.rerun()

if st.sidebar.button("🔄 Forcer la consolidation"):
    if consolidate_all():
        st.cache_data.clear()
        st.success("✅ Consolidation terminée")
        st.rerun()
    else:
        st.error("❌ Fichiers sources manquants")

heure = pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")
st.sidebar.caption(f"Dernière mise à jour : {heure}")

st.sidebar.markdown("---")
show_saisie = False
is_admin = False
sidebar_option = st.sidebar.selectbox("🔒 Options", ["Masqué", "🔐 Saisie MP", "👑 Admin"])
if sidebar_option == "🔐 Saisie MP":
    mp_password = st.sidebar.text_input("Mot de passe Saisie MP", type="password")
    if mp_password == "sinova2024":
        st.sidebar.success("Accès autorisé")
        show_saisie = True
    elif mp_password:
        st.sidebar.error("Mot de passe incorrect")
elif sidebar_option == "👑 Admin":
    admin_email = st.sidebar.text_input("Email admin")
    admin_pass = st.sidebar.text_input("Mot de passe admin", type="password")
    if admin_email == "hamoudikzei@gmail.com" and admin_pass == "hamoudi80291":
        st.sidebar.success("✅ Mode Admin activé")
        is_admin = True
        show_saisie = True
    elif admin_email or admin_pass:
        st.sidebar.error("Identifiants incorrects")

depot_sel = st.sidebar.selectbox("📌 Dépôt", ["Tous"] + depots)

designations = sorted(df['Désignation'].unique())
des_sel = st.sidebar.selectbox("📦 Catégorie", ["Toutes"] + designations)
des_list = [] if des_sel == "Toutes" else [des_sel]

refs_dispo = sorted(df[df['Désignation'].isin(des_list)]['Référence'].unique()) if des_list else sorted(df['Référence'].unique())

if des_sel == "AC":
    io_filter = st.sidebar.selectbox("🌡️ Type", ["Toutes", "Indoor", "Outdoor"])
    refs_dispo_io = []
    for r in refs_dispo:
        rl = r.upper()
        if io_filter == "Indoor":
            if "-INDOOR" in rl or "-OUTDOOR" not in rl:
                refs_dispo_io.append(r)
        elif io_filter == "Outdoor":
            if "-OUTDOOR" in rl:
                refs_dispo_io.append(r)
        else:
            refs_dispo_io.append(r)
    ref_sel = st.sidebar.selectbox("🔖 Référence", ["Toutes"] + refs_dispo_io)
else:
    ref_sel = st.sidebar.selectbox("🔖 Référence", ["Toutes"] + refs_dispo)

stock_filter = st.sidebar.radio("📊 Stock", ["Tous", "En stock", "Rupture", "Faible", "Déclasser"])
if stock_filter == "Faible":
    seuil = st.sidebar.number_input("Seuil stock faible", min_value=1, value=5, step=1)

filtered = df.copy()
if depot_sel != "Tous":
    filtered = filtered[filtered['Dépôt'] == depot_sel]
if des_list:
    filtered = filtered[filtered['Désignation'].isin(des_list)]
if ref_sel != "Toutes":
    filtered = filtered[filtered['Référence'] == ref_sel]
if stock_filter == "En stock":
    filtered = filtered[filtered['Stock Final'] > 0]
elif stock_filter == "Rupture":
    filtered = filtered[filtered['Stock Final'] == 0]
elif stock_filter == "Faible":
    filtered = filtered[filtered['Stock Final'] < seuil]
elif stock_filter == "Déclasser":
    filtered = filtered[filtered['Dépôt'].str.contains('DECLASSER', case=False, na=False)]
    filtered = filtered[filtered['Stock Final'] > 0]

st.sidebar.markdown("---")
st.sidebar.markdown("##### 📑 Navigation")
nav_items = {
    "📋 Données": "📋 Données",
    "📍 Emplacement": "📍 Emplacement",
    "📈 Analyse": "📈 Analyse",
    "🧪 Matières Premières": "🧪 Matières Premières",
}
if show_saisie:
    nav_items["📝 Saisie MP"] = "📝 Saisie MP"
tab_sel = st.sidebar.radio("", list(nav_items.values()))

def color_row(row):
    styles = [''] * len(row)
    sf = row.get('Stock Final', 0)
    if sf == 0:
        styles[list(row.index).index('Stock Final')] = "background: #ffcccc; color: #000"
    return styles

# -------- TAB 1 : DONNEES --------
if tab_sel == "📋 Données":
    st.title("📊 Consolidation des Stocks")

    k1, k2, k3, k4 = st.columns(4)
    total_s = filtered['Stock Final'].sum()
    k1.metric("Stock Total", f"{total_s:,}")
    k2.metric("Lignes", f"{len(filtered):,}")
    k3.metric("Dépôts", filtered['Dépôt'].nunique())
    k4.metric("Produits", filtered['Référence'].nunique())

    styled = filtered.style.apply(color_row, axis=1)
    st.dataframe(styled, use_container_width=True, hide_index=True, height=800)

# -------- TAB 2 : EMPLACEMENT --------
if tab_sel == "📍 Emplacement":
    st.subheader("📍 Emplacement d'une Référence")
    ref_loc = st.selectbox("Sélectionnez une référence", [""] + sorted(df['Référence'].unique()), placeholder="Chercher...")
    if ref_loc:
        loc = df[df['Référence'] == ref_loc]
        total = loc['Stock Final'].sum()
        non_zero = loc[loc['Stock Final'] > 0]
        cols = st.columns(4)
        cols[0].metric("Stock Total", f"{total:,}")
        cols[1].metric("Dépôts avec stock", len(non_zero))
        cols[2].metric("Dépôts sans stock", len(loc[loc['Stock Final'] == 0]))
        cols[3].metric("Désignation", loc['Désignation'].iloc[0])

        # Carte des dépôts (barres horizontales)
        loc_sorted = loc.sort_values('Stock Final')
        fig = px.bar(loc_sorted, x='Stock Final', y='Dépôt', orientation='h',
                     color='Stock Final', color_continuous_scale='RdYlGn',
                     text_auto=True, title=f"Répartition de {ref_loc}")
        fig.update_layout(height=400, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig, use_container_width=True, key="empl_ref_loc")

        st.dataframe(loc.style.apply(color_row, axis=1),
                     use_container_width=True, hide_index=True)

# -------- TAB 3 : ANALYSE --------
if tab_sel == "📈 Analyse":
    st.title("📈 Analyse des Stocks")

    total_stock = df['Stock Final'].sum()
    total_prods = df['Référence'].nunique()
    total_depots = df['Dépôt'].nunique()
    prods_en_stock = df[df['Stock Final'] > 0]['Référence'].nunique()
    cols = st.columns(5)
    cols[0].metric("Stock Total", f"{total_stock:,}")
    cols[1].metric("Produits", f"{total_prods:,}")
    cols[2].metric("Dépôts", f"{total_depots}")
    cols[3].metric("Produits en stock", f"{prods_en_stock:,}")
    cols[4].metric("Stock moyen/dépôt", f"{total_stock // total_depots:,}")

    st.divider()

    # --- Stock par Catégorie ---
    st.subheader("📦 Stock par Catégorie")
    by_des = df.groupby('Désignation', as_index=False)['Stock Final'].sum()
    by_des = by_des.sort_values('Stock Final', ascending=False)
    fig = px.bar(by_des, x='Désignation', y='Stock Final', color='Désignation',
                 text_auto=True, color_discrete_sequence=px.colors.qualitative.Set2)
    fig.update_layout(showlegend=False, height=400)
    c1, c2 = st.columns([3, 1])
    c1.plotly_chart(fig, use_container_width=True, key="anl_cat_bar")
    c2.dataframe(by_des, use_container_width=True, hide_index=True)

    st.divider()

    # --- Stock par Dépôt ---
    st.subheader("🏢 Stock par Dépôt")
    by_dep = df.groupby('Dépôt', as_index=False)['Stock Final'].sum()
    by_dep = by_dep.sort_values('Stock Final', ascending=False)
    fig = px.bar(by_dep, x='Dépôt', y='Stock Final', color='Dépôt',
                 text_auto=True, color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_layout(showlegend=False, height=500, xaxis_tickangle=-45)
    c1, c2 = st.columns([3, 1])
    c1.plotly_chart(fig, use_container_width=True, key="anl_dep_bar")
    c2.dataframe(by_dep, use_container_width=True, hide_index=True)

    st.divider()

    # --- Répartition par Dépôt (détaillée) ---
    st.subheader("📍 Répartition détaillée par Dépôt")
    pivot = df.pivot_table(index='Dépôt', columns='Désignation', values='Stock Final',
                           aggfunc='sum', fill_value=0)
    pivot['Total Stock'] = pivot.sum(axis=1)
    pivot = pivot.sort_values('Total Stock', ascending=False)
    st.dataframe(pivot.astype(int), use_container_width=True)

    by_dep_des = df.groupby(['Dépôt', 'Désignation'], as_index=False)['Stock Final'].sum()
    fig = px.treemap(by_dep_des, path=['Dépôt', 'Désignation'], values='Stock Final',
                     color='Stock Final', color_continuous_scale='RdYlGn',
                     hover_data={'Stock Final': ':,'})
    fig.update_layout(height=500, margin=dict(l=5, r=5, t=5, b=5))
    st.plotly_chart(fig, use_container_width=True, key="anl_treemap")

    dep_metrics = df.groupby('Dépôt').agg(
        Produits=('Référence', 'nunique'),
        Stock_Total=('Stock Final', 'sum')
    ).sort_values('Stock_Total', ascending=False)
    dep_metrics['Moyen/Produit'] = (dep_metrics['Stock_Total'] / dep_metrics['Produits']).astype(int)
    st.dataframe(dep_metrics, use_container_width=True)

    st.divider()

    # --- Designation Pie (filtrable par dépôt) ---
    st.subheader("🥧 Répartition par Catégorie")
    pie_depot = st.selectbox("Filtrer par dépôt", ["Tous"] + depots, key="pie_depot")
    pie_data = df if pie_depot == "Tous" else df[df['Dépôt'] == pie_depot]
    pie_by_des = pie_data.groupby('Désignation', as_index=False)['Stock Final'].sum()
    fig = px.pie(pie_by_des, values='Stock Final', names='Désignation',
                 color_discrete_sequence=px.colors.qualitative.Set3, hole=0.3)
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True, key="anl_cat_pie")

    st.divider()

    # --- Top / Flop ---
    st.subheader("🏆 Top 10 Produits")
    top = df.groupby(['Référence', 'Désignation'], as_index=False)['Stock Final'].sum()
    top = top.sort_values('Stock Final', ascending=False).head(10)
    fig = px.bar(top, x='Stock Final', y='Référence', color='Désignation',
                 orientation='h', text_auto=True, color_discrete_sequence=px.colors.qualitative.Bold)
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True, key="anl_top10")

    st.subheader("📉 Flop 10 Produits (stock > 0)")
    flop = df.groupby(['Référence', 'Désignation'], as_index=False)['Stock Final'].sum()
    flop = flop[flop['Stock Final'] > 0].sort_values('Stock Final').head(10)
    fig = px.bar(flop, x='Stock Final', y='Référence', color='Désignation',
                 orientation='h', text_auto=True, color_discrete_sequence=px.colors.qualitative.Prism)
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True, key="anl_flop10")

    st.divider()

    # --- Stock Nul ---
    st.subheader("⚠️ Dépôts à Stock Nul par Catégorie")
    zero = df[df['Stock Final'] == 0].groupby(['Dépôt', 'Désignation']).size().reset_index(name='Produits à 0')
    fig = px.density_heatmap(zero, x='Dépôt', y='Désignation', z='Produits à 0',
                             color_continuous_scale='Reds', text_auto=True)
    fig.update_layout(height=500, xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True, key="anl_heatmap")
    with st.expander("Voir le tableau"):
        st.dataframe(zero, use_container_width=True, hide_index=True)

    st.divider()

    # --- Rapport Export ---
    st.subheader("📄 Exporter le Rapport")
    export_all = st.checkbox("Inclure toutes les données (pas seulement la sélection)")
    if st.button("📥 Générer le CSV"):
        out = df if export_all else filtered
        csv = out.to_csv(sep=';', index=False, encoding='utf-8-sig')
        st.download_button("Télécharger CSV", data=csv, file_name="rapport_stock.csv", mime="text/csv")

# -------- TAB 4 : MATIERES PREMIERES --------
MP_CSV = os.path.join(BASE_DIR, "kit+mtp.csv")

@st.cache_data(ttl=600)
def load_mp():
    try:
        m = pd.read_csv(MP_CSV, sep=';', encoding='utf-8-sig', low_memory=False)
        m = m.iloc[:, :9].copy()
        m.columns = ['Désignation', 'Référence', 'code article', 'UM', 'Stock initial', 'Réceptions', 'Production', 'Stock Final', 'SHORTAGE']
        m.columns = m.columns.str.strip()
        for col in m.select_dtypes('object').columns:
            m[col] = m[col].astype(str).str.strip().replace('nan', '').replace('None', '')
        for col in ['Stock initial', 'Réceptions', 'Production', 'Stock Final', 'SHORTAGE']:
            if col in m.columns:
                m[col] = m[col].astype(str).str.replace(' ', '', regex=False).str.replace('-', '0', regex=False)
                m[col] = pd.to_numeric(m[col], errors='coerce').fillna(0).astype(int)
        m.rename(columns={
            'Désignation': 'Catégorie',
            'Référence': 'Article',
            'code article': 'Code',
            'Stock initial': 'Stock Initial',
            'Réceptions': 'Entrées',
            'Production': 'Sorties',
            'SHORTAGE': 'Shortage'
        }, inplace=True)
        return m
    except Exception:
        return pd.DataFrame(columns=['Catégorie', 'Article', 'Code', 'UM', 'Stock Initial', 'Entrées', 'Sorties', 'Stock Final', 'Shortage'])
    

if tab_sel == "🧪 Matières Premières":
    st.title("🧪 Matières Premières - Rapport Détaillé")

    mp = load_mp()

    # Filters
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        mp_cat = st.selectbox("Catégorie", ["Toutes"] + sorted(mp['Catégorie'].unique()), key="mp_cat")
    with col_f2:
        mp_arts = sorted(mp['Article'].unique()) if mp_cat == "Toutes" else sorted(mp[mp['Catégorie'] == mp_cat]['Article'].unique())
        mp_art = st.selectbox("Article", ["Tous"] + mp_arts, key="mp_art")
    with col_f3:
        um_all = sorted([str(v) for v in mp['UM'].unique() if pd.notna(v)])
        mp_um = st.selectbox("Unité", ["Toutes"] + um_all, key="mp_um")

    mp_filtered = mp.copy()
    if mp_cat != "Toutes":
        mp_filtered = mp_filtered[mp_filtered['Catégorie'] == mp_cat]
    if mp_art != "Tous":
        mp_filtered = mp_filtered[mp_filtered['Article'] == mp_art]
    if mp_um != "Toutes":
        mp_filtered = mp_filtered[mp_filtered['UM'] == mp_um]

    # KPIs
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Stock Final", f"{mp_filtered['Stock Final'].sum():,}")
    k2.metric("Stock Initial", f"{mp_filtered['Stock Initial'].sum():,}")
    k3.metric("Entrées", f"{mp_filtered['Entrées'].sum():,}")
    k4.metric("Sorties", f"{mp_filtered['Sorties'].sum():,}")
    k5.metric("Shortage", f"{mp_filtered['Shortage'].sum():,}")

    st.dataframe(mp_filtered, use_container_width=True, hide_index=True)

    st.divider()

    # --- SECTION ANALYSE ---
    sub_tab1, sub_tab2, sub_tab3, sub_tab4, sub_tab5 = st.tabs(
        ["📊 Par Catégorie", "🏆 Top / Flop", "⛔ Shortage", "📈 Mouvements", "📄 Rapport Complet"]
    )

    with sub_tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Stock Final par Catégorie")
            by_cat = mp.groupby('Catégorie', as_index=False)['Stock Final'].sum()
            by_cat = by_cat.sort_values('Stock Final', ascending=False)
            fig = px.bar(by_cat, x='Stock Final', y='Catégorie', color='Catégorie',
                         orientation='h', text_auto=True, color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_layout(showlegend=False, height=450)
            st.plotly_chart(fig, use_container_width=True, key="mp_cat_bar")

        with c2:
            st.subheader("Répartition %")
            fig = px.pie(by_cat, values='Stock Final', names='Catégorie',
                         color_discrete_sequence=px.colors.qualitative.Set3, hole=0.4)
            fig.update_layout(height=450)
            st.plotly_chart(fig, use_container_width=True, key="mp_cat_pie")

        st.subheader("Détail par Catégorie")
        detail = mp.groupby(['Catégorie', 'UM'], as_index=False).agg(
            Articles=('Article', 'count'),
            Stock_Initial=('Stock Initial', 'sum'),
            Entrées=('Entrées', 'sum'),
            Sorties=('Sorties', 'sum'),
            Stock_Final=('Stock Final', 'sum'),
            Shortage=('Shortage', 'sum')
        ).sort_values('Stock_Final', ascending=False)
        detail.columns = ['Catégorie', 'UM', 'Nb Articles', 'Stock Initial', 'Entrées', 'Sorties', 'Stock Final', 'Shortage']
        st.dataframe(detail, use_container_width=True, hide_index=True)

    with sub_tab2:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🏆 Top 10 Plus Grand Stock")
            top = mp.groupby(['Article', 'Catégorie'], as_index=False)['Stock Final'].sum()
            top = top.sort_values('Stock Final', ascending=False).head(10)
            fig = px.bar(top, x='Stock Final', y='Article', color='Catégorie',
                         orientation='h', text_auto=True, color_discrete_sequence=px.colors.qualitative.Bold)
            fig.update_layout(height=450)
            st.plotly_chart(fig, use_container_width=True, key="mp_top10")

        with c2:
            st.subheader("📉 Top 10 Plus Petit Stock (>0)")
            flop = mp.groupby(['Article', 'Catégorie'], as_index=False)['Stock Final'].sum()
            flop = flop[flop['Stock Final'] > 0].sort_values('Stock Final').head(10)
            fig = px.bar(flop, x='Stock Final', y='Article', color='Catégorie',
                         orientation='h', text_auto=True, color_discrete_sequence=px.colors.qualitative.Prism)
            fig.update_layout(height=450)
            st.plotly_chart(fig, use_container_width=True, key="mp_flop10")

        st.subheader("📋 Articles avec Stock Nul")
        zero = mp[mp['Stock Final'] == 0][['Catégorie', 'Article', 'Code', 'UM']].copy()
        if len(zero) > 0:
            by_cat_zero = zero.groupby('Catégorie').size().reset_index(name='Nb Articles à 0')
            c1, c2 = st.columns([1, 2])
            c1.dataframe(by_cat_zero, use_container_width=True, hide_index=True)
            c2.dataframe(zero, use_container_width=True, hide_index=True)
        else:
            st.success("Aucun article à stock nul")

    with sub_tab3:
        st.subheader("⛔ Analyse des Shortages")

        sh = mp[mp['Shortage'] > 0][['Catégorie', 'Article', 'Code', 'UM', 'Stock Initial', 'Entrées', 'Sorties', 'Stock Final', 'Shortage']].copy()
        sh = sh.sort_values('Shortage', ascending=False)

        k1, k2, k3 = st.columns(3)
        k1.metric("Articles en Shortage", len(sh))
        k2.metric("Total Shortage", f"{sh['Shortage'].sum():,}")
        k3.metric("Stock Restant", f"{sh['Stock Final'].sum():,}")

        c1, c2 = st.columns(2)
        with c1:
            sh_cat = sh.groupby('Catégorie', as_index=False)['Shortage'].sum()
            fig = px.bar(sh_cat, x='Catégorie', y='Shortage', color='Catégorie',
                         text_auto=True, color_discrete_sequence=px.colors.qualitative.Set1)
            fig.update_layout(showlegend=False, height=350)
            st.plotly_chart(fig, use_container_width=True, key="mp_short_cat")
        with c2:
            fig = px.bar(sh.head(15), x='Shortage', y='Article', color='Shortage',
                         orientation='h', text_auto=True, color_continuous_scale='Reds')
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True, key="mp_short_top")

        with st.expander("Voir tous les shortages"):
            st.dataframe(sh, use_container_width=True, hide_index=True)

    with sub_tab4:
        st.subheader("📈 Analyse des Mouvements")

        mouvement = mp.groupby('Catégorie', as_index=False).agg(
            Stock_Initial=('Stock Initial', 'sum'),
            Entrées=('Entrées', 'sum'),
            Sorties=('Sorties', 'sum'),
            Stock_Final=('Stock Final', 'sum')
        ).sort_values('Stock_Final', ascending=False)

        fig = go.Figure()
        fig.add_trace(go.Bar(name='Stock Initial', x=mouvement['Catégorie'], y=mouvement['Stock_Initial']))
        fig.add_trace(go.Bar(name='Entrées', x=mouvement['Catégorie'], y=mouvement['Entrées']))
        fig.add_trace(go.Bar(name='Sorties', x=mouvement['Catégorie'], y=mouvement['Sorties']))
        fig.add_trace(go.Bar(name='Stock Final', x=mouvement['Catégorie'], y=mouvement['Stock_Final']))
        fig.update_layout(barmode='group', height=450)
        st.plotly_chart(fig, use_container_width=True, key="mp_mouvement")

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Top 10 Entrées")
            top_in = mp.groupby('Article', as_index=False)['Entrées'].sum()
            top_in = top_in[top_in['Entrées'] > 0].sort_values('Entrées', ascending=False).head(10)
            fig = px.bar(top_in, x='Entrées', y='Article', orientation='h',
                         text_auto=True, color='Entrées', color_continuous_scale='Greens')
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True, key="mp_top_in")
        with c2:
            st.subheader("Top 10 Sorties")
            top_out = mp.groupby('Article', as_index=False)['Sorties'].sum()
            top_out = top_out[top_out['Sorties'] > 0].sort_values('Sorties', ascending=False).head(10)
            fig = px.bar(top_out, x='Sorties', y='Article', orientation='h',
                         text_auto=True, color='Sorties', color_continuous_scale='Reds')
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True, key="mp_top_out")

        st.subheader("📊 Consommation Nette par Catégorie")
        conso = mp.groupby('Catégorie', as_index=False).agg(
            Stock_Initial=('Stock Initial', 'sum'),
            Entrées=('Entrées', 'sum'),
            Sorties=('Sorties', 'sum'),
            Stock_Final=('Stock Final', 'sum')
        )
        conso['Consommation'] = conso['Stock_Initial'] + conso['Entrées'] - conso['Sorties']
        conso['Écart'] = conso['Consommation'] - conso['Stock_Final']
        conso = conso.sort_values('Écart', ascending=False)
        st.dataframe(conso, use_container_width=True, hide_index=True)

    with sub_tab5:
        st.subheader("📄 Rapport Complet - Export")

        rapport = mp.groupby(['Catégorie', 'Article', 'Code', 'UM'], as_index=False).agg(
            Stock_Initial=('Stock Initial', 'sum'),
            Entrées=('Entrées', 'sum'),
            Sorties=('Sorties', 'sum'),
            Stock_Final=('Stock Final', 'sum'),
            Shortage=('Shortage', 'sum')
        ).sort_values(['Catégorie', 'Article'])

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Lignes", len(rapport))
        with col2:
            st.metric("Valeur Stock Final", f"{rapport['Stock_Final'].sum():,}")

        st.dataframe(rapport, use_container_width=True, hide_index=True)

        csv_full = rapport.to_csv(sep=';', index=False, encoding='utf-8-sig')
        st.download_button("📥 Télécharger le Rapport Complet CSV",
                          data=csv_full, file_name="rapport_matieres_premieres.csv", mime="text/csv")

        st.divider()
        st.subheader("📊 Résumé Exécutif")
        total_init = mp['Stock Initial'].sum()
        total_in = mp['Entrées'].sum()
        total_out = mp['Sorties'].sum()
        total_final = mp['Stock Final'].sum()
        total_sh = mp['Shortage'].sum()

        resume = pd.DataFrame({
            'Indicateur': ['Stock Initial Total', 'Total Entrées', 'Total Sorties',
                          'Stock Final Total', 'Shortage Total',
                          'Taux d\'écoulement (Sorties/Disponible)'],
            'Valeur': [f"{total_init:,}", f"{total_in:,}", f"{total_out:,}",
                      f"{total_final:,}", f"{total_sh:,}",
                      f"{total_out/(total_init+total_in)*100:.1f}%" if (total_init+total_in) > 0 else "N/A"]
        })
        st.dataframe(resume, use_container_width=True, hide_index=True)

# -------- TAB 5 : SAISIE MP --------
MP_KIT_CSV = os.path.join(BASE_DIR, "kit+mtp.csv")
MP_SAISIE_CSV = os.path.join(BASE_DIR, "saisie_mp.csv")

@st.cache_data
def load_mp_kit():
    k = pd.read_csv(MP_KIT_CSV, sep=';', encoding='utf-8-sig', low_memory=False)
    k = k.iloc[:, :9].copy()
    k.columns = k.columns.str.strip()
    for col in k.select_dtypes('object').columns:
        k[col] = k[col].astype(str).str.strip().replace('nan', '')
    for col in ['Stock initial', 'Réceptions', 'Production', 'Stock Final', 'SHORTAGE']:
        if col in k.columns:
            k[col] = k[col].astype(str).str.replace(' ', '', regex=False).str.replace('-', '0', regex=False)
            k[col] = pd.to_numeric(k[col], errors='coerce').fillna(0).astype(int)
    return k

def load_saisie_mp():
    if os.path.exists(MP_SAISIE_CSV):
        s = pd.read_csv(MP_SAISIE_CSV, sep=';', encoding='utf-8-sig')
    else:
        s = pd.DataFrame(columns=["Date", "Désignation", "Référence", "code article", "UM",
                                   "Stock initial", "Réceptions", "Production", "Stock Final", "SHORTAGE"])
    return s

def save_saisie_mp(df_s):
    df_s.to_csv(MP_SAISIE_CSV, sep=';', index=False, encoding='utf-8-sig')

def update_stock_in_csv(ref, add_receptions, add_production):
    try:
        df = pd.read_csv(MP_KIT_CSV, sep=';', encoding='utf-8-sig', low_memory=False)
        df.columns = df.columns.str.strip()
        
        mask = df['Référence'].astype(str).str.strip() == ref
        if mask.any():
            current_row = df.loc[mask].iloc[0]
            
            def parse_val(v):
                v = str(v).strip()
                if v in ['-', '', 'nan', 'None']:
                    return 0
                return int(v.replace(' ', '').replace('-', '0'))
            
            stock_init = parse_val(current_row['Stock initial'])
            current_receptions = parse_val(current_row['Réceptions'])
            current_production = parse_val(current_row['Production'])
            
            new_receptions = current_receptions + add_receptions
            new_production = current_production + add_production
            new_stock_final = stock_init + new_receptions - new_production
            
            df.loc[mask, 'Réceptions'] = new_receptions
            df.loc[mask, 'Production'] = new_production
            df.loc[mask, 'Stock Final'] = new_stock_final
            
            df.to_csv(MP_KIT_CSV, sep=';', index=False, encoding='utf-8-sig')
            return new_stock_final
        return None
    except Exception as e:
        st.error(f"Erreur mise à jour stock: {e}")
        return None

if tab_sel == "📝 Saisie MP":
    if not show_saisie:
        st.warning("🔒 Accès restreint. Entrez le mot de passe dans la barre latérale.")
    else:
        st.title("📝 Matières Premières - Formulaire de Saisie")

        mp_kit = load_mp_kit()
        df_mp_saisie = load_saisie_mp()
        
        st.caption(f"Fichier : {MP_KIT_CSV}")

        cats = sorted(mp_kit['Désignation'].unique())
        form_cat = st.selectbox("Désignation", cats, key="form_des")
        refs_cat = sorted(mp_kit[mp_kit['Désignation'] == form_cat]['Référence'].unique())
        form_ref = st.selectbox("Référence", [""] + refs_cat, key="form_ref")

        if form_ref:
            match = mp_kit[(mp_kit['Désignation'] == form_cat) & (mp_kit['Référence'] == form_ref)]
            if not match.empty:
                m = match.iloc[0]
                code_val = m['code article'] if str(m['code article']) not in ['nan', ''] else ""
                um_val = m['UM'] if str(m['UM']) not in ['nan', ''] else ""
                stk_init_val = int(m['Stock initial']) if str(m['Stock initial']) not in ['nan', ''] else 0
                rec_exist = int(m['Réceptions']) if str(m['Réceptions']) not in ['nan', ''] else 0
                prod_exist = int(m['Production']) if str(m['Production']) not in ['nan', ''] else 0
        else:
            code_val = ""
            um_val = ""
            stk_init_val = 0
            rec_exist = 0
            prod_exist = 0

        c1, c2 = st.columns(2)
        c1.text_input("Code Article", value=code_val, disabled=True)
        c2.text_input("UM", value=um_val, disabled=True)

        saisie_date = st.date_input("Date", value=datetime.date.today())
        sc1, sc2, sc3 = st.columns(3)
        stk_init = sc1.number_input("Stock initial", min_value=0, value=stk_init_val, step=1)
        receptions = sc2.number_input("Réceptions", min_value=0, value=0, step=1)
        production = sc3.number_input("Production", min_value=0, value=0, step=1)

        stk_final = stk_init_val + rec_exist + receptions - prod_exist - production
        st.metric("Stock Final après mise à jour", f"{stk_final:,}")

        if 'mp_msg' in st.session_state:
            st.success(st.session_state['mp_msg'])
            del st.session_state['mp_msg']

        if st.button("📤 Envoyer", type="primary", use_container_width=True):
                if not form_ref:
                    st.error("❌ Veuillez sélectionner une Référence.")
                else:
                    new_row = pd.DataFrame([[
                        str(saisie_date), form_cat, form_ref, code_val, um_val,
                        stk_init_val, receptions, production, stk_init_val + receptions - production, 0
                    ]], columns=df_mp_saisie.columns)
                    df_mp_saisie = pd.concat([df_mp_saisie, new_row], ignore_index=True)
                    save_saisie_mp(df_mp_saisie)
                    
                    new_stock = update_stock_in_csv(form_ref, receptions, production)
                    if new_stock is not None:
                        st.session_state['mp_msg'] = f"✅ Stock mis à jour : {form_ref}\nStock Final = {new_stock:,} (Entrées: +{receptions}, Sorties: -{production})"
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(f"❌ Article introuvable: {form_ref}")

        st.divider()

        st.subheader("📋 Dernières saisies MP")
        if len(df_mp_saisie) > 0:
            dern = df_mp_saisie.tail(20).reset_index(drop=True)
            st.dataframe(dern[::-1], use_container_width=True, hide_index=True)
            st.caption(f"Total : {len(df_mp_saisie)} saisies")
            if is_admin:
                st.markdown("---")
                c_edit, c_del = st.columns(2)
                with c_edit:
                    st.markdown("##### ✏️ Modifier (Admin)")
                    edit_idx = st.selectbox("Ligne à modifier", dern.index[::-1],
                        format_func=lambda i: f"#{len(dern)-i} - {dern.iloc[i]['Référence']} ({dern.iloc[i]['Date']})",
                        key="edit_idx")
                    edit_row = dern.loc[edit_idx]
                    new_recep = st.number_input("Nouvelles Réceptions", min_value=0, value=int(edit_row['Réceptions']), step=1, key="edit_recep")
                    new_prod = st.number_input("Nouvelle Production", min_value=0, value=int(edit_row['Production']), step=1, key="edit_prod")
                    if st.button("💾 Appliquer modification", type="primary"):
                        old_recep = int(edit_row['Réceptions'])
                        old_prod = int(edit_row['Production'])
                        diff_recep = new_recep - old_recep
                        diff_prod = new_prod - old_prod
                        global_idx = df_mp_saisie.tail(20).index[edit_idx]
                        df_mp_saisie.at[global_idx, 'Réceptions'] = new_recep
                        df_mp_saisie.at[global_idx, 'Production'] = new_prod
                        new_final = int(edit_row['Stock initial']) + new_recep - new_prod
                        df_mp_saisie.at[global_idx, 'Stock Final'] = new_final
                        save_saisie_mp(df_mp_saisie)
                        update_stock_in_csv(edit_row['Référence'], diff_recep, diff_prod)
                        st.cache_data.clear()
                        st.success(f"✅ {edit_row['Référence']} modifié")
                        st.rerun()
                with c_del:
                    st.markdown("##### 🗑️ Suppression (Admin)")
                    del_idx = st.selectbox("Ligne à supprimer", dern.index[::-1],
                        format_func=lambda i: f"#{len(dern)-i} - {dern.iloc[i]['Référence']} ({dern.iloc[i]['Date']})",
                        key="del_idx")
                    if st.button("🗑️ Supprimer cette saisie", type="secondary"):
                        df_mp_saisie = df_mp_saisie.drop(df_mp_saisie.tail(20).index[del_idx]).reset_index(drop=True)
                        save_saisie_mp(df_mp_saisie)
                        st.cache_data.clear()
                        st.success("✅ Ligne supprimée")
                        st.rerun()
        else:
            st.info("Aucune saisie pour le moment")

        col_e1, col_e2 = st.columns(2)
        with col_e1:
            csv_export = df_mp_saisie.to_csv(sep=';', index=False, encoding='utf-8-sig')
            st.download_button("📥 Télécharger CSV", data=csv_export,
                              file_name="saisie_mp.csv", mime="text/csv")
        with col_e2:
            if st.button("🔄 Réinitialiser", type="secondary"):
                if os.path.exists(MP_SAISIE_CSV):
                    os.remove(MP_SAISIE_CSV)
                st.rerun()
