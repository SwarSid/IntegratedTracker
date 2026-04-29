# HCP Intelligence Platform
## ATU + PET Integrated Analytics Dashboard

---

## ⚠️ Fixing "Main module does not exist" on Streamlit Cloud

This error means Streamlit Cloud cannot find `app.py`. Follow these steps exactly:

### Step 1: Repo structure must be FLAT
Your GitHub repository root must contain these files directly (NOT in a subfolder):
```
your-repo/
├── app.py              ← must be at ROOT
├── requirements.txt    ← must be at ROOT
├── README.md
└── .streamlit/
    └── config.toml
```

### Step 2: Streamlit Cloud app settings
In your Streamlit Cloud dashboard → App settings:
- **Repository:** `your-username/your-repo-name`
- **Branch:** `main`
- **Main file path:** `app.py`  ← must be exactly this, NOT `hcp_dashboard/app.py`

### Step 3: Verify files are committed
```bash
git add app.py requirements.txt README.md .streamlit/config.toml
git commit -m "Fix deployment structure"
git push origin main
```

### Step 4: Redeploy
In Streamlit Cloud, click **"Reboot app"** or delete and redeploy.

---

## Running Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Data Files
The app auto-detects project Excel files. If not found, use **"Upload Custom Files"** 
mode in the sidebar to upload:
- ATU Raw File (2 quarters: Q1'26, Q2'26)  
- PET Raw File (3 quarters: Q4'25, Q1'26, Q2'26)
- Segment files (optional)
