import requests


def get_price(url, method_name='get', payload=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            response = getattr(requests, method_name)(
                url,
                json=payload
            )
            if response.status_code != 200:
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


@get_price('https://api.tetherland.com/currencies')
def get_tetherland_price(response):
    price = response['data']['currencies']['USDT']['price']
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
    
    for key, value in prices.items():
        if value is None:
            del prices[key]
            
    average_price = int(sum(prices.values())/ len(prices))
    
    alert_text = '\n'.join(
        [f'*میانگین: {average_price} تومان*', ''] +
        [f'{exchange_name}: {price} تومان' for exchange_name, price in prices.items()]
    )

    requests.post(
        url=f'https://api.telegram.org/bot{bot_token}/sendMessage',
        data={'chat_id': channel_id, 'text': alert_text, 'parse_mode': 'markdown'}
    )


if __name__ == "__main__":
    import os
    bot_token = os.getenv('BOT_TOKEN')
    channel_id = os.getenv('CHANNEL_ID')
    alert(bot_token, channel_id)
