import requests
import json
from typing import Any, Literal

token = "ad8ea0426fda4a1cb6b3867248c67a54d6db333530b24ec68bd28d6ea42508a8"
headers = {
    "accept": "application/json",
    "token": token
}

# region: 市场代码
# financial_type: 金融类型
Region = Literal["HK", "SZ", "SH", "US", "SG", "JP"]
MarketType = Literal["stock", "forex", "indices", "crypto", "future", "fund"]


def get_market_list(region: Region, financial_type: MarketType, code: str) -> list[dict[str, Any]]:
    url = "https://api.itick.io/symbol/list"
    params = {
        "region": region.lower(),
        "type": financial_type,
        "code": code
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    return {
        "code": data[0]["c"],
        "name":data[0]["n"],
        "market_type":data[0]["t"],
        "exchange":data[0]["e"],
        "symbol":data[0]["s"]
    }