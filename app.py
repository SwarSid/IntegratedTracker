"""
HCP Intelligence Platform — Glioma Research Analytics
Auto-segments from raw ATU + PET uploads. Zero manual configuration.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import re, io
from pathlib import Path

st.set_page_config(page_title="HCP Intelligence", page_icon="🧬", layout="wide",
                   initial_sidebar_state="expanded")

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');
:root{--red:#C8102E;--navy:#0D1B3E;--slate:#1C2B4A;--teal:#00B4B4;--gold:#E8A838;
      --fg:#F0F4FF;--muted:#8898C8;--border:rgba(200,220,255,.12);--card:rgba(28,43,74,.6)}
.stApp{background:#0A0F1E;font-family:"DM Sans",sans-serif}
#MainMenu,footer,.stDeployButton{visibility:hidden}
h1,h2,h3{font-family:"DM Serif Display",serif;color:var(--fg)}
[data-testid="stSidebar"]{background:var(--navy)!important;border-right:1px solid var(--border)}
[data-testid="stMetric"]{background:var(--card)!important;border:1px solid var(--border)!important;
  border-radius:12px!important;padding:16px!important}
[data-testid="stMetricLabel"]{color:var(--muted)!important;font-size:.75rem!important;
  text-transform:uppercase;letter-spacing:.08em}
[data-testid="stMetricValue"]{color:var(--fg)!important;font-family:"DM Serif Display",serif!important}
.stTabs [data-baseweb="tab-list"]{background:var(--navy)!important;border-bottom:1px solid var(--border)}
.stTabs [data-baseweb="tab"]{color:var(--muted)!important;font-size:.8rem!important;text-transform:uppercase}
.stTabs [aria-selected="true"]{color:var(--teal)!important;border-bottom:2px solid var(--teal)!important}
.stButton>button{background:linear-gradient(135deg,var(--red),#8B0A20)!important;color:#fff!important;
  border:none!important;border-radius:8px!important;font-weight:600!important}
.card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:20px;margin:6px 0}
.hero{background:linear-gradient(135deg,var(--navy),var(--slate),rgba(200,16,46,.12));
  border:1px solid var(--border);border-radius:16px;padding:28px 36px;margin-bottom:20px}
.badge{display:inline-block;background:rgba(200,16,46,.2);border:1px solid rgba(200,16,46,.4);
  color:#FF6B7A;font-size:.7rem;font-weight:700;letter-spacing:.1em;padding:3px 10px;
  border-radius:20px;margin-bottom:10px;text-transform:uppercase}
.insight{background:rgba(0,180,180,.08);border-left:3px solid var(--teal);
  border-radius:0 8px 8px 0;padding:12px 16px;margin:10px 0;color:var(--fg);font-size:.87rem}
.seg-pill{display:inline-block;padding:3px 12px;border-radius:20px;font-size:.78rem;font-weight:600;margin:2px}
.seg-high{background:rgba(0,200,80,.15);color:#00C850;border:1px solid rgba(0,200,80,.3)}
.seg-low{background:rgba(232,168,56,.15);color:#E8A838;border:1px solid rgba(232,168,56,.3)}
.seg-non{background:rgba(136,152,200,.15);color:var(--muted);border:1px solid rgba(136,152,200,.3)}
</style>""", unsafe_allow_html=True)

# ── Brand masking ──────────────────────────────────────────────────────────────
_PROD_PAT = re.compile(
    r"\b(VORANIGO|Voranigo|voranigo|vorasidenib|Vorasidenib|VORASIDENIB|"
    r"Vorasedinib|Vorasidinib|Vorasedenib|voradesnib|Voracitinib|"
    r"voracetinib|Voricitinib|voricitinib|VORA)\b", re.IGNORECASE)
_CO_PAT = re.compile(
    r"\b(ServierONE|Servier\s*ONE|Servier\s+Pharmaceuticals|Servier|"
    r"SERVIER|servier)\b", re.IGNORECASE)

def _mask(v):
    if not isinstance(v, str): return v
    v = _PROD_PAT.sub("Product Glioma", v)
    v = _CO_PAT.sub("Manufacturer Glioma", v)
    return v

