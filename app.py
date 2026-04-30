"""
HCP Research Analytics Agent
ATU + PET Integrated Intelligence Dashboard
Glioma Manufacturer Research Platform
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import json
from datetime import datetime
import re
from pathlib import Path

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="HCP Intelligence Platform",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# STYLING
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

/* Root variables */
:root {
    --brand-red: #C8102E;
    --brand-dark: #0A0F1E;
    --brand-navy: #0D1B3E;
    --brand-slate: #1C2B4A;
    --accent-gold: #E8A838;
    --accent-teal: #00B4B4;
    --text-primary: #F0F4FF;
    --text-muted: #8898C8;
    --border: rgba(200,220,255,0.12);
    --card-bg: rgba(28, 43, 74, 0.6);
}

/* Global */
.stApp {
    background: var(--brand-dark);
    font-family: 'DM Sans', sans-serif;
}

/* Hide default streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display: none;}

/* Headers */
h1, h2, h3 { font-family: 'DM Serif Display', serif; }
h1 { color: var(--text-primary); }
h2 { color: var(--text-primary); font-size: 1.6rem; }
h3 { color: var(--accent-teal); font-size: 1.1rem; }

/* Sidebar */
.css-1d391kg, [data-testid="stSidebar"] {
    background: var(--brand-navy) !important;
    border-right: 1px solid var(--border);
}

/* Metric cards */
[data-testid="stMetric"] {
    background: var(--card-bg) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 16px !important;
    backdrop-filter: blur(10px);
}
[data-testid="stMetricLabel"] { color: var(--text-muted) !important; font-size: 0.78rem !important; letter-spacing: 0.08em; text-transform: uppercase; }
[data-testid="stMetricValue"] { color: var(--text-primary) !important; font-family: 'DM Serif Display', serif !important; }
[data-testid="stMetricDelta"] { font-size: 0.8rem !important; }

/* Dataframes */
[data-testid="stDataFrame"] { background: var(--card-bg) !important; border-radius: 8px; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { 
    background: var(--brand-navy) !important; 
    border-bottom: 1px solid var(--border);
    gap: 4px;
}
.stTabs [data-baseweb="tab"] { 
    color: var(--text-muted) !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.stTabs [aria-selected="true"] { 
    color: var(--accent-teal) !important;
    border-bottom: 2px solid var(--accent-teal) !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, var(--brand-red), #8B0A20) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em;
    transition: all 0.2s ease;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(200,16,46,0.4) !important;
}

/* Select boxes */
.stSelectbox > div > div { 
    background: var(--brand-slate) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
}

/* File uploader */
.stFileUploader > div {
    background: var(--card-bg) !important;
    border: 2px dashed var(--border) !important;
    border-radius: 12px !important;
}

/* Custom card */
.hcp-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    margin: 8px 0;
    backdrop-filter: blur(10px);
}

/* Hero banner */
.hero-banner {
    background: linear-gradient(135deg, var(--brand-navy) 0%, var(--brand-slate) 50%, rgba(200,16,46,0.15) 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 32px 40px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(0,180,180,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2.2rem;
    color: var(--text-primary);
    margin: 0;
    line-height: 1.2;
}
.hero-sub {
    color: var(--text-muted);
    font-size: 0.9rem;
    margin-top: 6px;
    letter-spacing: 0.04em;
}
.hero-badge {
    display: inline-block;
    background: rgba(200,16,46,0.2);
    border: 1px solid rgba(200,16,46,0.4);
    color: #FF6B7A;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 3px 10px;
    border-radius: 20px;
    margin-bottom: 12px;
}

/* Segment pill badges */
.seg-high { background: rgba(0,200,80,0.15); color: #00C850; border: 1px solid rgba(0,200,80,0.3); padding: 2px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 600; }
.seg-low { background: rgba(232,168,56,0.15); color: #E8A838; border: 1px solid rgba(232,168,56,0.3); padding: 2px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 600; }
.seg-non { background: rgba(136,152,200,0.15); color: #8898C8; border: 1px solid rgba(136,152,200,0.3); padding: 2px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 600; }

/* Insight callout */
.insight-box {
    background: linear-gradient(135deg, rgba(0,180,180,0.08), rgba(0,180,180,0.03));
    border-left: 3px solid var(--accent-teal);
    border-radius: 0 8px 8px 0;
    padding: 14px 18px;
    margin: 12px 0;
    color: var(--text-primary);
    font-size: 0.88rem;
}

/* Warning box */
.warn-box {
    background: rgba(232,168,56,0.1);
    border-left: 3px solid var(--accent-gold);
    border-radius: 0 8px 8px 0;
    padding: 14px 18px;
    margin: 12px 0;
    color: var(--text-primary);
    font-size: 0.88rem;
}

/* Section divider */
.section-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border), transparent);
    margin: 24px 0;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--brand-dark); }
::-webkit-scrollbar-thumb { background: var(--brand-slate); border-radius: 3px; }

/* Plotly backgrounds */
.js-plotly-plot .plotly .plot-container { background: transparent !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
QUARTER_ORDER = ["Q4'25", "Q1'26", "Q2'26"]
ATU_QUARTERS = ["Q1'26", "Q2'26"]
PET_QUARTERS = ["Q4'25", "Q1'26", "Q2'26"]

PLOTLY_TEMPLATE = dict(
    layout=dict(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#F0F4FF', family='DM Sans'),
        xaxis=dict(gridcolor='rgba(200,220,255,0.08)', showgrid=True),
        yaxis=dict(gridcolor='rgba(200,220,255,0.08)', showgrid=True),
        colorway=['#C8102E', '#00B4B4', '#E8A838', '#8B5CF6', '#4ADE80', '#FB923C'],
        # Note: margin is set per-chart to avoid duplicate keyword conflicts
    )
)

COLORS = {
    # Segment values as they appear AFTER brand masking (handled by _mask_df at load time)
    'High PRODUCT GLIOMA Usage': '#00C850',
    'High PRODUCT GLIOMA User': '#00C850',
    'Low PRODUCT GLIOMA Usage': '#E8A838',
    'Low PRODUCT GLIOMA User': '#E8A838',
    'Non PRODUCT GLIOMA User': '#8898C8',
    'Non PRODUCT GLIOMA Usage': '#8898C8',
    'On Target': '#C8102E',
    'Off target': '#8898C8',
    'Co-locs': '#E8A838',
    'Academic': '#00B4B4',
    'Community': '#C8102E',
    "Q4'25": '#8B5CF6',
    "Q1'26": '#00B4B4',
    "Q2'26": '#C8102E',
}


# ─────────────────────────────────────────────
# DATA LOADING ENGINE
# ─────────────────────────────────────────────
class DataEngine:
    """Autonomous data ingestion and matching engine."""

    def __init__(self):
        self.atu_df = None
        self.pet_df = None
        self.segment_hl = None
        self.segment_atu_pet = None
        self.segment_rep = None
        self.overlap_df = None
        self.errors = []

    # ── Brand masking ──────────────────────────────────────────────────────────
    # Applied at load-time to EVERY dataframe: column headers, string cell values,
    # and segment label values. Covers all spelling variants found in raw data.
    _BRAND_PATTERN = re.compile(
        r'\b('
        r'VORANIGO|Voranigo|voranigo|Voranigio|Vorangio|Voranigio|Voranigeo|'
        r'Voranigio|Voranqo|Vora\s+igo|Vora\s+nigo|Vorangel|Vorangni|'
        r'vorasidenib|Vorasidenib|VORASIDENIB|vorasdenib|Vorasedinib|'
        r'Vorasedenib|vorasedenib|Vorasedinib|Vorasidinib|Vorasindenib|'
        r'Vorasodenib|Vorasodenob|vorasenib|vorasindenib|vorasidinib|'
        r'vorasdenib|vorasedinib|VORASEDINEB|VORASIDENIB|vorasidinib|'
        r'vorasodenib|Vorasedineb|Vorasedinib|voradesnib|voradesnib|'
        r'Voradesnib|voradesniib|Vorasidiniib|Vorasidnib|voracitinib|'
        r'Voracitinib|voracetinib|Voracetinib|voracitinib|Voricitinib|'
        r'voricitinib|Voricidinib|Borcitinib|borcitinib|borosit|Borosinib|'
        r'Borisinib|Loracitinib|loracitinib|Vorcidinib|Florositinib|'
        r'Orasidinib|orasidinib|Varacetamab|Baracitinib|Baricitinib|'
        r'baricitinib|Vercitinib|voraninga|voraniga|Voraninga|VORA\b'
        r')',
        re.IGNORECASE,
    )
    _MASK = 'PRODUCT GLIOMA'

    # Separate pattern for company/manufacturer name masking
    _COMPANY_PATTERN = re.compile(
        r'\b(ServierONE|Servier\s*ONE|Servier|SERVIER|servier|Serv1er)\b',
        re.IGNORECASE,
    )
    _COMPANY_MASK = 'Glioma Manufacturer'

    @classmethod
    def _mask_brand_str(cls, text: str) -> str:
        """Replace brand names with PRODUCT GLIOMA and company names with Glioma Manufacturer."""
        if not isinstance(text, str):
            return text
        # First mask product brand names (Voranigo/vorasidenib variants → PRODUCT GLIOMA)
        text = cls._BRAND_PATTERN.sub(cls._MASK, text)
        # Then mask company/manufacturer names (Servier variants → Glioma Manufacturer)
        text = cls._COMPANY_PATTERN.sub(cls._COMPANY_MASK, text)
        return text

    @classmethod
    def _is_string_col(cls, series: pd.Series) -> bool:
        """Detect string columns safely across pandas 1.x / 2.x / 3.x.
        Pandas 3.x changed default string dtype from object to StringDtype,
        so checking dtype==object alone misses all string columns."""
        dtype = series.dtype
        # object dtype (pandas <3 default for strings)
        if dtype == object:
            return True
        # pandas StringDtype ('str', 'string', pd.StringDtype)
        dtype_str = str(dtype).lower()
        if dtype_str in ('str', 'string', 'large_string'):
            return True
        # Catch pd.api.types check as fallback
        try:
            return pd.api.types.is_string_dtype(dtype) and not pd.api.types.is_bool_dtype(dtype)
        except Exception:
            return False

    @classmethod
    def _mask_df(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Mask brand names everywhere in a DataFrame:
          1. Column headers (string replacement)
          2. All string-dtype columns — every cell value
        Handles both pandas <3 (object dtype) and pandas 3.x (StringDtype).
        Returns a copy with all brand references replaced.
        """
        if df is None:
            return df
        df = df.copy()

        # 1. Column names
        df.columns = [cls._mask_brand_str(str(c)) for c in df.columns]

        # 2. All string cell values — dtype-safe for pandas 3.x
        for col in df.columns:
            if cls._is_string_col(df[col]):
                df[col] = df[col].apply(
                    lambda v: cls._mask_brand_str(str(v)) if pd.notna(v) else v
                )
        return df
    # ──────────────────────────────────────────────────────────────────────────

    def _detect_header_row(self, file_obj, sheet=0):
        """Detect which row contains actual headers."""
        raw = pd.read_excel(file_obj, sheet_name=sheet, header=None, nrows=10)
        for i, row in raw.iterrows():
            vals = [str(v) for v in row if pd.notna(v)]
            if 'User Id' in vals or 'user id' in [v.lower() for v in vals]:
                return i
        return 0

    def _load_raw_file(self, file_obj, label="file"):
        """Load ATU or PET raw file with auto-detected header, then mask brand names."""
        try:
            header_row = self._detect_header_row(file_obj)
            # dtype=object ensures consistent string handling in pandas 2.x and 3.x
            df = pd.read_excel(file_obj, sheet_name=0, header=header_row, dtype=object)
            # Clean: drop rows with no User Id
            uid_col = next((c for c in df.columns if str(c).strip().lower() == 'user id'), None)
            if uid_col is None:
                uid_col = next((c for c in df.columns if 'user' in str(c).lower() and 'id' in str(c).lower()), None)
            if uid_col is None:
                self.errors.append(f"Could not find 'User Id' column in {label}")
                return None
            df = df.rename(columns={uid_col: 'User Id'})
            df = df.dropna(subset=['User Id'])
            df['User Id'] = pd.to_numeric(df['User Id'], errors='coerce')
            df = df.dropna(subset=['User Id'])
            df['User Id'] = df['User Id'].astype(float).astype(int)
            # Rename unnamed quarter and target columns if present
            for col in df.columns:
                if 'Unnamed' in str(col):
                    sample_vals = df[col].dropna().unique()[:5]
                    sample_str = [str(v) for v in sample_vals]
                    if any(q in s for s in sample_str for q in ["Q1", "Q2", "Q3", "Q4", "FY"]):
                        df = df.rename(columns={col: 'Quarter'})
                    elif any(t in s for s in sample_str for t in ["Target", "target", "Co-loc", "Prospect"]):
                        df = df.rename(columns={col: 'Target_Type'})
            # ── Apply brand masking to all string content ──
            df = self._mask_df(df)
            return df
        except Exception as e:
            self.errors.append(f"Error loading {label}: {e}")
            return None

    def _load_segment_file(self, file_obj, label="segment"):
        """Load a segment file (standard 7-column format), then mask brand names."""
        try:
            # Use dtype=object to ensure consistent string handling across pandas versions
            df = pd.read_excel(file_obj, sheet_name=0, dtype=object)
            df = df.dropna(subset=['User Id'])
            df['User Id'] = pd.to_numeric(df['User Id'], errors='coerce').astype('Int64').dropna()
            df = df.dropna(subset=['User Id'])
            df['User Id'] = df['User Id'].astype(int)
            # ── Apply brand masking to all string content ──
            df = self._mask_df(df)
            return df
        except Exception as e:
            self.errors.append(f"Error loading {label}: {e}")
            return None

    def load_from_paths(self, atu_path, pet_path, hl_path=None, atu_pet_path=None, rep_path=None):
        """Load from file paths (for default project files). None paths are skipped gracefully."""
        self.atu_df = self._load_raw_file(atu_path, "ATU")
        self.pet_df = self._load_raw_file(pet_path, "PET")
        if hl_path is not None:
            self.segment_hl = self._load_segment_file(hl_path, "High/Low/No User Segment")
        if atu_pet_path is not None:
            self.segment_atu_pet = self._load_segment_file(atu_pet_path, "ATU+PET Perception Segment")
        if rep_path is not None:
            self.segment_rep = self._load_segment_file(rep_path, "Rep Driven Attributes")
        self._build_overlap()

    def load_from_uploads(self, atu_file, pet_file, hl_file=None, atu_pet_file=None, rep_file=None):
        """Load from Streamlit uploaded files."""
        self.atu_df = self._load_raw_file(atu_file, "ATU")
        self.pet_df = self._load_raw_file(pet_file, "PET")
        if hl_file:
            self.segment_hl = self._load_segment_file(hl_file, "High/Low/No User Segment")
        if atu_pet_file:
            self.segment_atu_pet = self._load_segment_file(atu_pet_file, "ATU+PET Segment")
        if rep_file:
            self.segment_rep = self._load_segment_file(rep_file, "Rep Attributes")
        self._build_overlap()

    def _build_overlap(self):
        """Identify overlapping HCPs and build enriched overlap DataFrame."""
        if self.atu_df is None or self.pet_df is None:
            return

        atu_ids = set(self.atu_df['User Id'].unique())
        pet_ids = set(self.pet_df['User Id'].unique())
        overlap_ids = atu_ids & pet_ids

        if len(overlap_ids) == 0:
            self.errors.append("No overlapping HCPs found between ATU and PET datasets.")
            return

        # Build overlap base
        atu_sub = self.atu_df[self.atu_df['User Id'].isin(overlap_ids)].copy()
        pet_sub = self.pet_df[self.pet_df['User Id'].isin(overlap_ids)].copy()

        # ATU summary per HCP
        atu_agg = atu_sub.groupby('User Id').agg(
            ATU_Quarters=('Quarter', lambda x: ', '.join(sorted(x.dropna().unique())) if 'Quarter' in atu_sub.columns else 'N/A'),
            ATU_Responses=('User Id', 'count'),
            ATU_Target_Type=('Target_Type', lambda x: x.mode()[0] if 'Target_Type' in atu_sub.columns and not x.dropna().empty else 'N/A')
        ).reset_index() if 'Quarter' in atu_sub.columns else atu_sub[['User Id']].drop_duplicates().assign(ATU_Responses=1)

        # PET summary per HCP
        pet_agg = pet_sub.groupby('User Id').agg(
            PET_Quarters=('Quarter', lambda x: ', '.join(sorted(x.dropna().unique())) if 'Quarter' in pet_sub.columns else 'N/A'),
            PET_Responses=('User Id', 'count'),
            PET_Target_Type=('Target_Type', lambda x: x.mode()[0] if 'Target_Type' in pet_sub.columns and not x.dropna().empty else 'N/A')
        ).reset_index() if 'Quarter' in pet_sub.columns else pet_sub[['User Id']].drop_duplicates().assign(PET_Responses=1)

        # Merge ATU and PET summaries
        self.overlap_df = atu_agg.merge(pet_agg, on='User Id', how='outer')

        # Enrich with segment data
        if self.segment_hl is not None:
            seg_hl = self.segment_hl[self.segment_hl['User Id'].isin(overlap_ids)].copy()
            # Take the most recent wave segment per HCP
            if 'Wave Number' in seg_hl.columns:
                seg_hl['Wave_Num'] = seg_hl['Wave Number'].str.extract(r'(\d+)').astype(float)
                seg_hl_latest = seg_hl.sort_values('Wave_Num').groupby('User Id').last().reset_index()
                seg_hl_latest = seg_hl_latest[['User Id', 'Segment Value', 'Wave Number']].rename(
                    columns={'Segment Value': 'Glioma_Usage_Segment', 'Wave Number': 'Latest_Wave_HL'})
                self.overlap_df = self.overlap_df.merge(seg_hl_latest, on='User Id', how='left')

        if self.segment_atu_pet is not None:
            seg_ap = self.segment_atu_pet[self.segment_atu_pet['User Id'].isin(overlap_ids)].copy()
            if len(seg_ap) > 0:
                seg_ap_latest = seg_ap.groupby('User Id').last().reset_index()
                seg_ap_latest = seg_ap_latest[['User Id', 'Segment Value']].rename(
                    columns={'Segment Value': 'ATU_PET_Segment'})
                self.overlap_df = self.overlap_df.merge(seg_ap_latest, on='User Id', how='left')

        if self.segment_rep is not None:
            seg_rep = self.segment_rep[self.segment_rep['User Id'].isin(overlap_ids)].copy()
            if len(seg_rep) > 0:
                seg_rep_latest = seg_rep.groupby('User Id').last().reset_index()
                seg_rep_latest = seg_rep_latest[['User Id', 'Segment Value']].rename(
                    columns={'Segment Value': 'Rep_Interaction_Segment'})
                self.overlap_df = self.overlap_df.merge(seg_rep_latest, on='User Id', how='left')

        # ── Brand masking is applied at load time by _mask_df(); no further remap needed ──
        # Brand masking is applied at load time by _mask_df() via _BRAND_PATTERN,
        # so segment values already read as "PRODUCT GLIOMA" by this point.
        # No additional remapping needed here.

    def get_summary_stats(self):
        """Return key summary statistics."""
        if self.atu_df is None or self.pet_df is None:
            return {}

        atu_ids = set(self.atu_df['User Id'].unique())
        pet_ids = set(self.pet_df['User Id'].unique())
        overlap_ids = atu_ids & pet_ids

        stats = {
            'total_atu_hcps': len(atu_ids),
            'total_pet_hcps': len(pet_ids),
            'overlap_count': len(overlap_ids),
            'overlap_pct_atu': round(len(overlap_ids) / len(atu_ids) * 100, 1) if atu_ids else 0,
            'overlap_pct_pet': round(len(overlap_ids) / len(pet_ids) * 100, 1) if pet_ids else 0,
            'atu_quarters': sorted(self.atu_df['Quarter'].dropna().unique().tolist()) if 'Quarter' in self.atu_df.columns else [],
            'pet_quarters': sorted(self.pet_df['Quarter'].dropna().unique().tolist()) if 'Quarter' in self.pet_df.columns else [],
        }

        if self.overlap_df is not None and 'Glioma_Usage_Segment' in self.overlap_df.columns:
            seg_counts = self.overlap_df['Glioma_Usage_Segment'].value_counts().to_dict()
            # Sanitize any raw "Glioma" labels that slipped through
            _vr = {'High Glioma Usage': 'High Glioma Usage', 'Low Glioma Usage': 'Low Glioma Usage',
                   'Non Glioma User': 'Non Glioma User', 'High Glioma User': 'High Glioma User'}
            seg_counts = {_vr.get(k, k): v for k, v in seg_counts.items()}
            stats['glioma_segments'] = seg_counts

        return stats


