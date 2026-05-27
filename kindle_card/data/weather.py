import requests

def fetch(city: str = "Beijing") -> dict:
    """Fetch weather from wttr.in API."""
    try:
        resp = requests.get(
            f"https://wttr.in/{city}?format=j1",
            timeout=10,
            headers={"User-Agent": "kindle-desk-card"},
        )
        resp.raise_for_status()
        data = resp.json()

        current = data.get("current_condition", [{}])[0]
        forecast_raw = data.get("weather", [])

        forecast = []
        for day in forecast_raw[:3]:
            forecast.append({
                "date": day.get("date", ""),
                "high": day.get("maxtempC", "?"),
                "low": day.get("mintempC", "?"),
                "condition": day.get("hourly", [{}])[4].get("weatherDesc", [{}])[0].get("value", ""),
            })

        return {
            "city": city,
            "temp": current.get("temp_C", "--"),
            "condition": current.get("weatherDesc", [{}])[0].get("value", ""),
            "forecast": forecast,
        }
    except Exception as e:
        return {
            "city": city,
            "temp": "--",
            "condition": f"获取失败",
            "forecast": [],
        }
