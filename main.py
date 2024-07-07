import json
import requests


def alert(bot_token, channel_id):
    response = requests.post(
        url='https://api.nobitex.ir/market/stats',
        json={"srcCurrency": "usdt", "dstCurrency": "rls"}
    )
    if response.status_code != 200:
        return
    response = json.loads(response.content.decode('utf-8'))
    price = response['stats']['usdt-rls']['latest'][:-1]

    requests.post(
        url=f'https://api.telegram.org/bot{bot_token}/sendMessage',
        data={'chat_id': channel_id, 'text': f'{price} تومان '}
    )


if __name__ == "__main__":
    import os
    bot_token = os.getenv('BOT_TOKEN')
    channel_id = os.getenv('CHANNEL_ID')
    alert(bot_token, channel_id)
