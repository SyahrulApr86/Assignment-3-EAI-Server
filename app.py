from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Definisi base URL untuk API eksternal
DOG_IMAGE_API = "https://dog.ceo/api/breeds/image/random"
JOKE_API = "https://official-joke-api.appspot.com/random_joke"
AGE_API = "https://api.agify.io"
GENDER_API = "https://api.genderize.io"
NATIONALITY_API = "https://api.nationalize.io"
ACTIVITY_API = "https://www.boredapi.com/api/activity"


@app.route('/api/user', methods=['POST'])
def get_user_info():
    data = request.json
    name = data.get('name')
    role = data.get('role')

    response = {
        "name": name,
        "image": requests.get(DOG_IMAGE_API).json().get('message', '-')
    }

    try:
        gender_response = requests.get(f"{GENDER_API}?name={name}").json()
        print("Gender API response:", gender_response)  # Debugging print statement
        # Adjusting logic based on actual response structure
        gender_data = gender_response.get('gender', '-') if isinstance(gender_response, dict) else '-'
        probability = gender_response.get('probability', 0) if isinstance(gender_response, dict) else 0

        if role == "guest":
            response.update({
                "age": requests.get(f"{AGE_API}?name={name}").json().get('age', '-'),
                "gender": gender_data,
                "id_country": max(requests.get(f"{NATIONALITY_API}?name={name}").json().get('country', []),
                                  key=lambda x: x['probability'], default={'country_id': '-'}).get('country_id')
            })
        elif role == "friend":
            response.update({
                "quote": get_joke(),
                "hobby": requests.get(ACTIVITY_API).json().get('activity', '-')
            })
        elif role == "inspector":
            response.update({
                "age": requests.get(f"{AGE_API}?name={name}").json().get('age', '-'),
                "gender": gender_data,
                "id_country": max(requests.get(f"{NATIONALITY_API}?name={name}").json().get('country', []),
                                  key=lambda x: x['probability'], default={'country_id': '-'}).get('country_id'),
                "quote": get_joke(),
                "hobby": requests.get(ACTIVITY_API).json().get('activity', '-')
            })
        else:
            response.update({"error": "Invalid role"})

    except Exception as e:
        print("Error processing API response:", e)
        response.update({"error": str(e)})
    return jsonify(response)


def get_joke():
    joke_data = requests.get(JOKE_API).json()
    return f"{joke_data.get('setup', '')} {joke_data.get('punchline', '')}"


if __name__ == '__main__':
    app.run(debug=True)