def mask_df(df):
    if df is None: return df
    df = df.copy()
    df.columns = [_mask(str(c)) for c in df.columns]
    for col in df.columns:
        if df[col].dtype == object or str(df[col].dtype).lower() in ("str","string"):
            df[col] = df[col].apply(lambda v: _mask(str(v)) if pd.notna(v) else v)
    return df

# ── Chart theme ────────────────────────────────────────────────────────────────
DARK = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#F0F4FF", family="DM Sans"),
            xaxis=dict(gridcolor="rgba(200,220,255,.08)"),
            yaxis=dict(gridcolor="rgba(200,220,255,.08)"),
            margin=dict(l=0,r=0,t=36,b=0))

SEG_COLORS = {
    "High Product Glioma Usage":"#00C850","Low Product Glioma Usage":"#E8A838",
    "Non Product Glioma User":"#8898C8",
    "High Vora Usage":"#00C850","Low Vora Usage":"#E8A838","Non Vora User":"#8898C8",
    "Interaction":"#C8102E","No Interaction":"#8898C8",
    "Q4\'25":"#8B5CF6","Q1\'26":"#00B4B4","Q2\'26":"#C8102E"
}

def donut(vals, labels, title):
    clr = [SEG_COLORS.get(l,"#8898C8") for l in labels]
    fig = go.Figure(go.Pie(values=vals, labels=labels, hole=.6,
                           textinfo="percent+label", textfont=dict(size=11),
                           marker=dict(colors=clr, line=dict(color="#0A0F1E",width=2))))
    fig.update_layout(**DARK, height=260, showlegend=False,
                      title=dict(text=title, font=dict(size=12,color="#F0F4FF"),x=.5))
    return fig

def hbar(labels, values, title, color="#C8102E", n=None):
    pct_labels = [f"{v:.0f}%" for v in values]
    fig = go.Figure(go.Bar(y=labels, x=values, orientation="h",
                           marker_color=color, text=pct_labels, textposition="outside"))
    t = title + (f" (n={n})" if n else "")
    fig.update_layout(**DARK, height=max(220, len(labels)*24),
                      title=dict(text=t, font=dict(size=13,color="#F0F4FF")))
    return fig

