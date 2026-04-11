import os
import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Weather Forecasting API",
    description="Python FastAPI backend for weather forecasting using OpenWeatherMap",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5"


def check_api_key():
    if not OPENWEATHER_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="OPENWEATHER_API_KEY not configured. Please set it in environment secrets."
        )


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
    <head>
        <title>Weather Forecasting API</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; background: #f0f4f8; }
            h1 { color: #2d3748; }
            .card { background: white; border-radius: 12px; padding: 20px; margin: 15px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
            code { background: #e2e8f0; padding: 3px 8px; border-radius: 4px; font-family: monospace; }
            a { color: #3182ce; text-decoration: none; }
            a:hover { text-decoration: underline; }
            .badge { display: inline-block; background: #48bb78; color: white; padding: 2px 10px; border-radius: 20px; font-size: 13px; }
        </style>
    </head>
    <body>
        <h1>🌤️ Weather Forecasting API</h1>
        <div class="card">
            <p><span class="badge">LIVE</span> FastAPI Python Backend</p>
            <p>Yeh API Flutter ya kisi bhi frontend se connect ki ja sakti hai.</p>
        </div>
        <div class="card">
            <h2>Available Endpoints:</h2>
            <ul>
                <li><a href="/docs">/docs</a> — Interactive API documentation (Swagger UI)</li>
                <li><code>GET /weather/current?city=Delhi</code> — Current weather</li>
                <li><code>GET /weather/forecast?city=Mumbai</code> — 5-day forecast</li>
                <li><code>GET /weather/current?lat=28.6&lon=77.2</code> — By coordinates</li>
            </ul>
        </div>
        <div class="card">
            <h2>Flutter Integration:</h2>
            <p>Base URL: <code>https://[your-repl-domain]</code></p>
            <p>Example: <code>http.get('/weather/current?city=Delhi')</code></p>
        </div>
    </body>
    </html>
    """


@app.get("/weather/current")
async def get_current_weather(
    city: str = Query(None, description="City name (e.g., Delhi, Mumbai, London)"),
    lat: float = Query(None, description="Latitude"),
    lon: float = Query(None, description="Longitude"),
    units: str = Query("metric", description="Units: metric (Celsius), imperial (Fahrenheit), standard (Kelvin)")
):
    """
    Get current weather for a city or coordinates.
    
    - **city**: City name (e.g., Delhi, Mumbai, Karachi)
    - **lat/lon**: Latitude and Longitude (alternative to city name)
    - **units**: metric = Celsius, imperial = Fahrenheit
    """
    check_api_key()

    if not city and (lat is None or lon is None):
        raise HTTPException(status_code=400, detail="Provide either 'city' or both 'lat' and 'lon'")

    params = {
        "appid": OPENWEATHER_API_KEY,
        "units": units
    }

    if city:
        params["q"] = city
    else:
        params["lat"] = lat
        params["lon"] = lon

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/weather", params=params)

    if response.status_code == 401:
        raise HTTPException(status_code=401, detail="Invalid API key. Please check your OPENWEATHER_API_KEY.")
    elif response.status_code == 404:
        raise HTTPException(status_code=404, detail=f"City '{city}' not found.")
    elif response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Weather API error.")

    data = response.json()

    return {
        "city": data["name"],
        "country": data["sys"]["country"],
        "temperature": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "temp_min": data["main"]["temp_min"],
        "temp_max": data["main"]["temp_max"],
        "humidity": data["main"]["humidity"],
        "pressure": data["main"]["pressure"],
        "weather": data["weather"][0]["main"],
        "description": data["weather"][0]["description"],
        "icon": data["weather"][0]["icon"],
        "icon_url": f"https://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png",
        "wind_speed": data["wind"]["speed"],
        "wind_direction": data["wind"].get("deg", 0),
        "visibility": data.get("visibility", 0),
        "cloudiness": data["clouds"]["all"],
        "units": units,
        "timezone": data["timezone"],
        "sunrise": data["sys"]["sunrise"],
        "sunset": data["sys"]["sunset"]
    }


@app.get("/weather/forecast")
async def get_forecast(
    city: str = Query(None, description="City name"),
    lat: float = Query(None, description="Latitude"),
    lon: float = Query(None, description="Longitude"),
    units: str = Query("metric", description="Units: metric, imperial, standard"),
    days: int = Query(5, ge=1, le=5, description="Number of forecast days (1-5)")
):
    """
    Get 5-day weather forecast (3-hour intervals).
    
    - **city**: City name (e.g., Delhi, Lahore, Dhaka)
    - **lat/lon**: Coordinates (alternative to city)
    - **units**: metric = Celsius
    - **days**: How many days of forecast (1-5)
    """
    check_api_key()

    if not city and (lat is None or lon is None):
        raise HTTPException(status_code=400, detail="Provide either 'city' or both 'lat' and 'lon'")

    params = {
        "appid": OPENWEATHER_API_KEY,
        "units": units,
        "cnt": days * 8
    }

    if city:
        params["q"] = city
    else:
        params["lat"] = lat
        params["lon"] = lon

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/forecast", params=params)

    if response.status_code == 401:
        raise HTTPException(status_code=401, detail="Invalid API key.")
    elif response.status_code == 404:
        raise HTTPException(status_code=404, detail=f"City '{city}' not found.")
    elif response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Weather API error.")

    data = response.json()

    forecasts = []
    for item in data["list"]:
        forecasts.append({
            "datetime": item["dt_txt"],
            "timestamp": item["dt"],
            "temperature": item["main"]["temp"],
            "feels_like": item["main"]["feels_like"],
            "temp_min": item["main"]["temp_min"],
            "temp_max": item["main"]["temp_max"],
            "humidity": item["main"]["humidity"],
            "weather": item["weather"][0]["main"],
            "description": item["weather"][0]["description"],
            "icon": item["weather"][0]["icon"],
            "icon_url": f"https://openweathermap.org/img/wn/{item['weather'][0]['icon']}@2x.png",
            "wind_speed": item["wind"]["speed"],
            "cloudiness": item["clouds"]["all"],
            "rain_probability": item.get("pop", 0) * 100
        })

    return {
        "city": data["city"]["name"],
        "country": data["city"]["country"],
        "units": units,
        "forecast_count": len(forecasts),
        "forecasts": forecasts
    }


@app.get("/weather/cities")
async def search_cities(
    q: str = Query(..., min_length=2, description="City name to search"),
    units: str = Query("metric", description="Units")
):
    """
    Search weather by partial city name.
    Returns current weather for the best matching city.
    """
    check_api_key()

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/weather", params={
            "q": q,
            "appid": OPENWEATHER_API_KEY,
            "units": units
        })

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail=f"No city found matching '{q}'")
    elif response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Search error.")

    data = response.json()
    return {
        "city": data["name"],
        "country": data["sys"]["country"],
        "lat": data["coord"]["lat"],
        "lon": data["coord"]["lon"],
        "temperature": data["main"]["temp"],
        "weather": data["weather"][0]["main"],
        "description": data["weather"][0]["description"],
        "icon_url": f"https://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
