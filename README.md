# UniCredit ECM Intelligence Platform - Streamlit MVP

## What this MVP does
- Product-based modules: ECM Cash, PCM, SES
- ECM Cash: ABB, Rights Issue, IPO scoring
- PCM: Fundraising Radar and Investor Matching
- SES: SSL Tracker plus LTIP / Derivatives preview
- Editable Threshold Module by product and GICS sector
- Excel upload for companies, investors and KPI settings
- AI Banker Copilot with fallback demo mode

## Run locally
```bash
cd "/Users/dogaerdal/Documents/Polimi/Classes/Finance Lab/unicredit_ecm_streamlit_mvp"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL shown by Streamlit, usually:
```text
http://localhost:8501
```

## Optional real AI integration
By default the AI Banker uses demo mode. To use OpenAI API:
```bash
export OPENAI_API_KEY="your_api_key_here"
streamlit run app.py
```

## Excel data model
The app can run with built-in dummy data or uploaded Excel files:
- `companies.xlsx`
- `investors.xlsx`
- `kpi_settings.xlsx`

You can download the full demo workbook directly from the Data Upload page.
# final threshold version
