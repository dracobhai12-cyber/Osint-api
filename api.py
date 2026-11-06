# save as api.py
# run: python api.py
# base: http://127.0.0.1:5000

from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# === DEV CREDIT ===
DEVELOPER = "t.me/optimusprime50"

# === KEYS (optional) ===
HITEK_TOKEN = os.getenv("HITEK_API_TOKEN", "")
HITECK_KEY  = os.getenv("HITECK_API_KEY", "")


# =========================================================
# AUTO-INJECT CREDIT INTO EVERY JSON RESPONSE
# =========================================================
def _add_credit(data):
    """Recursively add developer credit to dict responses."""
    if isinstance(data, dict):
        # Neeche se pehle add karo takki existing keys overwrite na ho
        data.setdefault("developer", DEVELOPER)
    return data


@app.after_request
def add_developer_credit(response):
    """
    Har response ke JSON body me 'developer' field inject karta hai.
    Agar response JSON hai to hi modify karega, warna chhod dega.
    """
    try:
        if response.is_json:
            data = response.get_json(silent=True)
            if isinstance(data, dict):
                data["developer"] = DEVELOPER
                response.set_data(jsonify(data).get_data())
            elif isinstance(data, list):
                # List of results — ek wrapper object me daal do
                wrapped = {"results": data, "developer": DEVELOPER}
                response.set_data(jsonify(wrapped).get_data())
    except Exception:
        pass  # Kabhi bhi response ko break na kare
    return response


# =========================================================
# ROUTES
# =========================================================
@app.route("/")
def home():
    return jsonify({
        "status": "online",
        "developer": DEVELOPER,
        "endpoints": {
            "/hitek?number=XXXXXXXXXX": "Hitek mobile lookup",
            "/hiteck?email=xxx@domain.com": "HiTeck email lookup",
            "/insta?username=xxx": "InstaNum username",
            "/insta?phone=xxxxxxxxxx": "InstaNum phone",
            "/insta?email=xxx@domain.com": "InstaNum email",
            "/insta?name=FirstName": "InstaNum name",
            "/all?phone=xxxxxxxxxx": "Query all APIs at once (phone)",
            "/all?email=xxx@domain.com": "Query all APIs at once (email)"
        }
    })


@app.route("/hitek")
def hitek():
    number = request.args.get("number", "").strip()
    if not number or not number.isdigit() or not (10 <= len(number) <= 15):
        return jsonify({"status": "error", "message": "Valid 10-15 digit number required"}), 400
    headers = {}
    if HITEK_TOKEN:
        headers["Authorization"] = f"Bearer {HITEK_TOKEN}"
    try:
        r = requests.get(
            "https://buttukha596-hitekapi.hf.space/FetchData",
            params={"Number": number},
            headers=headers,
            timeout=30
        )
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/hiteck")
def hiteck():
    email = request.args.get("email", "").strip().lower()
    if not email or "@" not in email:
        return jsonify({"status": "error", "message": "Valid email required"}), 400
    try:
        r = requests.get(
            "https://hiteckgroup-hiteckgrouppp.hf.space/search",
            params={"key": HITECK_KEY, "email": email, "pretty": "true"},
            timeout=60
        )
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/insta")
def insta():
    params = {}
    for k in ("username", "phone", "email", "name", "limit"):
        v = request.args.get(k)
        if v:
            params[k] = v
    if not any(k in params for k in ("username", "phone", "email", "name")):
        return jsonify({"status": "error", "message": "Provide username / phone / email / name"}), 400
    try:
        r = requests.get(
            "https://bruhletme-instanum-api.hf.space/api",
            params=params,
            timeout=30
        )
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/all")
def all_sources():
    phone = request.args.get("phone", "").strip()
    email = request.args.get("email", "").strip().lower()
    result = {}

    if phone:
        headers = {}
        if HITEK_TOKEN:
            headers["Authorization"] = f"Bearer {HITEK_TOKEN}"
        try:
            r = requests.get(
                "https://buttukha596-hitekapi.hf.space/FetchData",
                params={"Number": phone},
                headers=headers,
                timeout=25
            )
            result["hitek"] = r.json()
        except Exception as e:
            result["hitek"] = {"error": str(e)}

        try:
            r = requests.get(
                "https://bruhletme-instanum-api.hf.space/api",
                params={"phone": phone, "limit": 10},
                timeout=25
            )
            result["insta"] = r.json()
        except Exception as e:
            result["insta"] = {"error": str(e)}

    if email:
        try:
            r = requests.get(
                "https://hiteckgroup-hiteckgrouppp.hf.space/search",
                params={"key": HITECK_KEY, "email": email, "pretty": "true"},
                timeout=50
            )
            result["hiteck"] = r.json()
        except Exception as e:
            result["hiteck"] = {"error": str(e)}

        try:
            r = requests.get(
                "https://bruhletme-instanum-api.hf.space/api",
                params={"email": email, "limit": 10},
                timeout=25
            )
            result["insta"] = r.json()
        except Exception as e:
            result["insta"] = {"error": str(e)}

    if not result:
        return jsonify({"status": "error", "message": "Provide phone or email"}), 400

    return jsonify(result)


if __name__ == "__main__":
    print("API live → http://127.0.0.1:5000")
    print(f"Developer credit: {DEVELOPER}")
    app.run(host="127.0.0.1", port=5000, debug=False)
