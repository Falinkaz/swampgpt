import csv, json, os, time, re, requests
from flask import Flask, render_template, request, jsonify, session
from openai import OpenAI

application = Flask(__name__)
API_KEY = os.getenv('OPENAI_API_KEY')
if not API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables")

def remove_special_characters(text):
    return re.sub(r'【.*?】', '', text)
def extract_card_names(text):
    return re.findall(r'\*\*(.*?)\*\*', text)

def get_cards_from_csv(csv_filename):
    cards = []
    with open(csv_filename, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            cards.append(row['Card Name'])
    return cards

def get_card_image_url(card_name):
    try:
        formatted_card_name = requests.utils.quote(card_name)
        print(f"Requesting Scryfall API with card name: {formatted_card_name}")
        response = requests.get(f'https://api.scryfall.com/cards/named?exact={formatted_card_name}')
        print(response)
        response.raise_for_status()  # Raise an error for bad status codes
        card_data = response.json()

        # Check for 'card_faces' if the card has multiple faces
        if 'card_faces' in card_data:
            image_urls = [face['image_uris']['border_crop'] for face in card_data['card_faces'] if 'image_uris' in face]
            if image_urls:
                return image_urls  # Return list of URLs for each face
            else:
                print(f"No 'image_uris' found for card faces: {card_name}")
                return None
        elif 'image_uris' in card_data:
            return [card_data['image_uris']['border_crop']]  # Return single URL in a list
        else:
            print(f"No 'image_uris' found for card: {card_name}")
            print(f"Response from Scryfall: {card_data}")
            return None
    except requests.RequestException as e:
        print(f"Request error fetching data for card: {card_name}")
        print(f"Exception: {e}")
        return None
    except Exception as e:
        print(f"Error fetching data for card: {card_name}")
        print(f"Exception: {e}")
        return None


def generate_response_with_images(chatgpt_response):
    print("ChatGPT Response for Images:", chatgpt_response)  # Print input
    card_names = extract_card_names(chatgpt_response)
    print("Extracted Card Names:", card_names)  # Print extracted card names
    
    card_recommendations = re.findall(r'(\*\*.*?\*\*.*?)(?=\n|$)', chatgpt_response)
    print("Card Recommendations:", card_recommendations)  # Print card recommendations

    response_with_images = []

    for card_recommendation in card_recommendations:
        card_name = extract_card_names(card_recommendation)[0]  # Assuming there's only one card name per recommendation
        card_image_url = get_card_image_url(card_name)
        response_with_images.append({
            'card_name': card_name,
            'recommendation': card_recommendation,
            'image_url': card_image_url
        })
    
    print("Response with Images:", response_with_images)  # Print the final result
    return response_with_images


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
    print("Current Working Directory:", os.getcwd())
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
    selectedFormat = data.get('selectedFormat', 'Any')  # Retrieve the selected format from the session
    client = OpenAI(api_key=API_KEY)
    thread = client.beta.threads.create()

    messages = [{"role": "user", "content": "Provide recommendations of the same colors palette for " + str(selectedFormat) + " format. The user has in their deck (may or may not be a complete deck. DO not enclose these cards in **):"}]
    for card in selectedOptions:
        messages[0]["content"] += f' {card},'  # Appending each card to the content

    run = client.beta.threads.create_and_run(
    assistant_id="asst_L87PSj1oIRz5XIzBYkXA0fQJ",
    thread={"messages": messages}
    )


    run_status = client.beta.threads.runs.retrieve(
    thread_id=(run.thread_id),
    run_id=(run.id)
    )


    response_json = None  # Initialize response variable outside the loop
    while run_status.status != 'completed': # Poll for completion
        time.sleep(5)  # Poll every 5 seconds
        run_status = client.beta.threads.runs.retrieve(thread_id=run.thread_id, run_id=run.id)
    try:
        thread_messages = client.beta.threads.messages.list(run.thread_id)
        response = (thread_messages.data[0].content[0].text.value)
    except Exception as e:
        return("error: Invalid response")  # Return a generic error response

    if thread_messages:
        cleaned_response = str(remove_special_characters(response))
        print(type(cleaned_response))
        print(messages)
        print(selectedFormat)
        print(str(response))
        card_names = extract_card_names(response)
        print(str(card_names))
        card_image_urls = [get_card_image_url(card_name) for card_name in card_names]
        print(str(card_image_urls))
        response_with_images = generate_response_with_images(cleaned_response)
        print("Response with Images:", response_with_images)
        print(response_with_images)
        return jsonify({"response_with_images": response_with_images})
        

if __name__ == '__main__':
    application.run(debug=True, port=8004)



