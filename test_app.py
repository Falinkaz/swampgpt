import pytest, os
from project import get_cards_from_csv, index, autocomplete, app, log_selected_options


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client



def test_get_cards_from_csv():
    #calling the same file used in the code
    csv_filename = 'allcardsv3.csv'

    #call the funcion with the parth to file:
    cards = get_cards_from_csv(csv_filename)

    assert cards

    assert len(cards) > 27045

    assert "Annul" in cards
    assert "Counterspell" in cards
    assert "A-Base Camp" in cards


def test_index(client):
    response = client.get('/')
    assert response.status_code == 200


def test_autocomplete(client):
    response = client.get('/autocomplete?q=card')
    assert response.status_code == 200

def test_log_selected_options(client):
    data = {'selected options': ['Annul', 'Counterspell']}
    response = client.post('/log_selected_options', json=data)
    assert response.status_code ==204

def test_send_gpt(client):
    data = {'selected options': ['Annul', 'Counterspell']}
    response = client.post('/send_gpt', json=data)
    assert response.status_code == 200
    json_data = response.get_json()
    assert isinstance(json_data['recommendations'], dict)
