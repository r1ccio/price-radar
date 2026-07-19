import re
from curl_cffi import requests
from bs4 import BeautifulSoup
from celery import shared_task
from django.utils import timezone
from .models import Target, PriceHistory

@shared_task
def parse_target_price(target_id):
    try:
        target = Target.objects.get(id=target_id)
    except Target.DoesNotExist:
        return f"Target {target_id} not found."
    
    # headers = {
    #     'User_Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    #     }
    
    try: 
        response = requests.get(target.url, impersonate="chrome120", timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"Error Fetching {target.url}: {str(e)}"
    
    soup = BeautifulSoup(response.text, 'html.parser')

    if not target.title:
        title_tag = soup.find('title')
        if title_tag:
            target.title = title_tag.text.strip()[:255]
    
    price = None

    meta_price = soup.find('meta', {'property': 'product:price:amount'}) or \
                 soup.find('meta', {'itemprop': 'price'})
    
    if meta_price and meta_price.get('content'):
        try:
            price = float(meta_price['content'].replace(',', '.'))
        except ValueError:
            pass

    if not price:
        price_elements = soup.find_all(re.compile(r'^(span|div|p|h[1-6])$'), class_=re.compile(r'(price|cost|val)', re.I))
        for el in price_elements:
            match = re.search(r'(\d+[\d\s]*[,.]?\d*)', el.text)
            if match:
                clean_num = match.group(1).replace(' ', '').replace(',', '.')
                try:
                    price = float(clean_num)
                    if price > 0:
                        break
                except ValueError:
                    continue

    if price:
        target.current_price = price
        target.save(update_fields=['title', 'current_price', 'updated_at'])

        PriceHistory.objects.create(
            target=target,
            price=price
        )
        return f"SuccessFully updated Target #{target.id}: new price is {price}"
    
    if target.title:
        target.save(update_fields=['title', 'updated_at'])

    return f"Could not extract price for Target #{target.id}"
