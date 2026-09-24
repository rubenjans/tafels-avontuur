# 🚀 Tafels Avontuur

Een visueel Streamlit-spel waarmee kinderen de tafels van 0 tot en met 10 oefenen. Er is bewust geen klassement en er worden geen persoonsgegevens opgeslagen.

## Functies
- Selecteer één of meer tafels van 0 t/m 10
- Drie spelmodi: Rustig, Normaal en Tijdchallenge
- Score, XP, levens, streaks, badges en eindfeedback
- Willekeurige meerkeuzevragen
- Mobielvriendelijke interface

## Lokaal starten
```bash
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## Naar GitHub
```bash
git init
git add .
git commit -m "Eerste versie Tafels Avontuur"
git branch -M main
git remote add origin https://github.com/JOUW-GEBRUIKERSNAAM/tafels-avontuur.git
git push -u origin main
```

## Deployen op Streamlit Community Cloud
1. Maak op GitHub een repository `tafels-avontuur` en push deze bestanden.
2. Meld je aan bij Streamlit Community Cloud met GitHub.
3. Kies **Create app**.
4. Selecteer de repository, branch `main` en bestand `app.py`.
5. Klik op **Deploy**.

## Privacy
De voortgang blijft alleen in de actieve Streamlit-sessie. Er is geen database, login of klassement.