# ─────────────────────────────────────────────
# QUESTION CLASSIFIER (Autonomous)
# ─────────────────────────────────────────────
class QuestionClassifier:
    """Autonomous question segmentation using content-driven pattern recognition."""

    SEGMENT_RULES = {
        'Screener & Eligibility': [
            r'board.certif', r'years.*practic', r'primary.*specialty', r'practice.*setting',
            r'percent.*time', r'primary.*decision', r'affiliated.*family', r'state.*practic',
            r'grade.*patient', r'tumor type', r'active.*management', r'qualify', r'eligible',
            r'IDH.*mutant.*patient', r'astrocytoma.*oligodendroglioma.*patient'
        ],
        'Molecular Testing & Diagnostics': [
            r'NGS', r'IHC', r'immunohistochemistry', r'next.generation.*sequenc',
            r'molecular.*test', r'IDH.*test', r'IDH.*status', r'IDH1.*IDH2',
            r'mutational.*status', r'biopsy.*resection.*test', r'reflex.*NGS',
            r'insurance.*test', r'BRAF', r'CDKN', r'EGFR', r'MGMT', r'1p.19q',
            r'test.*result', r'diagnostic', r'FDA.approved.*test'
        ],
        'Brand Awareness & Familiarity': [
            r'familiar.*treatment', r'aware.*treatment', r'come.*mind.*treat',
            r'Glioma', r'Glioma', r'Temodar', r'temozolomide', r'Tibsovo',
            r'ivosidenib', r'Rezlidhia', r'olutasidenib', r'bevacizumab', r'Avastin',
            r'heard.*product', r'familiar.*brand', r'NCCN.*update', r'v1.2025.*NCCN',
            r'PCV.*regimen', r'lomustine', r'carmustine'
        ],
        'Treatment Patterns & Usage': [
            r'current.*receiv', r'treatment.*decision', r'prescrib', r'next.*10.*patient',
            r'line.*therapy', r'adjuvant', r'maintenance', r'recurrent', r'progression',
            r'GTR', r'STR.*biopsy', r'first.*line', r'second.*line', r'newly.*diagnos',
            r'patient.*type.*influenc', r'grade 2.*IDH', r'currently.*treat',
            r'patient.*setting', r'treatment.*approach', r'patient.*profile'
        ],
        'Product Perception & Attributes': [
            r'rate.*attribute', r'performance.*attribute', r'perception.*product',
            r'prolonged.*PFS', r'progression.*free.*survival', r'overall.*survival',
            r'tumor.*volume', r'adverse.*event', r'hepatic.*toxic', r'hematolog',
            r'neurotox', r'hypermutation', r'LFT.*monitor', r'quality.*life',
            r'affordable', r'easy.*prescrib', r'route.*admin', r'fertility',
            r'seizure', r'long.term.*side', r'delay.*treatment', r'importance.*attribute',
            r'how.*would.*rate', r'adjuvant.*first.line.*treatment'
        ],
        'Access, Reimbursement & Support': [
            r'insurance', r'prior.*authoriz', r'coverage', r'copay', r'out.of.pocket',
            r'manufacturer.*support', r'patient.*support', r'bridge.*program', r'PAP',
            r'QuickStart', r'specialty.*pharmacy', r'dispens', r'reimburse',
            r'barrier.*prescrib', r'access.*issue', r'cost.*issue', r'letter.*medical',
            r'commercial.*co.pay', r'patient.*assist'
        ],
        'Rep Interaction & Promotion': [
            r'sales.*rep', r'manufacturer.*rep', r'recent.*interaction',
            r'discuss.*rep', r'visual.*aid', r'message.*recall', r'topic.*discuss',
            r'quality.*interaction', r'preparedness', r'knowledgeable',
            r'personal.*promotion', r'detail.*rep', r'call.*rep',
            r'channel.*receiv', r'non.personal', r'online.*ad',
            r'email.*manufacturer', r'conference', r'webinar', r'speaker.*program',
            r'motivating', r'believable', r'clear.*message'
        ],
        'Patient Behavior & Shared Decision': [
            r'patient.*ask', r'patient.*inquiry', r'patient.*prefer',
            r'patient.*conflict', r'shared.*decision', r'patient.*request',
            r'patient.*research', r'patient.*express', r'influence.*prescrib',
            r'patient.*online', r'support.*group'
        ],
        'MRI & Disease Monitoring': [
            r'MRI', r'monitoring.*practic', r'check.*progression',
            r'post.resection', r'follow.up.*scan', r'imaging.*frequenc',
            r'monitoring.*evolv', r'disease.*monitor'
        ],
        'Disease State Education': [
            r'glioma.*common', r'IDH.mutant.*wildtype', r'prognosis.*IDH',
            r'WHO.*classification', r'oligodendroglioma.*astrocytoma.*prognos',
            r'molecular.*workup', r'IDH.*testing.*initial', r'DSE',
            r'disease.*state.*education', r'WHO.*CNS.*2021', r'tumor.*classif'
        ],
        'Sources of Information': [
            r'source.*information', r'where.*seen.*heard', r'preferred.*source',
            r'journal.*publication', r'conference.*symposium', r'CME',
            r'colleague.*practice', r'manufacturer.*website', r'social.*media',
            r'NCCN.*recommendation', r'UpToDate', r'professional.*app',
            r'oncology.*societ', r'email.*society', r'SNO', r'ASCO'
        ],
        'HCP Profiling & Demographics': [
            r'physicians.*practice', r'practice.*location', r'urban.*suburban.*rural',
            r'insurance.*patient.*population', r'GPO', r'OCM', r'IDN.*health',
            r'ACO', r'out.patient.*pharmacy', r'clinical.*trial.*involv',
            r'tumor.*board', r'multidisciplinary', r'fellowship.*training',
            r'years.*practice.*post.residency', r'primary.*specialty.*profil'
        ],
    }

    @classmethod
    def classify(cls, question_text: str):
        """Classify a single question. Returns (segment, confidence, matched_rules)."""
        if not question_text or not isinstance(question_text, str):
            return 'Uncategorized', 0.0, []

        text_lower = question_text.lower()
        scores = {}
        matched = {}

        for segment, patterns in cls.SEGMENT_RULES.items():
            hits = []
            for p in patterns:
                if re.search(p, text_lower, re.IGNORECASE):
                    hits.append(p)
            if hits:
                scores[segment] = len(hits)
                matched[segment] = hits

        if not scores:
            return 'Uncategorized', 0.0, []

        best_seg = max(scores, key=scores.get)
        total_hits = sum(scores.values())
        confidence = min(scores[best_seg] / max(total_hits, 1) * 1.5, 1.0)

        # Boost confidence if clear winner
        if scores[best_seg] >= 2:
            confidence = min(confidence + 0.2, 1.0)

        return best_seg, round(confidence, 2), matched[best_seg]

    @classmethod
    def classify_batch(cls, questions: list):
        """Classify a list of questions."""
        results = []
        for q in questions:
            seg, conf, rules = cls.classify(str(q))
            results.append({
                'Question': q,
                'Segment': seg,
                'Confidence': conf,
                'Matched_Patterns': ', '.join(rules[:3]),
            })
        return pd.DataFrame(results)