# ══════════════════════════════════════════════════════════════════════════════
# RAW FILE PARSER
# ══════════════════════════════════════════════════════════════════════════════
class RawParser:
    """Auto-discovers LimeSurvey export structure.
    Row 0 = col IDs | Row 3 = question text | Row 4+ = sub-labels + data"""
    def __init__(self, file_obj):
        raw = pd.read_excel(file_obj, sheet_name=0, header=None, dtype=object)
        self._raw = raw
        hdr = 0
        for i in range(min(5, raw.shape[0])):
            if str(raw.iloc[i,1]).strip() == "User Id":
                hdr = i; break
        self.hdr = hdr
        self.col_ids = raw.iloc[hdr, :]
        self.q_text  = raw.iloc[hdr+3, :] if hdr+3 < raw.shape[0] else raw.iloc[-1,:]
        self.sub_lbl = raw.iloc[hdr+4, :] if hdr+4 < raw.shape[0] else raw.iloc[-1,:]
        self.tag_row = raw.iloc[hdr+2, :] if hdr+2 < raw.shape[0] else raw.iloc[-1,:]
        self.n_cols  = raw.shape[1]
        # Find data start
        self.data_start = hdr+4
        for i in range(hdr+1, raw.shape[0]):
            if pd.notna(pd.to_numeric(raw.iloc[i,1], errors="coerce")):
                self.data_start = i; break

    def get_df(self):
        raw = self._raw
        col_names = [str(v) if pd.notna(v) else f"col_{i}"
                     for i, v in enumerate(self.col_ids)]
        df = raw.iloc[self.data_start:, :].copy()
        df.columns = col_names
        df = df.rename(columns={col_names[1]: "User Id"})
        df["User Id"] = pd.to_numeric(df["User Id"], errors="coerce")
        df = df.dropna(subset=["User Id"])
        df["User Id"] = df["User Id"].astype(int)
        # Quarter
        for i in [2,3]:
            vals = df.iloc[:,i].dropna().astype(str).str.strip().unique()
            if any(v.startswith("Q") for v in vals):
                df = df.rename(columns={col_names[i]:"Quarter"}); break
        # Target type
        for i in [2,3,4]:
            vals = df.iloc[:,i].dropna().astype(str).str.strip().unique()
            if any(t in vals for t in ["On Target","Off target","Co-locs"]):
                df = df.rename(columns={col_names[i]:"Target_Type"}); break
        return mask_df(df)

    def get_blocks(self, df, uid_set=None):
        """Auto-discover question blocks tagged in tag_row. Return list of block dicts."""
        sub_df = df[df["User Id"].isin(uid_set)].copy() if uid_set else df
        n = len(sub_df)
        if n == 0: return []
        raw = self._raw
        seen = set(); blocks = []
        col_list = list(df.columns)

        for i in range(self.n_cols):
            tag = str(self.tag_row.iloc[i]).strip() if i < self.n_cols else ""
            if not tag or tag == "nan" or tag in seen: continue
            cols_i = [j for j in range(self.n_cols)
                      if str(self.tag_row.iloc[j]).strip() == tag]
            if len(cols_i) < 2: seen.add(tag); continue
            seen.add(tag)
            qt = str(self.q_text.iloc[cols_i[0]]) if cols_i[0] < len(self.q_text) else tag
            if qt.startswith("{") or not qt.strip() or qt == "nan": continue
            qt = _mask(qt[:90])

            rows = []
            for ci in cols_i:
                sl = str(self.sub_lbl.iloc[ci]) if ci < len(self.sub_lbl) else ""
                if not sl or sl == "nan" or sl.startswith("{") or sl.startswith("Q"): continue
                label = _mask(sl[:70])
                if ci < len(col_list):
                    cname = col_list[ci]
                    if cname in df.columns:
                        num = pd.to_numeric(sub_df[cname], errors="coerce")
                        if num.notna().sum() > 0:
                            pct_hi = (num >= 6).mean() * 100
                            pct_sel = (num >= 1).mean() * 100
                            mean_v  = num.mean()
                            rows.append({"Label":label,"PctHigh":pct_hi,"PctSel":pct_sel,"Mean":mean_v,"n":n})
            if rows:
                blocks.append({"title":qt,"tag":tag,"df":pd.DataFrame(rows).drop_duplicates("Label")})
            if len(blocks) >= 25: break
        return blocks

