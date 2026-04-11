from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

API_KEY = "39f975c0ce727af7dd78118571d13143"

@app.route('/weather', methods=['GET'])
def get_weather():
    city = request.args.get('city')
    
    if not city:
        return jsonify({"error": "City not provided"}), 400

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

    response = requests.get(url)
    data = response.json()

    if response.status_code != 200:
        return jsonify(data), response.status_code

    weather_data = {
        "city": data["name"],
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"]
    }

    return jsonify(weather_data)

if __name__ == '__main__':
    app.run(debug=True, port=8080)
