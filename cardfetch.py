import requests
import csv
import time
from datetime import datetime
import codecs
import logging
from mtgsdk import Card as MTGCard, Set as MTGSet

# Set up logging
logging.basicConfig(filename='cardfetch.log', level=logging.INFO)

# Load all cards
all_cards = MTGCard.all()

# Checkpoint to resume from
start_index = 0

# Define chunk size and delay between chunks
chunk_size = 2500
delay_seconds = 0.1

# Load processed cards from file
try:
    with open('processed_cards.txt', 'r') as f:
        processed_cards = set(line.strip() for line in f)
except FileNotFoundError:
    processed_cards = set()

def save_to_csv(distinct_cards, csv_file_name):
    with open(csv_file_name, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['name', 'mana_cost', 'cmc', 'colors', 'type', 'supertypes', 'subtypes', 'text', 'power', 'toughness', 'loyalty', 'legalities']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for card in distinct_cards:
            writer.writerow({
                'name': card.name,
                'mana_cost': card.mana_cost,
                'cmc': card.cmc,
                'colors': ', '.join(card.colors) if card.colors else None,
                'type': card.type,
                'supertypes': ', '.join(card.supertypes) if card.supertypes else None,
                'subtypes': ', '.join(card.subtypes) if card.subtypes else None,
                'text': card.text,
                'power': card.power,
                'toughness': card.toughness,
                'loyalty': card.loyalty,
                'legalities': ', '.join(f"{k}: {v}" for d in card.legalities for k, v in d.items()) if card.legalities else None
            })

# Process cards in chunks
while start_index < len(all_cards):
    end_index = start_index + chunk_size
    chunk = all_cards[start_index:end_index]

    try:
        # Process and save progress
        distinct_cards = [card for card in chunk if card.name not in processed_cards]
        processed_cards.update(card.name for card in distinct_cards)

        # Print out the data being processed
        print(f'Processing cards from index {start_index} to {end_index}')
        for card in distinct_cards:
            print(f'Processing card: {card.name}')

        # Only save to CSV if there are distinct cards
        if distinct_cards:
            print(f'Number of distinct cards: {len(distinct_cards)}')  # Add this line
            csv_file_name = f"mtg_dataset_{start_index}_{end_index}.csv"
            save_to_csv(distinct_cards, csv_file_name)

        # Log progress
        logging.info(f'Successfully processed cards from index {start_index} to {end_index}')

        # Save processed cards to file
        with open('processed_cards.txt', 'w') as f:
            for card_name in processed_cards:
                f.write(f'{card_name}\n')

        start_index = end_index
    except Exception as e:
        logging.error(f'Error processing cards from index {start_index} to {end_index}: {e}')
        break

print("Processing complete!")  # This line should be outside the loop