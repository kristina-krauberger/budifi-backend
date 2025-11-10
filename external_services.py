"""
https://corrently.io/books/marktdaten-strompreis/page/sondernutzung-individuelle-marktpreise
Daten die ich brauche:
- Postleitzahl → um local_price abzufragen
- Haushaltsgröße: wie viele Personen im Haushalt? - 900 kWh /im Jahr
- Monatliche Zahlung
- (Optional - Anbietername)
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN_CORRENTLY")

base_url = "https://api.corrently.io/v2.0/gsi/marketdata"
params = {
    "zip": "10969",
    "token": API_TOKEN
}
headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {API_TOKEN}"
}


response = requests.get(base_url, params=params, headers=headers)
print(response.json())
