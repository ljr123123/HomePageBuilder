import requests

url = "https://api.itick.io/stock/kline?region=HK&code=700&kType=2&limit=10"

headers = {
"accept": "application/json",
"token": "ad8ea0426fda4a1cb6b3867248c67a54d6db333530b24ec68bd28d6ea42508a8"
}

response = requests.get(url, headers=headers)

print(response.text)