# ══════════════════════════════════════════════════════════════════════════════
# SEGMENT AUTO-DETECTOR (reverse-engineered from segment files)
# ══════════════════════════════════════════════════════════════════════════════
class Segmenter:
    """
    Reverse-engineers segment logic:
    - HIGH: Q2.20 familiarity=5 AND above-median current Voranigo patients
    - LOW:  familiarity=4-5 but low/zero patients
    - NON:  familiarity <=3
    - REP:  ATU HCP appears in PET = Interaction, else No Interaction
    - CROSS: Usage tier x PET LTIP score (Q3.35)
    """
    FAM_COL_IDX     = 151   # Q2.20_k = Product Glioma familiarity
    USAGE_PAT       = re.compile(r"B8_A1|B9_A1|B10_A1|B12_A1")
    Q110_TAG        = "Q3_110Z"
    Q120_TAG        = "Q3_120Z"

    @classmethod
    def usage_segments(cls, parser):
        raw = parser._raw
        col_ids = parser.col_ids
        ds = parser.data_start
        fam_col = cls.FAM_COL_IDX
        # Find actual familiarity col (B11 = Product Glioma in Q2.20)
        for i in range(139,160):
            sl = str(parser.sub_lbl.iloc[i]) if i < len(parser.sub_lbl) else ""
            if "voranigo" in sl.lower() or "product glioma" in sl.lower():
                fam_col = i; break
        # Voranigo usage cols
        vora_cols = [i for i in range(167,410)
                     if i < parser.n_cols and cls.USAGE_PAT.search(str(col_ids.iloc[i]))]
        per_user = {}
        for ri in range(ds, raw.shape[0]):
            uid = pd.to_numeric(raw.iloc[ri,1], errors="coerce")
            if pd.isna(uid): continue
            uid = int(uid)
            fam = pd.to_numeric(raw.iloc[ri, fam_col] if fam_col < raw.shape[1] else np.nan,
                                 errors="coerce")
            usage = sum(pd.to_numeric(raw.iloc[ri,c], errors="coerce") or 0
                        for c in vora_cols if c < raw.shape[1])
            per_user[uid] = (fam, usage)

        med = np.median([u for f,u in per_user.values() if f==5 and u>0]) or 0
        seg = {}
        for uid,(fam,usage) in per_user.items():
            if pd.isna(fam) or fam <= 3:
                seg[uid] = "Non Product Glioma User"
            elif fam == 5 and usage >= max(med,1):
                seg[uid] = "High Product Glioma Usage"
            else:
                seg[uid] = "Low Product Glioma Usage"
        return seg

    @classmethod
    def rep_segments(cls, atu_df, pet_df):
        pet_ids = set(pet_df["User Id"].unique()) if pet_df is not None else set()
        return {uid: ("Interaction" if uid in pet_ids else "No Interaction")
                for uid in atu_df["User Id"].unique()}

    @classmethod
    def cross_segments(cls, usage_seg, pet_df, pet_parser):
        if pet_df is None: return {}
        pet_ids = set(pet_df["User Id"].unique())
        # Find LTIP col in PET
        ltip_col = None
        for i in range(pet_parser.n_cols):
            qt = str(pet_parser.q_text.iloc[i]) if i < len(pet_parser.q_text) else ""
            if "likely" in qt.lower() and "increase" in qt.lower() and "prescrib" in qt.lower():
                ltip_col = i; break
        raw = pet_parser._raw
        pet_ltip = {}
        for ri in range(pet_parser.data_start, raw.shape[0]):
            uid = pd.to_numeric(raw.iloc[ri,1], errors="coerce")
            if pd.isna(uid): continue
            uid = int(uid)
            if ltip_col:
                sc = pd.to_numeric(raw.iloc[ri,ltip_col], errors="coerce")
            else:
                sc = np.nan
            pet_ltip.setdefault(uid,[])
            if pd.notna(sc): pet_ltip[uid].append(sc)

        p_tier = {}
        for uid,scores in pet_ltip.items():
            avg = np.mean(scores) if scores else np.nan
            p_tier[uid] = ("high perception" if not pd.isna(avg) and avg>=6
                           else ("low perception" if not pd.isna(avg) else "no interaction"))

        cross = {}
        for uid, useg in usage_seg.items():
            tier = useg.split()[0]
            pt = p_tier.get(uid,"no interaction") if uid in pet_ids else "no interaction"
            cross[uid] = f"{tier} User and {pt}"
        return cross

    @classmethod
    def get_q_block(cls, df, uid_set, tag, parser):
        sub_df = df[df["User Id"].isin(uid_set)] if uid_set else df
        n = len(sub_df)
        if n == 0: return pd.DataFrame()
        raw = parser._raw
        col_list = list(df.columns)
        cols_i = [i for i in range(parser.n_cols)
                  if str(parser.tag_row.iloc[i]).strip() == tag]
        rows = []
        for ci in cols_i:
            sl = str(parser.sub_lbl.iloc[ci]) if ci < len(parser.sub_lbl) else ""
            if not sl or sl == "nan" or sl.startswith("{") or sl.startswith("Q"): continue
            label = _mask(sl[:80])
            if ci < len(col_list):
                cname = col_list[ci]
                if cname in df.columns:
                    num = pd.to_numeric(sub_df[cname], errors="coerce")
                    if num.notna().sum() > 0:
                        rows.append({"Attribute":label,
                                     "% Rating 6-7": (num>=6).mean()*100,
                                     "Mean Score": num.mean(), "n":n})
        return pd.DataFrame(rows).drop_duplicates("Attribute") if rows else pd.DataFrame()

