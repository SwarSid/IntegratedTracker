# HCP Intelligence Platform
## VORANIGO® Glioma ATU + PET Integrated Analytics Dashboard

---

## Overview

This is a production-ready Streamlit analytics agent that:

1. **Ingests raw ATU (2 quarters) and PET (3 quarters) data** from uploaded Excel files
2. **Matches overlapping HCPs** across datasets using `User Id` as the primary key
3. **Enriches** matched records with Vora Usage segments, ATU+PET perception segments, and Rep interaction segments
4. **Classifies survey questions** autonomously into 13 semantic categories using content-driven pattern matching
5. **Delivers interactive executive dashboards** for temporal analysis, segment intelligence, and drill-down exploration

---

## File Structure

```
hcp_dashboard/
├── app.py              # Main Streamlit application (all-in-one)
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## Quick Start (Local)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run app.py

# 3. Open browser at http://localhost:8501
```

---

## Streamlit Cloud Deployment

1. Push to a GitHub repository
2. Go to https://share.streamlit.io
3. Click **New app** → select your repo → set `app.py` as the main file
4. Click **Deploy**

Note: For Streamlit Cloud deployment with project files baked in, update the paths in `load_project_files()` or use the "Upload Custom Files" mode in the sidebar.

---

## Input File Specifications

### ATU Raw File (2 quarters: Q1'26, Q2'26)
- **Format**: Excel (.xlsx)
- **Key columns**: `User Id`, `Quarter` (Unnamed col with Q1'26/Q2'26), `Target_Type` (On Target/Off target/Co-locs)
- **Header row**: Auto-detected (row 0 typical)

### PET Raw File (3 quarters: Q4'25, Q1'26, Q2'26)
- **Format**: Excel (.xlsx)
- **Key columns**: `User Id`, `Quarter` (Unnamed col), `Target_Type`
- **Header row**: Auto-detected (row 2 in current format, but agent auto-discovers)

### Segment Files (optional but recommended)
- `High_vs_Low_vs_No_User_ATU_PET_Segment.xlsx` — Vora Usage segments (High/Low/Non User) across waves
- `ATU_Usage_and_PET_Perception.xlsx` — Combined ATU+PET segments
- `Rep_Driven_Attributes_ATU.xlsx` — Rep interaction segments (High LTIP / No Interaction / Other)

**All segment files follow the standard 7-column format:**
`Id | Wave Number | Wave Id | User Id | User Type | Status | Segment Value`

---

## Key Features

### 1. Executive Overview
- Total HCP counts, overlap metrics, coverage percentages
- Quarter-level distribution charts (ATU × PET)
- VORANIGO usage segment donut chart
- Target type split

### 2. HCP Overlap Analysis
- Filterable table of all overlapping HCPs (ATU + PET matches)
- Temporal heatmap: which ATU quarter × PET quarter combinations exist
- Downloadable overlap CSV with enriched segment data

### 3. Segment Intelligence
- VORANIGO usage trends across waves (High/Low/Non User)
- ATU+PET combined perception segments
- Rep interaction LTIP segments
- Wave-by-wave breakdown matrix

### 4. Autonomous Question Classifier
- Upload any survey file or paste questions manually
- Auto-classifies into 13 semantic segments using regex pattern matching
- Shows confidence scores, matched patterns, distribution charts
- Export classified results as CSV or JSON
- Pre-loaded with ATU and PET survey question sets

### 5. Temporal Trends
- Target type evolution across quarters
- Segment drift across PET/ATU waves
- Quarter-pair overlap counts

### 6. Raw Data Explorer
- Browse any dataset with searchable columns
- Adjustable row preview
- CSV download of any filtered view

---

## Matching Logic

```python
# Core overlap detection
atu_ids = set(atu_df['User Id'].unique())
pet_ids = set(pet_df['User Id'].unique())
overlap_ids = atu_ids & pet_ids  # Set intersection

# Enrichment: for each overlapping HCP
# 1. Aggregate ATU quarters and responses
# 2. Aggregate PET quarters and responses
# 3. Join Vora Usage segment (most recent wave)
# 4. Join ATU+PET perception segment
# 5. Join Rep interaction segment
```

---

## Question Classifier Segments

| Segment | Key Patterns |
|---------|-------------|
| Screener & Eligibility | Board-certified, years of practice, IDH patient counts |
| Molecular Testing & Diagnostics | NGS, IHC, IDH testing, BRAF, MGMT, 1p/19q |
| Brand Awareness & Familiarity | VORANIGO, Temodar, ivosidenib, NCCN update |
| Treatment Patterns & Usage | Prescribing, adjuvant, line of therapy, GTR/STR |
| Product Perception & Attributes | PFS, OS, hepatic toxicity, LFT, seizure, fertility |
| Access, Reimbursement & Support | Insurance, copay, ServierONE, specialty pharmacy |
| Rep Interaction & Promotion | Sales rep, visual aids, message recall, online ads |
| Patient Behavior & Shared Decision | Patient inquiry, shared decision, patient preference |
| MRI & Disease Monitoring | MRI frequency, post-resection monitoring |
| Disease State Education | WHO classification, IDH wildtype vs mutant, glioma basics |
| Sources of Information | Journals, conferences, NCCN, UpToDate, social media |
| HCP Profiling & Demographics | Practice size, insurance mix, GPO, tumor board |

---

## Zero External API Dependencies
This application runs entirely on local compute with:
- **Pandas** for data manipulation
- **Streamlit** for the UI layer
- **Plotly** for interactive visualizations
- **openpyxl** for Excel file reading

No API keys, no cloud services, no costs.

---

## Future File Compatibility

The agent is format-resilient:
- **Header detection** is auto-discovered (not hardcoded to row index)
- **Column identification** uses semantic matching (looks for "User Id" anywhere)
- **Quarter detection** uses pattern matching on column values (Q1'26, Q2'26, etc.)
- **New segment files** with the standard 7-column format are auto-compatible

To support a new quarterly release, simply upload the new files — no code changes needed.
