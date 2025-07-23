# 🛢️ Well Log Analyzer (Streamlit App)

**A powerful Streamlit-based web app to visualize, analyze, and interpret digital well log data from LAS files with porosity calculations, hydrocarbon detection, crossplots, and triple combo plots.**

---

## 🚀 Features

- ✅ Upload & parse LAS well log files
- 📈 Interactive log plotting (depth vs log curves)
- 🧮 Density porosity calculator (from RHOB/RHOP)
- 🛢️ Hydrocarbon zone detection using GR and NPHI
- 📍 Crossplots (e.g., RHOB vs NPHI with depth gradient)
- 📊 Triple combo track (GR + Resistivity + Porosity logs)
- 📤 Export processed results to Excel
- 🌐 Streamlit-powered responsive interface

---

## 📂 How to Run Locally

```bash
git clone https://github.com/yourusername/well-log-analyzer.git
cd well-log-analyzer

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Launch the app
streamlit run app.py
```

---

## 📁 Folder Structure

```
📁 well-log-analyzer/
├── app.py                # Main Streamlit app
├── sample.las            # Sample LAS file for testing
├── requirements.txt      # Required Python packages
└── results/              # Auto-created for Excel exports
```

---

## 🛠️ Dependencies

- `streamlit`
- `lasio`
- `pandas`
- `matplotlib`
- `openpyxl` (for Excel export)

Install all using:

```bash
pip install -r requirements.txt
```

---

## 🧠 Future Additions

- [ ] Archie’s Equation Sw calculator
- [ ] Water saturation maps
- [ ] Zone-wise lithology flags
- [ ] PDF report generator

---

## 🧑‍💻 Author

**Harsh Raj**  
BTech, Petroleum Engineering, IIT(ISM) Dhanbad  
Website Link : https://rharsh9162-well-log-analyzer-app-goa7s3.streamlit.app/

---

## 📄 License

This project is licensed under the MIT License.