# ══════════════════════════════════════════════════════════════════════════════
# DATA ENGINE
# ══════════════════════════════════════════════════════════════════════════════
class Engine:
    def __init__(self):
        self.atu_df = self.pet_df = None
        self.atu_p  = self.pet_p  = None
        self.usage_seg = self.rep_seg = self.cross_seg = {}
        self.errors = []

    def load(self, atu_file, pet_file=None):
        try:
            self.atu_p = RawParser(atu_file)
            self.atu_df = self.atu_p.get_df()
        except Exception as e:
            self.errors.append(f"ATU: {e}"); return
        if pet_file:
            try:
                self.pet_p = RawParser(pet_file)
                self.pet_df = self.pet_p.get_df()
            except Exception as e:
                self.errors.append(f"PET: {e}")
        # Segments
        self.usage_seg = Segmenter.usage_segments(self.atu_p)
        self.rep_seg   = Segmenter.rep_segments(self.atu_df, self.pet_df)
        if self.pet_df is not None and self.pet_p:
            self.cross_seg = Segmenter.cross_segments(self.usage_seg, self.pet_df, self.pet_p)
        # Attach
        self.atu_df["Seg_Usage"] = self.atu_df["User Id"].map(self.usage_seg)
        self.atu_df["Seg_Rep"]   = self.atu_df["User Id"].map(self.rep_seg)
        self.atu_df["Seg_Cross"] = self.atu_df["User Id"].map(self.cross_seg)
        if self.pet_df is not None:
            self.pet_df["Seg_Usage"] = self.pet_df["User Id"].map(self.usage_seg)
            self.pet_df["Seg_Rep"]   = self.pet_df["User Id"].map(self.rep_seg)

    def filter(self, col, val, source="atu"):
        df = self.atu_df if source=="atu" else self.pet_df
        if df is None: return pd.DataFrame()
        if val == "All": return df
        return df[df[col]==val].copy()

    def q110(self, uid_set):
        return Segmenter.get_q_block(self.atu_df, uid_set, Segmenter.Q110_TAG, self.atu_p) if self.atu_p else pd.DataFrame()

    def q120(self, uid_set):
        return Segmenter.get_q_block(self.atu_df, uid_set, Segmenter.Q120_TAG, self.atu_p) if self.atu_p else pd.DataFrame()

    def blocks(self, uid_set, source="atu"):
        p = self.atu_p if source=="atu" else self.pet_p
        df= self.atu_df if source=="atu" else self.pet_df
        if p is None or df is None: return []
        return p.get_blocks(df, uid_set)

    def export_csv(self, seg_col, seg_val):
        filt = self.filter(seg_col, seg_val)
        n = filt["User Id"].nunique()
        uid_set = set(filt["User Id"].unique())
        rows = [{"Section":"Profile","Metric":"N","Value":n,"Segment":seg_val}]
        if "Target_Type" in filt.columns:
            for tt,cnt in filt["Target_Type"].value_counts().items():
                rows.append({"Section":"Profile","Metric":f"Target — {tt}",
                              "Value":f"{cnt/n:.1%}","Segment":seg_val})
        for tag,sec in [(Segmenter.Q110_TAG,"Q3.110"),(Segmenter.Q120_TAG,"Q3.120")]:
            blk = Segmenter.get_q_block(self.atu_df, uid_set, tag, self.atu_p) if self.atu_p else pd.DataFrame()
            for _,r in blk.iterrows():
                rows.append({"Section":sec,"Metric":r["Attribute"],
                              "Value":f"{r['% Rating 6-7']:.1f}%","Segment":seg_val})
        buf = io.BytesIO()
        pd.DataFrame(rows).to_csv(buf, index=False)
        return buf.getvalue(), f"Glioma_{seg_val.replace(' ','_')}.csv"

# ══════════════════════════════════════════════════════════════════════════════
# VIEWS
# ══════════════════════════════════════════════════════════════════════════════
def pill(seg):
    cls = "seg-high" if "High" in seg else ("seg-low" if "Low" in seg else "seg-non")
    return f"<span class='seg-pill {cls}'>{seg}</span>"

