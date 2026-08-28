# Airbnb Hotel Booking Analysis — Interactive Web App

This project converts the original `Airbnb_Hotel_Booking_Analysis.ipynb` analysis into an interactive Streamlit dashboard.

## Features

- Upload the Airbnb Excel/CSV dataset
- Apply neighbourhood and room-type filters
- View listing KPIs
- Room-type and neighbourhood analysis
- Average price analysis
- Construction year vs price
- Top hosts
- Host availability analysis
- Host verification and review analysis
- Price vs service fee correlation
- Correlation matrix
- View/download cleaned filtered data
- Conclusions and recommendations from the original notebook

## Files

- `app.py` — Streamlit web application
- `requirements.txt` — Python dependencies
- `Airbnb_Hotel_Booking_Analysis.ipynb` — original analysis notebook
- `Airbnb_Open_Data.xlsx` — place your dataset here if you want the app to load it automatically (or upload it through the sidebar)

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL shown by Streamlit.

## GitHub + Streamlit deployment

1. Upload `app.py`, `requirements.txt`, `README.md`, and the original `.ipynb` to your GitHub repository.
2. Deploy the repository using Streamlit Community Cloud.
3. Select `app.py` as the main file.
4. Share the generated web-app URL.

The dataset can be uploaded through the app if it is not committed to GitHub.