# ─────────────────────────────────────────────
# CHART HELPERS
# ─────────────────────────────────────────────
def make_donut(values, labels, title, colors_map=None):
    colors = [colors_map.get(l, '#8898C8') for l in labels] if colors_map else None
    fig = go.Figure(go.Pie(
        values=values, labels=labels,
        hole=0.6,
        textinfo='percent+label',
        textfont=dict(size=11),
        marker=dict(colors=colors, line=dict(color='#0A0F1E', width=2)),
    ))
    fig.update_layout(
        **PLOTLY_TEMPLATE['layout'],
        title=dict(text=title, font=dict(size=13, color='#F0F4FF'), x=0.5),
        showlegend=False,
        height=280,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig

def make_bar(df, x, y, title, color_col=None, colors_map=None, orientation='v'):
    if color_col and colors_map:
        color_seq = [colors_map.get(v, '#8898C8') for v in df[color_col]]
    else:
        color_seq = ['#00B4B4'] * len(df)

    if orientation == 'h':
        fig = go.Figure(go.Bar(
            x=df[y], y=df[x], orientation='h',
            marker_color=color_seq,
            text=df[y],
            textposition='outside',
            textfont=dict(size=10),
        ))
    else:
        fig = go.Figure(go.Bar(
            x=df[x], y=df[y],
            marker_color=color_seq,
            text=df[y],
            textposition='outside',
            textfont=dict(size=10),
        ))

    fig.update_layout(
        **PLOTLY_TEMPLATE['layout'],
        title=dict(text=title, font=dict(size=13, color='#F0F4FF'), x=0),
        height=300,
    )
    return fig

def make_heatmap(df_pivot, title):
    fig = go.Figure(go.Heatmap(
        z=df_pivot.values,
        x=df_pivot.columns.tolist(),
        y=df_pivot.index.tolist(),
        colorscale=[[0, '#0D1B3E'], [0.5, '#C8102E'], [1, '#FF6B7A']],
        text=df_pivot.values,
        texttemplate='%{text}',
        textfont=dict(size=11),
        showscale=True,
    ))
    fig.update_layout(
        **PLOTLY_TEMPLATE['layout'],
        title=dict(text=title, font=dict(size=13, color='#F0F4FF'), x=0),
        height=350,
    )
    return fig


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
def render_sidebar():
    # Use st.sidebar.xxx directly — avoids `with st.sidebar:` context manager
    # issues on certain Streamlit Cloud versions.
    sb = st.sidebar

    sb.markdown("""
    <div style='padding: 16px 0 8px; text-align: center;'>
        <div style='font-family: DM Serif Display, serif; font-size: 1.3rem; color: #F0F4FF;'>🧬 HCP Intel</div>
        <div style='color: #8898C8; font-size: 0.7rem; letter-spacing: 0.1em; text-transform: uppercase; margin-top: 4px;'>Research Analytics Platform</div>
    </div>
    """, unsafe_allow_html=True)
    sb.markdown("---")

    sb.markdown("### 📁 Data Sources")
    data_mode = sb.radio(
        "Source", ["Use Project Files", "Upload Custom Files"],
        label_visibility="collapsed"
    )

    uploaded = {}
    if data_mode == "Upload Custom Files":
        sb.markdown("**ATU Raw File** (2 quarters)")
        uploaded['atu'] = sb.file_uploader("ATU", type=['xlsx', 'csv'], label_visibility="collapsed")
        sb.markdown("**PET Raw File** (3 quarters)")
        uploaded['pet'] = sb.file_uploader("PET", type=['xlsx', 'csv'], label_visibility="collapsed")
        sb.markdown("**Segment: High/Low/No User** *(optional)*")
        uploaded['hl'] = sb.file_uploader("HL Segment", type=['xlsx'], label_visibility="collapsed")
        sb.markdown("**Segment: ATU+PET Perception** *(optional)*")
        uploaded['atu_pet'] = sb.file_uploader("ATU PET Segment", type=['xlsx'], label_visibility="collapsed")
        sb.markdown("**Segment: Rep Attributes** *(optional)*")
        uploaded['rep'] = sb.file_uploader("Rep Segment", type=['xlsx'], label_visibility="collapsed")

    sb.markdown("---")
    sb.markdown("### 🔬 Analysis Focus")
    analysis_view = sb.selectbox(
        "Primary View",
        ["Executive Overview", "HCP Overlap Analysis", "Segment Intelligence",
         "Question Classifier", "Temporal Trends", "Raw Data Explorer"],
        label_visibility="collapsed"
    )

    sb.markdown("---")
    sb.markdown("""
    <div style='color: #8898C8; font-size: 0.7rem; padding: 8px 0;'>
    <b style='color: #F0F4FF;'>Glioma Program</b><br>
    Glioma Manufacturer Internal Analytics<br>
    FY26 Q1-Q2 Integrated Research
    </div>
    """, unsafe_allow_html=True)

    return data_mode, uploaded, analysis_view


# ─────────────────────────────────────────────
# VIEWS
# ─────────────────────────────────────────────
def view_executive_overview(engine: DataEngine):
    stats = engine.get_summary_stats()
    if not stats:
        st.warning("No data loaded. Please ensure files are available.")
        return

    st.markdown("""
    <div class='hero-banner'>
        <div class='hero-badge'>Glioma® Program · FY26</div>
        <div class='hero-title'>ATU & PET Integrated Intelligence</div>
        <div class='hero-sub'>Cross-dataset HCP analysis across 3 PET quarters × 2 ATU quarters</div>
    </div>
    """, unsafe_allow_html=True)

    # KPI row
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("ATU Unique HCPs", stats['total_atu_hcps'],
                  f"{', '.join(stats['atu_quarters'])}")
    with c2:
        st.metric("PET Unique HCPs", stats['total_pet_hcps'],
                  f"{', '.join(stats['pet_quarters'])}")
    with c3:
        st.metric("Overlapping HCPs", stats['overlap_count'],
                  f"+{stats['overlap_pct_atu']}% of ATU")
    with c4:
        st.metric("ATU Coverage", f"{stats['overlap_pct_atu']}%",
                  "Matched in PET")
    with c5:
        st.metric("PET Coverage", f"{stats['overlap_pct_pet']}%",
                  "Matched in ATU")

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.markdown("### Overlap Coverage Map")
        # Venn-style bar
        fig = go.Figure()
        categories = ['ATU Only', 'Both ATU & PET', 'PET Only']
        atu_only = stats['total_atu_hcps'] - stats['overlap_count']
        pet_only = stats['total_pet_hcps'] - stats['overlap_count']
        values = [atu_only, stats['overlap_count'], pet_only]
        bar_colors = ['#8898C8', '#C8102E', '#00B4B4']

        fig.add_trace(go.Bar(
            x=categories, y=values,
            marker_color=bar_colors,
            text=values, textposition='outside',
            textfont=dict(size=13, color='#F0F4FF'),
        ))
        fig.update_layout(
            **PLOTLY_TEMPLATE['layout'],
            height=300,
            title=dict(text='HCP Distribution Across Datasets', font=dict(size=13, color='#F0F4FF')),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Quarterly breakdown if available
        if engine.atu_df is not None and 'Quarter' in engine.atu_df.columns:
            st.markdown("### Quarter-Level Distribution")
            atu_q = engine.atu_df.groupby('Quarter')['User Id'].nunique().reset_index(name='ATU HCPs')
            pet_q = engine.pet_df.groupby('Quarter')['User Id'].nunique().reset_index(name='PET HCPs') if 'Quarter' in engine.pet_df.columns else pd.DataFrame()

            all_q = pd.DataFrame({'Quarter': QUARTER_ORDER})
            if len(atu_q):
                all_q = all_q.merge(atu_q, on='Quarter', how='left')
            if len(pet_q):
                all_q = all_q.merge(pet_q, on='Quarter', how='left')
            all_q = all_q.fillna(0)

            fig2 = go.Figure()
            if 'ATU HCPs' in all_q.columns:
                fig2.add_trace(go.Bar(name='ATU', x=all_q['Quarter'], y=all_q['ATU HCPs'],
                                      marker_color='#C8102E', text=all_q['ATU HCPs'].astype(int), textposition='outside'))
            if 'PET HCPs' in all_q.columns:
                fig2.add_trace(go.Bar(name='PET', x=all_q['Quarter'], y=all_q['PET HCPs'],
                                      marker_color='#00B4B4', text=all_q['PET HCPs'].astype(int), textposition='outside'))
            fig2.update_layout(**PLOTLY_TEMPLATE['layout'], barmode='group', height=280,
                               title=dict(text='HCPs per Quarter by Dataset', font=dict(size=13, color='#F0F4FF')))
            st.plotly_chart(fig2, use_container_width=True)

    with col_right:
        # Glioma Usage Segments
        if 'glioma_segments' in stats and stats['glioma_segments']:
            seg_labels = list(stats['glioma_segments'].keys())
            seg_vals = list(stats['glioma_segments'].values())
            fig_seg = make_donut(seg_vals, seg_labels, 'Glioma Usage Segments<br>(Overlapping HCPs)', COLORS)
            st.plotly_chart(fig_seg, use_container_width=True)

        # Target type donut
        if engine.atu_df is not None and 'Target_Type' in engine.atu_df.columns:
            tt = engine.atu_df.dropna(subset=['Target_Type'])['Target_Type'].value_counts()
            fig_tt = make_donut(tt.values.tolist(), tt.index.tolist(), 'ATU Target Type Split', COLORS)
            st.plotly_chart(fig_tt, use_container_width=True)

        # Key insight
        overlap_pct = stats['overlap_pct_atu']
        insight_txt = (
            f"<b>{stats['overlap_count']} HCPs</b> appear in both ATU and PET datasets, "
            f"representing <b>{overlap_pct}%</b> of ATU respondents. "
            f"This overlap enables direct correlation of promotional exposure (PET) "
            f"with awareness, attitude, and usage behaviors (ATU)."
        )
        st.markdown(f"<div class='insight-box'>🔍 {insight_txt}</div>", unsafe_allow_html=True)


def view_overlap_analysis(engine: DataEngine):
    st.markdown("## HCP Overlap Analysis")
    st.markdown("*Detailed view of HCPs appearing in both ATU and PET datasets*")

    if engine.overlap_df is None or len(engine.overlap_df) == 0:
        st.error("No overlapping HCPs found. Check data sources.")
        return

    df = engine.overlap_df.copy()

    # Filters
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        seg_options = ['All'] + sorted(df['Glioma_Usage_Segment'].dropna().unique().tolist()) if 'Glioma_Usage_Segment' in df.columns else ['All']
        seg_filter = st.selectbox("Glioma Usage Segment", seg_options)
    with fc2:
        tt_options = ['All'] + sorted(df['ATU_Target_Type'].dropna().unique().tolist()) if 'ATU_Target_Type' in df.columns else ['All']
        tt_filter = st.selectbox("ATU Target Type", tt_options)
    with fc3:
        q_options = ['All'] + QUARTER_ORDER
        q_filter = st.selectbox("Quarter Filter", q_options)

    # Apply filters
    if seg_filter != 'All' and 'Glioma_Usage_Segment' in df.columns:
        df = df[df['Glioma_Usage_Segment'] == seg_filter]
    if tt_filter != 'All' and 'ATU_Target_Type' in df.columns:
        df = df[df['ATU_Target_Type'] == tt_filter]
    if q_filter != 'All':
        if 'ATU_Quarters' in df.columns:
            df = df[df['ATU_Quarters'].str.contains(q_filter, na=False) |
                    df.get('PET_Quarters', pd.Series(dtype=str)).str.contains(q_filter, na=False)]

    st.metric("Filtered Overlap HCPs", len(df))

    # Display table
    display_cols = ['User Id']
    for col in ['ATU_Quarters', 'PET_Quarters', 'ATU_Target_Type', 'PET_Target_Type',
                'Glioma_Usage_Segment', 'ATU_PET_Segment', 'Rep_Interaction_Segment',
                'ATU_Responses', 'PET_Responses']:
        if col in df.columns:
            display_cols.append(col)

    st.dataframe(
        df[display_cols].sort_values('User Id'),
        use_container_width=True,
        height=400
    )

    # Quarter temporal heatmap
    if 'ATU_Quarters' in df.columns and 'PET_Quarters' in df.columns:
        st.markdown("### Temporal Coverage: ATU × PET Quarter Combinations")
        combo_data = []
        for _, row in df.iterrows():
            atu_qs = str(row.get('ATU_Quarters', '')).split(', ')
            pet_qs = str(row.get('PET_Quarters', '')).split(', ')
            for aq in atu_qs:
                for pq in pet_qs:
                    if aq and pq and aq != 'nan' and pq != 'nan':
                        combo_data.append({'ATU_Quarter': aq.strip(), 'PET_Quarter': pq.strip()})

        if combo_data:
            combo_df = pd.DataFrame(combo_data)
            pivot = combo_df.groupby(['ATU_Quarter', 'PET_Quarter']).size().unstack(fill_value=0)
            fig = make_heatmap(pivot, 'HCP Count: ATU Quarter × PET Quarter')
            st.plotly_chart(fig, use_container_width=True)

    # Download
    csv_data = df[display_cols].to_csv(index=False)
    st.download_button(
        "⬇ Download Overlap HCP List (CSV)",
        data=csv_data,
        file_name=f"overlap_hcps_{datetime.now().strftime('%Y%m%d')}.csv",
        mime='text/csv'
    )


def view_segment_intelligence(engine: DataEngine):
    st.markdown("## Segment Intelligence")

    tabs = st.tabs(["Glioma Usage Segments", "ATU+PET Combined Segments", "Rep Interaction Segments"])

    with tabs[0]:
        if engine.segment_hl is None:
            st.info("High/Low/No User segment file not loaded.")
        else:
            df = engine.segment_hl.dropna(subset=['User Id'])

            col1, col2 = st.columns(2)
            with col1:
                seg_counts = df['Segment Value'].value_counts().reset_index()
                seg_counts.columns = ['Segment', 'Count']
                fig = make_bar(seg_counts, 'Segment', 'Count', 'Glioma Usage Distribution',
                               color_col='Segment', colors_map=COLORS)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Wave trend
                if 'Wave Number' in df.columns:
                    wave_seg = df.groupby(['Wave Number', 'Segment Value']).size().reset_index(name='Count')
                    wave_seg['Wave_Num'] = wave_seg['Wave Number'].str.extract(r'(\d+)').astype(float)
                    wave_seg = wave_seg.sort_values('Wave_Num')
                    fig2 = px.line(wave_seg, x='Wave Number', y='Count', color='Segment Value',
                                   color_discrete_map=COLORS)
                    fig2.update_layout(**PLOTLY_TEMPLATE['layout'], height=300,
                                       title=dict(text='Segment Trend Across Waves', font=dict(size=13, color='#F0F4FF')))
                    st.plotly_chart(fig2, use_container_width=True)

            # Wave breakdown table
            st.markdown("### Wave-by-Wave Segment Breakdown")
            if 'Wave Number' in df.columns:
                pivot = df.groupby(['Wave Number', 'Segment Value']).size().unstack(fill_value=0)
                st.dataframe(pivot, use_container_width=True)

    with tabs[1]:
        if engine.segment_atu_pet is None:
            st.info("ATU+PET Perception segment file not loaded.")
        else:
            df2 = engine.segment_atu_pet.dropna(subset=['User Id'])
            seg2 = df2['Segment Value'].value_counts().reset_index()
            seg2.columns = ['Segment', 'Count']

            col1, col2 = st.columns(2)
            with col1:
                fig = make_donut(seg2['Count'].tolist(), seg2['Segment'].tolist(),
                                 'ATU + PET Combined Segments')
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                st.dataframe(seg2, use_container_width=True)

            st.markdown("""
            <div class='insight-box'>
            💡 <b>Segment Interpretation:</b> These segments combine Glioma product usage level (from ATU) 
            with PET perception score (high/low perception of product after rep interaction). 
            HCPs with <i>high perception + high usage</i> represent fully activated advocates, 
            while <i>non-users with high perception</i> indicate conversion opportunity.
            </div>
            """, unsafe_allow_html=True)

    with tabs[2]:
        if engine.segment_rep is None:
            st.info("Rep Driven Attributes segment file not loaded.")
        else:
            df3 = engine.segment_rep.dropna(subset=['User Id'])
            seg3 = df3['Segment Value'].value_counts().reset_index()
            seg3.columns = ['Segment', 'Count']

            fig = make_bar(seg3, 'Segment', 'Count', 'Rep Interaction Segments',
                           color_col='Segment', colors_map={'High LTIP': '#00C850', 'No Interaction': '#8898C8', 'Other': '#E8A838'})
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("""
            <div class='warn-box'>
            ⚡ <b>LTIP = Likelihood to Increase Prescribing.</b> 
            HCPs with "High LTIP" after rep interactions represent highest-value targets for continued engagement. 
            "No Interaction" HCPs in ATU represent an untouched opportunity pool.
            </div>
            """, unsafe_allow_html=True)


def view_question_classifier(engine: DataEngine):
    st.markdown("## Autonomous Question Classifier")
    st.markdown("*Content-driven segmentation of survey questions — no manual mapping required*")

    # Show discovered segments
    with st.expander("📋 Discovered Segment Categories & Classification Rules", expanded=False):
        cols = st.columns(2)
        segments = list(QuestionClassifier.SEGMENT_RULES.keys())
        for i, seg in enumerate(segments):
            with cols[i % 2]:
                rules_preview = ', '.join([r[:30] + '...' if len(r) > 30 else r
                                           for r in QuestionClassifier.SEGMENT_RULES[seg][:4]])
                st.markdown(f"""
                <div class='hcp-card' style='margin: 4px 0; padding: 12px;'>
                    <div style='color: #00B4B4; font-weight: 600; font-size: 0.85rem;'>{seg}</div>
                    <div style='color: #8898C8; font-size: 0.72rem; margin-top: 4px;'>{rules_preview}</div>
                </div>
                """, unsafe_allow_html=True)

    # Input mode
    input_mode = st.radio("Question Source", ["Upload Survey File", "Enter Questions Manually", "Classify ATU Survey Questions", "Classify PET Survey Questions"], horizontal=True)

    questions_to_classify = []

    if input_mode == "Upload Survey File":
        survey_file = st.file_uploader("Upload survey file (CSV/Excel with a question column)", type=['csv', 'xlsx'])
        if survey_file:
            try:
                if survey_file.name.endswith('.csv'):
                    df_survey = pd.read_csv(survey_file)
                else:
                    df_survey = pd.read_excel(survey_file)
                q_col = st.selectbox("Select question column", df_survey.columns.tolist())
                questions_to_classify = df_survey[q_col].dropna().tolist()
            except Exception as e:
                st.error(f"Error: {e}")

    elif input_mode == "Enter Questions Manually":
        raw_text = st.text_area("Paste questions (one per line)", height=200,
                                placeholder="How familiar are you with Glioma?\nWhat percent of patients are tested for IDH mutations?\n...")
        if raw_text:
            questions_to_classify = [q.strip() for q in raw_text.split('\n') if q.strip()]

    elif input_mode == "Classify ATU Survey Questions":
        # Use embedded question list from ATU survey
        atu_questions = [
            "What percent of your newly diagnosed adult-type diffuse glioma patients are initially tested for IDH status with IHC only?",
            "Are you aware of any FDA-approved diagnostic tests available for detecting IDH1 or IDH2 mutations in patients with Grade 2 glioma?",
            "How confident are you that you know the method of molecular testing conducted on biopsy or resection samples from your adult-type diffuse glioma patients?",
            "Please select reasons for not testing all your newly diagnosed adult-type diffuse glioma patients for IDH status with NGS",
            "What percent of your adult-type diffuse glioma patients who test negative for R132h IDH1 mutation through IHC are tested for IDH1 and/or IDH2 using NGS?",
            "What is your typical protocol for ordering NGS testing in newly diagnosed adult-type diffuse glioma patients?",
            "Where is NGS testing in newly diagnosed adult-type diffuse glioma patients typically conducted?",
            "In the last three months only, have you had a request for NGS testing of an adult-type diffuse glioma patient denied by insurance?",
            "Approximately what percent of your adult-type diffuse glioma patients do you test for BRAF, CDKN2A/B, EGFR, IDH1, IDH2, MGMT promoter methylation?",
            "How familiar are you with the v1.2025 NCCN CNS update published in June 2025?",
            "What treatments come to mind when thinking of treating IDH-mutant astrocytoma or oligodendroglioma patients?",
            "How familiar are you with each of the following as a treatment for IDH-mutant astrocytoma or oligodendroglioma? Including Temozolomide, PCV regimen, Glioma, ivosidenib",
            "Among your grade 2 patients with IDH-mutant astrocytoma or oligodendroglioma how many are newly diagnosed?",
            "How many of your grade 2 IDH-mutant astrocytoma and oligodendroglioma patients meet each of the following descriptions (Adjuvant, Stable, Recurrence)?",
            "How many of your patients of this type are currently receiving each treatment? And what treatment will your next 10 patients receive?",
            "How frequently do you obtain MRIs for your post-resection IDH-mutant astrocytoma and oligodendroglioma patients to check for progression?",
            "Please elaborate on your MRI monitoring practices – think about how it is evolving in connection to treatment advancements",
            "Rate the importance of each attribute when selecting a treatment for grade 2 IDH-mutant astrocytoma or oligodendroglioma patients - Prolonged PFS, OS, adverse events, hepatic toxicity, LFT monitoring",
            "How would you rate Glioma, Temozolomide+RT, and Radiation therapy alone on each attribute including PFS, OS, adverse events, hepatic toxicity?",
            "What percent of the time do you dispense Glioma to grade 2 IDH-mutant astrocytoma or oligodendroglioma patients via internal vs external specialty pharmacy?",
            "How much impact do insurance coverage, NCCN guidelines, reimbursement level have on your decision to prescribe Glioma?",
            "Which of the following are the main barriers to prescribing Glioma for IDH-mutant astrocytoma or oligodendroglioma patients?",
            "How familiar are you with the Glioma Manufacturer Support Program?",
            "Which Glioma Manufacturer patient support services are you aware of - Commercial Co-Pay Program, Bridge Program, Patient Assistance Program, QuickStart?",
            "How often do patients ask about Glioma as a treatment option for IDH-mutant astrocytoma or oligodendroglioma?",
            "To what extent does patient inquiry influence your decision to prescribe or recommend Glioma?",
            "In the past 6 months, where have you seen or heard information on IDH-mutant astrocytoma or oligodendroglioma?",
            "Gliomas are the most common primary malignant brain tumor - how strongly do you agree or disagree?",
            "IDH-mutant glioma is a distinct molecularly defined glioma sub-type in the WHO CNS Tumors 2021 classification",
            "How many physicians are in your practice? What percent of your patient population have Commercial, Medicare, Medicaid insurance?",
            "Does your practice have an out-patient pharmacy on site? Have you been involved in clinical trials for adult-type diffuse gliomas?",
        ]
        questions_to_classify = atu_questions

    elif input_mode == "Classify PET Survey Questions":
        pet_questions = [
            "How much time (in minutes) did you spend with the Glioma Manufacturer rep during your most recent interaction?",
            "During your most recent interaction with the Glioma Manufacturer representative, what proportion of time was spent discussing Disease State Education vs Glioma product?",
            "How valuable did you find the disease state education (DSE) content provided during your most recent interaction?",
            "Did the disease state education (DSE) highlight any gaps or unmet needs in your current knowledge or practice?",
            "Please select the type of interaction you had with Glioma Manufacturer sales rep - In-person, Video conference, Tele-conference",
            "Which of the following topics were discussed during your most recent interaction with the Glioma Manufacturer representative? (Efficacy, Safety, Dosing, Patient types, Access, NCCN Guidelines, Molecular testing)",
            "What are the primary messages you recall hearing during your most recent interaction with the Glioma Manufacturer sales rep discussing Glioma for Gliomas?",
            "Which Glioma sales messages do you specifically recall hearing - Glioma indicated for Grade 2 patients 12+, first treatment in 20+ years, dual inhibitor targeting mIDH1 and mIDH2?",
            "Did the Glioma Manufacturer sales rep specifically ask you to prescribe Glioma for Gliomas?",
            "Prior to your most recent interaction with Glioma Manufacturer sales representative, please rate your likelihood to prescribe Glioma for Gliomas",
            "How likely are you to increase prescribing Glioma for Gliomas based on your most recent interaction with the Glioma Manufacturer representative?",
            "Based on your most recent interaction with the Glioma Manufacturer sales rep, please indicate the change in your perception of Glioma across Efficacy, Safety, Dosing, Access attributes",
            "Please indicate the importance of rep performance attributes - How prepared, organized, knowledgeable, engaging was the Glioma Manufacturer rep?",
            "How frequently do you discuss Gliomas with Glioma Manufacturer sales reps?",
            "Glioma Manufacturer reps have provided me with useful materials that help me educate my patients about Glioma",
            "Glioma Manufacturer reps have been supportive in ensuring that my patients can get access to Glioma",
            "Which Glioma Manufacturer patient support services are you aware of - Commercial Co-Pay, Bridge Program, PAP, QuickStart?",
            "Please indicate via which channels you have received information regarding Glioma - Online ads, Email, Medical journals, Conferences, Social media",
            "Please rate the online ad you recently saw about Glioma across motivating, believable, clear, relevant dimensions",
            "How frequently do you conduct molecular or mutational testing for your glioma patients at initial diagnosis?",
            "When glioma patients initiate conversations about treatment options, how often do you discuss supporting clinical evidence?",
            "How do patient preferences for fertility, delaying radiation, limited long-term evidence influence your treatment decision?",
            "Please name all the products you are aware of that are currently available for the treatment of Gliomas",
            "Glioma is indicated for treatment of patients 12 years and older with Grade 2 astrocytoma or oligodendroglioma with IDH1 or IDH2 mutation - is this message differentiated, believable, motivating?",
            "Glioma is the first new treatment in more than 20 years for Grade 2 mIDH glioma - how differentiated and motivating is this message?",
        ]
        questions_to_classify = pet_questions

    if questions_to_classify:
        with st.spinner("Classifying questions..."):
            results_df = QuestionClassifier.classify_batch(questions_to_classify)

        # Summary stats
        total = len(results_df)
        classified = len(results_df[results_df['Segment'] != 'Uncategorized'])
        avg_conf = results_df['Confidence'].mean()

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Questions", total)
        m2.metric("Classified", classified, f"{classified/total*100:.0f}%")
        m3.metric("Unclassified", total - classified)
        m4.metric("Avg Confidence", f"{avg_conf:.0%}")

        col1, col2 = st.columns([1, 1.5])
        with col1:
            seg_dist = results_df['Segment'].value_counts().reset_index()
            seg_dist.columns = ['Segment', 'Count']
            fig = px.bar(seg_dist, x='Count', y='Segment', orientation='h',
                         color='Count', color_continuous_scale=['#1C2B4A', '#C8102E'])
            fig.update_layout(**PLOTLY_TEMPLATE['layout'], height=400,
                              title=dict(text='Questions per Segment', font=dict(size=13, color='#F0F4FF')),
                              showlegend=False)
            fig.update_coloraxes(showscale=False)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Confidence distribution
            fig2 = px.histogram(results_df, x='Confidence', nbins=10,
                                color_discrete_sequence=['#00B4B4'])
            fig2.update_layout(**PLOTLY_TEMPLATE['layout'], height=400,
                               title=dict(text='Classification Confidence Distribution', font=dict(size=13, color='#F0F4FF')))
            st.plotly_chart(fig2, use_container_width=True)

        # Filters
        st.markdown("### Classified Questions")
        fc1, fc2 = st.columns(2)
        with fc1:
            seg_filter = st.selectbox("Filter by Segment", ['All'] + sorted(results_df['Segment'].unique().tolist()))
        with fc2:
            conf_filter = st.slider("Min Confidence", 0.0, 1.0, 0.0, 0.1)

        filtered = results_df.copy()
        if seg_filter != 'All':
            filtered = filtered[filtered['Segment'] == seg_filter]
        filtered = filtered[filtered['Confidence'] >= conf_filter]

        # Color code confidence
        def conf_color(val):
            if val >= 0.7:
                return 'color: #00C850'
            elif val >= 0.4:
                return 'color: #E8A838'
            return 'color: #FF6B7A'

        st.dataframe(
            filtered[['Question', 'Segment', 'Confidence', 'Matched_Patterns']],
            use_container_width=True,
            height=400
        )

        # Export
        csv_out = filtered.to_csv(index=False)
        st.download_button("⬇ Export Classifications (CSV)", data=csv_out,
                           file_name="question_classifications.csv", mime='text/csv')

        json_out = json.dumps(filtered.to_dict(orient='records'), indent=2)
        st.download_button("⬇ Export Classifications (JSON)", data=json_out,
                           file_name="question_classifications.json", mime='application/json')


def view_temporal_trends(engine: DataEngine):
    st.markdown("## Temporal Trends")
    st.markdown("*How HCP composition and segments evolve across quarters*")

    if engine.atu_df is None:
        st.info("No data loaded.")
        return

    col1, col2 = st.columns(2)

    with col1:
        if 'Quarter' in engine.atu_df.columns and 'Target_Type' in engine.atu_df.columns:
            st.markdown("### ATU: Target Type × Quarter")
            atu_tt_q = engine.atu_df.groupby(['Quarter', 'Target_Type'])['User Id'].nunique().reset_index(name='HCPs')
            fig = px.bar(atu_tt_q, x='Quarter', y='HCPs', color='Target_Type',
                         color_discrete_map=COLORS, barmode='stack')
            fig.update_layout(**PLOTLY_TEMPLATE['layout'], height=320)
            st.plotly_chart(fig, use_container_width=True)

        if engine.segment_hl is not None and 'Wave Number' in engine.segment_hl.columns:
            st.markdown("### Glioma Usage Segment by Wave")
            df_hl = engine.segment_hl.dropna(subset=['User Id'])
            df_hl['Wave_Num'] = df_hl['Wave Number'].str.extract(r'(\d+)').astype(float)
            wave_seg = df_hl.groupby(['Wave Number', 'Wave_Num', 'Segment Value']).size().reset_index(name='Count')
            wave_seg = wave_seg.sort_values('Wave_Num')
            fig2 = px.area(wave_seg, x='Wave Number', y='Count', color='Segment Value',
                           color_discrete_map=COLORS)
            fig2.update_layout(**PLOTLY_TEMPLATE['layout'], height=320,
                               title=dict(text='Usage Segment Evolution Across Waves', font=dict(size=13, color='#F0F4FF')))
            st.plotly_chart(fig2, use_container_width=True)

    with col2:
        if engine.pet_df is not None and 'Quarter' in engine.pet_df.columns and 'Target_Type' in engine.pet_df.columns:
            st.markdown("### PET: Target Type × Quarter")
            pet_tt_q = engine.pet_df.groupby(['Quarter', 'Target_Type'])['User Id'].nunique().reset_index(name='HCPs')
            pet_tt_q = pet_tt_q[pet_tt_q['Quarter'].isin(QUARTER_ORDER)]
            fig3 = px.bar(pet_tt_q, x='Quarter', y='HCPs', color='Target_Type',
                          color_discrete_map=COLORS, barmode='stack',
                          category_orders={'Quarter': QUARTER_ORDER})
            fig3.update_layout(**PLOTLY_TEMPLATE['layout'], height=320)
            st.plotly_chart(fig3, use_container_width=True)

        # Overlap by quarter pair
        if engine.overlap_df is not None and 'ATU_Quarters' in engine.overlap_df.columns:
            st.markdown("### Overlap HCPs per ATU Quarter")
            q_rows = []
            for q in ATU_QUARTERS:
                count = engine.overlap_df[engine.overlap_df['ATU_Quarters'].str.contains(q, na=False)].shape[0]
                q_rows.append({'ATU Quarter': q, 'Overlap HCPs': count})
            q_df = pd.DataFrame(q_rows)
            fig4 = make_bar(q_df, 'ATU Quarter', 'Overlap HCPs', 'ATU-PET Overlap by Quarter')
            st.plotly_chart(fig4, use_container_width=True)

    # Trend table
    if engine.segment_hl is not None:
        st.markdown("### Complete Wave-Segment Matrix")
        df_hl = engine.segment_hl.dropna(subset=['User Id'])
        if 'Wave Number' in df_hl.columns and 'Segment Value' in df_hl.columns:
            pivot = df_hl.groupby(['Wave Number', 'Segment Value']).size().unstack(fill_value=0)
            pivot['Total'] = pivot.sum(axis=1)
            # Add % cols
            for seg in [c for c in pivot.columns if c != 'Total']:
                pivot[f'{seg} %'] = (pivot[seg] / pivot['Total'] * 100).round(1).astype(str) + '%'
            st.dataframe(pivot, use_container_width=True)


def view_raw_data(engine: DataEngine):
    st.markdown("## Raw Data Explorer")

    ds = st.selectbox("Dataset", ["ATU Raw", "PET Raw", "Segment: High/Low/No", "Segment: ATU+PET", "Segment: Rep Attrs"])

    df_map = {
        "ATU Raw": engine.atu_df,
        "PET Raw": engine.pet_df,
        "Segment: High/Low/No": engine.segment_hl,
        "Segment: ATU+PET": engine.segment_atu_pet,
        "Segment: Rep Attrs": engine.segment_rep,
    }

    df = df_map.get(ds)
    if df is None:
        st.info(f"No data loaded for {ds}")
        return

    # Info
    st.markdown(f"""
    <div class='hcp-card'>
    <b>Shape:</b> {df.shape[0]:,} rows × {df.shape[1]:,} columns &nbsp;|&nbsp;
    <b>Unique HCPs:</b> {df['User Id'].nunique() if 'User Id' in df.columns else 'N/A'} &nbsp;|&nbsp;
    <b>Columns:</b> {df.shape[1]}
    </div>
    """, unsafe_allow_html=True)

    # Column search
    col_search = st.text_input("Search columns", placeholder="e.g. Quarter, Segment, Wave...")
    if col_search:
        matching = [c for c in df.columns if col_search.lower() in str(c).lower()]
        display_df = df[matching] if matching else df
    else:
        display_df = df

    # Row limit
    n_rows = st.slider("Preview rows", 10, min(500, len(df)), 50)

    st.dataframe(display_df.head(n_rows), use_container_width=True, height=500)

    # Download
    csv_data = display_df.to_csv(index=False)
    st.download_button(f"⬇ Download {ds} (CSV)", data=csv_data,
                       file_name=f"{ds.replace(' ', '_').lower()}.csv", mime='text/csv')


# ─────────────────────────────────────────────
# MODULE-LEVEL CACHED DATA LOADER
# @st.cache_resource must be at module scope to work reliably on all
# Streamlit versions — nested decorators can silently fail on Cloud.
# ─────────────────────────────────────────────
@st.cache_resource
def _load_project_files_cached():
    """Search candidate directories for project xlsx files, load, and cache."""
    engine = DataEngine()
    candidate_dirs = [
        Path('/mnt/project'),
        Path('.'),
        Path('/home/claude/hcp_dashboard'),
        Path('/app'),
        Path('/mount/src'),
        Path('/mount/src/hcp_dashboard'),
    ]
    project = None
    for d in candidate_dirs:
        try:
            if (d / 'GLIOMA_ATU_Q126_Q226.xlsx').exists():
                project = d
                break
        except Exception:
            continue

    if project is None:
        engine.errors.append(
            "Project files not found. Switch to 'Upload Custom Files' in the sidebar "
            "and upload your ATU and PET Excel files directly."
        )
        return engine

    def _safe(p):
        try:
            return p if p.exists() else None
        except Exception:
            return None

    try:
        engine.load_from_paths(
            atu_path=project / 'GLIOMA_ATU_Q126_Q226.xlsx',
            pet_path=project / 'GLIOMA_PET_Q425_Q126_Q226.xlsx',
            hl_path=_safe(project / 'High_vs_Low_vs_No_User_ATU_PET_Segment.xlsx'),
            atu_pet_path=_safe(project / 'ATU_Usage_and_PET_Perception.xlsx'),
            rep_path=_safe(project / 'Rep_Driven_Attributes_ATU.xlsx'),
        )
    except Exception as e:
        engine.errors.append(f"Data loading error: {e}")
    return engine


# ─────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────
def main():
    data_mode, uploaded, analysis_view = render_sidebar()

    # ── Load data ──
    if data_mode == "Use Project Files":
        engine = _load_project_files_cached()
    else:
        # Upload mode
        if uploaded.get('atu') and uploaded.get('pet'):
            engine = DataEngine()
            engine.load_from_uploads(
                atu_file=uploaded['atu'],
                pet_file=uploaded['pet'],
                hl_file=uploaded.get('hl'),
                atu_pet_file=uploaded.get('atu_pet'),
                rep_file=uploaded.get('rep'),
            )
        else:
            engine = DataEngine()
            st.markdown("""
            <div class='hero-banner'>
                <div class='hero-badge'>AWAITING DATA</div>
                <div class='hero-title'>Upload Your Research Files</div>
                <div class='hero-sub'>Please upload ATU (2 quarters) and PET (3 quarters) raw files in the sidebar to begin analysis.</div>
            </div>
            """, unsafe_allow_html=True)
            return

    # Show errors if any
    if engine.errors:
        with st.expander(f"⚠ {len(engine.errors)} Data Warning(s)", expanded=False):
            for err in engine.errors:
                st.warning(err)

    # ── Route views ──
    view_map = {
        "Executive Overview": view_executive_overview,
        "HCP Overlap Analysis": view_overlap_analysis,
        "Segment Intelligence": view_segment_intelligence,
        "Question Classifier": view_question_classifier,
        "Temporal Trends": view_temporal_trends,
        "Raw Data Explorer": view_raw_data,
    }

    view_fn = view_map.get(analysis_view)
    if view_fn:
        if analysis_view == "Question Classifier":
            view_fn(engine)
        else:
            view_fn(engine)


if __name__ == "__main__":
    try:
        main()
    except Exception as _app_err:
        import traceback as _tb
        st.error(f"**Application startup error:** {_app_err}")
        with st.expander("Show full traceback for debugging"):
            st.code(_tb.format_exc())