def view_overview(eng):
    atu = eng.atu_df; pet = eng.pet_df
    st.markdown("""<div class='hero'>
        <div class='badge'>Glioma Program · FY26</div>
        <h1 style='margin:0'>ATU & PET Integrated Intelligence</h1>
        <p style='color:#8898C8;margin:4px 0 0'>Segments auto-detected from raw upload — no segment files needed</p>
    </div>""", unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("ATU Unique HCPs", atu["User Id"].nunique() if atu is not None else "—")
    c2.metric("PET Unique HCPs", pet["User Id"].nunique() if pet is not None else "—")
    overlap = len(set(atu["User Id"])&set(pet["User Id"])) if (atu is not None and pet is not None) else 0
    c3.metric("Overlap HCPs", overlap)
    c4.metric("ATU Quarters", ", ".join(sorted(atu["Quarter"].dropna().unique())) if atu is not None and "Quarter" in atu else "—")

    col1,col2 = st.columns(2)
    with col1:
        vc = pd.Series(eng.usage_seg).value_counts()
        st.plotly_chart(donut(vc.values.tolist(), vc.index.tolist(),
                              "Usage Segments (auto-detected)"), use_container_width=True)
    with col2:
        if atu is not None and "Target_Type" in atu.columns:
            tt = atu["Target_Type"].value_counts()
            st.plotly_chart(donut(tt.values.tolist(), tt.index.tolist(), "ATU Target Type"),
                            use_container_width=True)
    st.markdown("""<div class='insight'>
        <b>How segments are auto-detected from raw files:</b><br>
        <b>High Product Glioma Usage</b> — Q2.20 familiarity=5 (used it) + above-median patient load in Q3.60a<br>
        <b>Low Product Glioma Usage</b> — familiarity=4-5 but low/zero patients<br>
        <b>Non Product Glioma User</b> — familiarity &le;3 (not planning / not familiar)<br>
        <b>Rep Interaction / No Interaction</b> — ATU HCP presence in PET respondent list<br>
        <b>ATU+PET Cross</b> — Usage tier crossed with PET LTIP score (Q3.35 &ge;6 = high perception)
    </div>""", unsafe_allow_html=True)

def view_seg_dash(eng):
    st.markdown("## Segment Dashboard")
    sb = st.sidebar
    stype = sb.selectbox("Segment Type", [
        "Usage (High/Low/Non)", "Rep Interaction", "ATU+PET Cross"])
    col_map = {"Usage (High/Low/Non)":"Seg_Usage",
               "Rep Interaction":"Seg_Rep","ATU+PET Cross":"Seg_Cross"}
    scol = col_map[stype]

    df = eng.atu_df
    if df is None: st.info("Upload ATU file."); return
    all_segs = ["All"] + sorted(df[scol].dropna().unique().tolist()) if scol in df.columns else ["All"]
    chosen = sb.selectbox("Select Segment Value", all_segs)

    filt = eng.filter(scol, chosen)
    n = filt["User Id"].nunique()
    uid_set = set(filt["User Id"].unique())
    st.markdown(f"### {pill(chosen) if chosen!='All' else '<b>All HCPs</b>'} &nbsp; n={n}", unsafe_allow_html=True)

    tabs = st.tabs(["Q3.110 Attribute Importance","Q3.120 Product Ratings",
                    "All Questions Explorer","PET Rep Metrics"])

    with tabs[0]:
        q = eng.q110(uid_set)
        if len(q):
            adj = q[q["Attribute"].str.contains("Adjuvant",case=False,na=False)].copy()
            fl  = q[~q["Attribute"].str.contains("Adjuvant",case=False,na=False)].copy()
            clean = lambda s: re.sub(r"^(adjuvant|first.?line)\s+treatment\s*","",s,flags=re.IGNORECASE).strip() or s[:40]
            for title, sub, clr in [("Adjuvant",adj,"#C8102E"),("First-Line",fl,"#00B4B4")]:
                if len(sub):
                    sub["Label"] = sub["Attribute"].apply(clean)
                    st.plotly_chart(hbar(sub["Label"].tolist(), sub["% Rating 6-7"].tolist(),
                                        f"{title} — % Rating 6-7", clr, n), use_container_width=True)
            st.dataframe(q[["Attribute","% Rating 6-7","Mean Score","n"]], use_container_width=True)
        else:
            st.info("Q3.110 data not found for this segment.")

    with tabs[1]:
        q = eng.q120(uid_set)
        if len(q):
            def prod_g(s):
                sl = s.lower()
                if "product glioma" in sl: return "Product Glioma"
                if "temozolomide" in sl or "temodar" in sl: return "Temozolomide+RT"
                return "Radiation Alone"
            q["Product"] = q["Attribute"].apply(prod_g)
            clr_map = {"Product Glioma":"#C8102E","Temozolomide+RT":"#00B4B4","Radiation Alone":"#8898C8"}
            for prod,grp in q.groupby("Product"):
                clean_lbl = grp["Attribute"].str.replace(prod,"",case=False,regex=False).str.strip()
                st.plotly_chart(hbar(clean_lbl.tolist(), grp["% Rating 6-7"].tolist(),
                                     f"{prod} — % Rating 6-7", clr_map.get(prod,"#C8102E"), n),
                                use_container_width=True)
        else:
            st.info("Q3.120 data not found.")

    with tabs[2]:
        src = st.radio("Source", ["ATU","PET"], horizontal=True) if eng.pet_df is not None else "ATU"
        u_set = uid_set if src=="ATU" else (set(eng.pet_df[eng.pet_df["User Id"].isin(uid_set)]["User Id"]) if eng.pet_df is not None else set())
        blks = eng.blocks(u_set, src.lower())
        if not blks: st.info("No question blocks detected.")
        for blk in blks:
            with st.expander(f"📌 {blk['title'][:80]}"):
                bdf = blk["df"]
                if len(bdf):
                    fig = go.Figure(go.Bar(y=bdf["Label"], x=bdf["PctHigh"], orientation="h",
                                          marker_color="#C8102E",
                                          text=bdf["PctHigh"].apply(lambda v:f"{v:.0f}%"),
                                          textposition="outside"))
                    fig.update_layout(**DARK, height=max(200,len(bdf)*22),
                                      title=dict(text=f"% Rating 6-7 | n={bdf['n'].iloc[0]}",
                                                 font=dict(size=12)))
                    st.plotly_chart(fig, use_container_width=True)
                    st.dataframe(bdf[["Label","PctHigh","Mean"]].rename(
                        columns={"PctHigh":"% Rating 6-7","Mean":"Mean Score"}), use_container_width=True)
                    csv = bdf.to_csv(index=False).encode()
                    st.download_button(f"⬇ {blk['tag']}",data=csv,
                                       file_name=f"{blk['tag']}.csv",mime="text/csv",
                                       key=f"dl_{blk['tag']}")

    with tabs[3]:
        if eng.pet_df is None: st.info("Upload PET file to see rep interaction metrics."); return
        pet_u = set(eng.pet_df[eng.pet_df["User Id"].isin(uid_set)]["User Id"])
        st.metric("PET respondents in segment", len(pet_u))
        for blk in eng.blocks(pet_u,"pet")[:8]:
            with st.expander(f"📡 {blk['title'][:80]}"):
                bdf = blk["df"]
                if len(bdf):
                    fig = go.Figure(go.Bar(y=bdf["Label"],x=bdf["PctHigh"],orientation="h",
                                          marker_color="#00B4B4",
                                          text=bdf["PctHigh"].apply(lambda v:f"{v:.0f}%"),
                                          textposition="outside"))
                    fig.update_layout(**DARK, height=max(200,len(bdf)*22))
                    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    csv_bytes,fname = eng.export_csv(scol,chosen)
    st.download_button("⬇ Export Workbook-Style CSV",data=csv_bytes,file_name=fname,mime="text/csv")

def view_compare(eng):
    st.markdown("## Segment Comparison — Q3.110 Attribute Importance")
    if eng.atu_df is None: st.info("Upload ATU file."); return
    scol = st.selectbox("Compare by", ["Seg_Usage","Seg_Rep","Seg_Cross"])
    segs = sorted(eng.atu_df[scol].dropna().unique().tolist()) if scol in eng.atu_df.columns else []
    if not segs: st.info("No segments found."); return

    all_q = {}
    for seg in segs:
        uid_set = set(eng.atu_df[eng.atu_df[scol]==seg]["User Id"])
        q = eng.q110(uid_set)
        if len(q):
            all_q[seg] = q.set_index("Attribute")["% Rating 6-7"]

    if not all_q: st.info("No Q3.110 data."); return
    comp = pd.DataFrame(all_q).fillna(0)
    comp = comp[~comp.index.duplicated()]
    comp.index = [re.sub(r"^(Adjuvant|First.?line) treatment\s*","",s,flags=re.IGNORECASE).strip() for s in comp.index]

    fig = go.Figure(go.Heatmap(
        z=comp.values, x=comp.columns.tolist(), y=comp.index.tolist(),
        colorscale=[[0,"#0D1B3E"],[.5,"#C8102E"],[1,"#FF9090"]],
        text=comp.values.round(0), texttemplate="%{text:.0f}%",
        textfont=dict(size=10), showscale=True))
    fig.update_layout(**DARK, height=max(420,len(comp)*20),
                      title=dict(text="Q3.110 % Rating 6-7 by Segment",font=dict(size=13)))
    st.plotly_chart(fig, use_container_width=True)

    attr = st.selectbox("Drill into attribute", comp.index.tolist())
    if attr:
        vals = comp.loc[attr]
        fig2 = go.Figure(go.Bar(
            x=vals.index, y=vals.values,
            marker_color=[SEG_COLORS.get(s,"#8898C8") for s in vals.index],
            text=[f"{v:.0f}%" for v in vals.values], textposition="outside"))
        fig2.update_layout(**DARK, height=300, title=dict(text=attr[:70],font=dict(size=12)))
        st.plotly_chart(fig2, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# CACHED PROJECT FILE LOADER
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_resource
def load_project():
    eng = Engine()
    for d in [Path("/mnt/project"), Path("."), Path("/home/claude/hcp_dashboard")]:
        try:
            a = d/"GLIOMA_ATU_Q126_Q226.xlsx"
            p = d/"GLIOMA_PET_Q425_Q126_Q226.xlsx"
            if a.exists():
                eng.load(open(a,"rb"), open(p,"rb") if p.exists() else None)
                break
        except Exception as e:
            eng.errors.append(str(e))
    return eng

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    sb = st.sidebar
    sb.markdown("""<div style="padding:14px 0 6px;text-align:center">
        <div style="font-family:DM Serif Display,serif;font-size:1.3rem;color:#F0F4FF">🧬 HCP Intel</div>
        <div style="color:#8898C8;font-size:.68rem;letter-spacing:.1em;text-transform:uppercase">
        Glioma Analytics</div></div>""", unsafe_allow_html=True)
    sb.markdown("---")
    sb.markdown("### Upload Raw Files")
    atu_file = sb.file_uploader("ATU Raw File (.xlsx)", type=["xlsx"], key="atu")
    pet_file = sb.file_uploader("PET Raw File (.xlsx, optional)", type=["xlsx"], key="pet")
    sb.markdown("---")
    view = sb.selectbox("View", ["Overview","Segment Dashboard","Segment Comparison"])
    sb.markdown("---")
    sb.markdown("""<div style="color:#8898C8;font-size:.68rem">
        <b style="color:#F0F4FF">Glioma Program</b><br>
        Manufacturer Glioma Analytics<br>FY26 Q1-Q2</div>""", unsafe_allow_html=True)

    if atu_file:
        with st.spinner("Processing files & auto-detecting segments…"):
            eng = Engine()
            atu_file.seek(0)
            if pet_file: pet_file.seek(0)
            eng.load(atu_file, pet_file)
    else:
        eng = load_project()

    if eng.errors:
        with st.expander(f"Warnings ({len(eng.errors)})"):
            for e in eng.errors: st.warning(e)

    if eng.atu_df is None:
        st.markdown("""<div class="hero">
            <div class="badge">Ready</div>
            <h2 style="margin:0">Upload ATU raw file to begin</h2>
            <p style="color:#8898C8">Segments auto-detected — no segment files required</p>
        </div>""", unsafe_allow_html=True)
        return

    if view == "Overview": view_overview(eng)
    elif view == "Segment Dashboard": view_seg_dash(eng)
    elif view == "Segment Comparison": view_compare(eng)

if __name__ == "__main__":
    try:
        main()
    except Exception as _e:
        import traceback as _tb
        st.error(f"App error: {_e}")
        with st.expander("Traceback"): st.code(_tb.format_exc())
