import csv, openai, json
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from config import api_key


application = Flask(__name__)


def get_cards_from_csv(csv_filename):
    cards = []
    with open(csv_filename, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            cards.append(row['Card Name'])
    return cards

@application.route('/')
def index():
    cards = []
    return render_template('index.html', cards=cards)

@application.route('/autocomplete')
def autocomplete():
    query = request.args.get('q', '').lower()
    csv_filename = 'allcardsv3.csv'
    cards = get_cards_from_csv(csv_filename)
    suggestions = [card for card in cards if query in card.lower()]
    return jsonify(suggestions)

@application.route('/log_selected_options', methods=['POST'])
def log_selected_options():
    data = request.get_json()
    selectedOptions = data.get('selectedOptions')
    print("selectedOptions:", selectedOptions)
    return '', 204


@application.route('/send_gpt', methods=['POST'])
def send_gpt():
    data = request.get_json()
    selectedOptions = data.get('selectedOptions', [])
    client = OpenAI(api_key=api_key)
    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "Do not include any explanations, only provide an RFC8259 compliant JSON response following a dict class format without deviation. Always use "'cards'" as the value for the dict key, and fill out each value with either a card name, or a "'substitute X with Y'" statement You are a gen-Z Magic The Gathering player. Your mission is to provide a list of cards that should accompany a player's deck based on the cards that they already have in theirs. In the case that a card should be substituted by another card, you will mention: 'Substitute X wqith Y'. If not, only mention the new card that should be added. Do not include card commentary (except if it is a card that should substitute an existing one in the player's deck). Stick to a list of cards (and the substitute comentary if applicable) and format it as a python list. For each card that was provided by the user as input, analyze all existing MTG cards and ONLY in case there is a card that either has a lower mana cost or an added playing value (as long as the mana value is the same or less than that of the substituted card), propose the better card as a substitute in all cases. You should never recommend a card that has already been provided as part of an existing deck. Consider the most recent MTG expansions by surfing the web. NEVER RECOMMEND TO SUBSTITUTE A CARD WITH ANOTHER THAT HAS A HIGHER MANA COST"},
        {"role": "user", "content": "The player currently has in their deck: " + str(selectedOptions)}
    ]
    )
    content = completion.choices[0].message.content
    try:
        json_response = json.loads(content)
        print(json_response)
        print(type(json_response))
        return jsonify({"recommendations": json_response})
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return jsonify({"recommendations": []})  # Empty list as a default

if __name__ == '__main__':
    application.run(debug=True, port=8004)



