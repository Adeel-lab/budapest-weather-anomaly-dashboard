# 🌦️ Budapest Weather Anomaly Dashboard

A live weather anomaly detection dashboard for Budapest, built with Python and Streamlit.  
It pulls **6+ years of hourly weather data** (2020–present) from the Open-Meteo API and flags statistically unusual weather events using **Z-score analysis**.

🔗 **[Live App →](https://your-app-url.streamlit.app)**  
*(Deploy to Streamlit Cloud and replace this link)*

---

## 📌 What It Does

- Pulls live hourly weather data for Budapest from the [Open-Meteo Archive API](https://open-meteo.com/)
- Computes **historical baselines** (mean + std) grouped by **Month × Hour** — 288 groups across 6 years
- Flags any hour where a variable deviates more than **±3 standard deviations** from its historical norm
- Displays a live dashboard with KPIs, temperature chart, anomaly table, and monthly breakdown

---

## 📊 Variables Monitored

| Variable | Unit |
|---|---|
| Temperature (2m) | °C |
| Relative Humidity (2m) | % |
| Precipitation | mm |
| Wind Speed (10m) | km/h |
| Apparent Temperature | °C |

---

## 🔍 Anomaly Detection Method — Z-Score

$$Z = \frac{X - \mu}{\sigma}$$

- **X** = actual observed value
- **μ** = historical mean for that Month + Hour group
- **σ** = historical std for that Month + Hour group
- A row is flagged as `is_anomaly = True` if **any** Z-score exceeds **±3**

This approach is context-aware — a 35°C reading in August is normal, but the same in January would be flagged immediately.

---

## 📈 Key Findings (2020–2026)

- **3.56% anomaly rate** — 1,964 anomalous hours out of 55,224 total
- **Precipitation** drives 61.4% of all anomalies
- **November** is the most anomalous month (203 anomalies)
- **Temperature** is the most stable variable (only 2.4% of anomalies)

---

## 🚀 Run Locally

```bash
git clone https://github.com/Adeel-lab/budapest-weather-anomaly-dashboard.git
cd budapest-weather-anomaly-dashboard
pip install -r requirements.txt
streamlit run app.py
```

---

## ☁️ Deploy to Streamlit Cloud (Free)

1. Fork this repo
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo and set `app.py` as the entry point
4. Click Deploy — live URL in ~2 minutes

---

## 📦 Requirements
streamlit
openmeteo-requests
requests-cache
retry-requests
pandas
numpy


---

## 📁 Project Structure


budapest-weather-anomaly-dashboard/
│
├── app.py # Streamlit dashboard
├── Budapest_Weather_Anomaly_Detection.ipynb # Full analysis notebook
├── requirements.txt # Dependencies
└── README.md


---

## 👤 Author

**Adeel Kamal**  
[GitHub](https://github.com/Adeel-lab)
