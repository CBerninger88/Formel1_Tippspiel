from flask import Flask, request, jsonify, render_template
app = Flask(__name__)

# Speichert die Auswahlen
tippData = {
    "Christine": {},
    "Christoph": {}
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_selection')
def get_selection():
    name = request.args.get('name')
    city = request.args.get('city')
    if name in tippData and city in tippData[name]:
        return jsonify(tippData[name][city])
    return jsonify({"driver1": None, "driver2": None})

@app.route('/save_selection', methods=['POST'])
def save_selection():
    data = request.get_json()
    city = data['city']
    name = data['name']
    driver1 = data['driver1']
    driver2 = data['driver2']

    if name not in tippData:
        tippData[name] = {}
    tippData[name][city] = {"driver1": driver1, "driver2": driver2}
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True)
