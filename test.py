import requests

telegram_token = "6728316261:AAHRd_lopYRyqKtVWvyW-ACtgnj1ptB1UO0"

telegram_api_url = f'https://api.telegram.org/bot{telegram_token}/sendMessage'

def send_telegram_message(chat_id, message):
    """
    Function to send a message to the Telegram Bot API.
    """
    params = {
        'chat_id': chat_id,
        'text': message
    }
    response = requests.post(telegram_api_url, params=params)
    print(response)
    return response.json()


response = send_telegram_message(2062580383, "Krish")
print(response)
