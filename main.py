import requests


english_to_persian_dict = {
    '0': '۰',
    '1': '۱',
    '2': '۲',
    '3': '۳',
    '4': '۴',
    '5': '۵',
    '6': '۶',
    '7': '۷',
    '8': '۸',
    '9': '۹'
}

LATEST_PRICE_KEY = 'LATEST_PRICE'


def set_latest_price(price: int):
    with open(os.getenv('GITHUB_ENV'), 'a') as f:
        f.write(f"{LATEST_PRICE_KEY}={price}\n")


def get_latest_price():
    try:
        price = os.getenv(LATEST_PRICE_KEY)
        if price is None:
            return None
        return int(price)
    except ValueError:
        return None


def get_price(url, method_name='get', payload=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                response = getattr(requests, method_name)(
                    url,
                    json=payload
                )
                response.raise_for_status()
            except:
                return None
            try:
                return func(*args, **kwargs, response=response.json())
            except (KeyError, ValueError):
                return None
        return wrapper
    return decorator


@get_price('https://api.nobitex.ir/market/stats', method_name='post',
           payload={"srcCurrency": "usdt", "dstCurrency": "rls"})
def get_nobitex_price(response):
    price = response['stats']['usdt-rls']['latest'][:-1]
    return int(price)


@get_price('https://api.wallex.ir/v1/trades?symbol=USDTTMN')
def get_wallex_price(response):
    price = response['result']['latestTrades'][0]['price']
    return int(float(price))


@get_price('https://api.bitpin.ir/v1/mkt/markets/')
def get_bitpin_price(response):
    price = None
    for market in response['results']:
        if market['code'] == 'USDT_IRT':
            price = market['price']
            break
    return int(price)


@get_price('https://market.tetherland.com/last_trades')
def get_tetherland_price(response):
    price = response['data'][0]['price']
    return int(price)


@get_price('https://api-web.tabdeal.org/r/plots/currency_prices/')
def get_tabdeal_price(response):
    price = response[1]['markets'][0]['price']
    return int(price)


def alert(bot_token, channel_id):
    prices = {
        'نوبیتکس': get_nobitex_price(),
        'والکس': get_wallex_price(),
        'بیت‌پین': get_bitpin_price(),
        'تترلند': get_tetherland_price(),
        'تبدیل': get_tabdeal_price(),
    }
    
    for key, value in prices.copy().items():
        if value is None:
            del prices[key]
    
    average_price = int(sum(prices.values())/ len(prices))
    
    latest_price = get_latest_price()
    average_emoji = ''
    if latest_price is not None:
        average_emoji = '🔴' if average_price < latest_price else '🟢'
    set_latest_price(average_price)
    
    postfixes = {
        'نوبیتکس': '',
        'والکس': '',
        'بیت‌پین': '',
        'تترلند': '',
        'تبدیل': '',
    }
    
    postfixes[min(prices, key=prices.get)] = '🔽'
    postfixes[max(prices, key=prices.get)] = '🔼'
    
    alert_text = '\n'.join(
        [f'*میانگین: {average_price} تومان* {average_emoji}', ''] +
        [f'{exchange_name}: {price} تومان {postfixes[exchange_name]}' for exchange_name, price in prices.items()]
    )
    
    for eng_digit, per_digit in english_to_persian_dict.items():
        alert_text = alert_text.replace(eng_digit, per_digit)

    requests.post(
        url=f'https://api.telegram.org/bot{bot_token}/sendMessage',
        data={'chat_id': channel_id, 'text': alert_text, 'parse_mode': 'markdown'}
    )


if __name__ == "__main__":
    import os
    bot_token = os.getenv('BOT_TOKEN')
    channel_id = os.getenv('CHANNEL_ID')
    alert(bot_token, channel_id)
