import json
import logging
from curl_cffi import requests
from bs4 import BeautifulSoup
from celery import shared_task
from playwright.sync_api import sync_playwright
from django.utils import timezone
from django.conf import settings
from .models import Target, PriceHistory

logger = logging.getLogger(__name__)

def send_telegram_notification(chat_id, title, url, current_price, target_price):
    token = settings.TELEGRAM_BOT_TOKEN
    if not token or not chat_id:
        return False

    api_url=f'https://api.telegram.org/bot{token}/sendMessage'

    text = (
        f"🔥 **Price lowered!**\n\n"
        f"📦 **Item:** <a href='{url}'>{title or 'Item URL'}</a>\n"
        f"💰 **Current price:** {current_price}\n"
        f"🎯 **Your target:** {target_price}\n\n"
        f"⚡ <i>Hurry up! Buy it before price goes up again!</i>"
    )

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }

    try:
        response = requests.post(api_url, json=payload, timeout=5)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Failde to send Telegram alert: {e}")
        return False

def fetch_html_with_playwright(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )

        page = context.new_page()
        try:
            page.goto(url, timeout=30000, wait_until='domcontentloaded')
            page.wait_for_timeout(2000)

            html = page.content()
        except Exception as e:
            logger.error(f"Playwright timeout/error for {url}: {e}")
            html = ""
        finally:
            browser.close()

        return html

@shared_task
def parse_target_price(target_id):
    try:
        target = Target.objects.get(id=target_id)
    except Target.DoesNotExist:
        return f"Target {target_id} not found."

    html_content = fetch_html_with_playwright(target.url)

    if not html_content:
        return f"Could not fetch HTML for Target #{target.id}"

    soup = BeautifulSoup(html_content, 'html.parser')
    
    
#     # headers = {
#     #     'User_Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
#     #     }
    
#     try: 
#         response = requests.get(target.url, impersonate="chrome120", timeout=15)
#         response.raise_for_status()
#     except requests.RequestException as e:
#         return f"Error Fetching {target.url}: {str(e)}"
    
    soup = BeautifulSoup(html_content, 'html.parser')

    if not target.title:
        title_tag = soup.find('title')
        if title_tag:
            target.title = title_tag.text.strip()[:255]
    
    price = None
#     parsing_method = None

# # Parsing stage 1: JSON-LD

    scripts = soup.find_all('script', type='application/ld+json')
    for script in scripts:
        try:
            data = json.loads(script.string, strict=False)
            items = data if isinstance(data, list) else data.get('@graph', [data])
            for item in items:
                if item.get('@type') == 'Product':
                    offers = item.get('offers', {})
                    if isinstance(offers, list) and len(offers) > 0:
                        offers = offers[0]
                    parsed_price = offers.get('price')
                    if parsed_price:
                        price = float(parsed_price)
                        parsing_method = "JSON_LD"
                        logger.info(f"[Target #{target.id} Price was found with {parsing_method}]")
                        break
        except Exception:
            continue
        if price:
            break

# # Parsing stage 2: Beautifulsoup

#     if not price:

#         meta_tags = [
#             {'property': 'product:price:amount'},
#             {'itemprop': 'price'},
#             {'property': 'og:price:amount'}
#         ]

#         for tag_attrs in meta_tags:
#             meta_price = soup.find('meta', tag_attrs)
#             if meta_price and meta_price.get('content'):
#                 try:
#                     price = float(meta_price['content'].replace(',', '.'))
#                     parsing_method = f"Meta ({list(tag_attrs.values())[0]})"
#                     logger.info(f"[Target #{target.id} Price was found with {parsing_method}]")
#                     break
#                 except ValueError:
#                     continue
             

    
#         # if meta_price and meta_price.get('content'):
#         #     try:
#         #         price = float(meta_price['content'].replace(',', '.'))
#         #         parsing_method = "Meta/OpenGraph"
#         #         logger.info(f"[Target #{target.id} Price was found with {parsing_method}]")
#         #     except ValueError:
#         #         pass

# # Parsing stage 3: Regex
            
#     if not price:
#         price_elements = soup.find_all(re.compile(r'^(span|div|p|h[1-6])$'), class_=re.compile(r'(price|cost|val)', re.I))

#         stop_words = ['delivery', 'credit', 'month', 'installment', 'part', 'shipping', 'old', 'prev', 'base', 'regular']

#         potential_prices = []

#         for el in price_elements:
#             if el.find(class_=re.compile(r'(price|cost|val)', re.I)):
#                 continue

#             if el.name in ['del', 's', 'strike'] or el.find_parent(['del', 's', 'strike']):
#                 continue

#             classes = " ".join(el.get('class', [])).lower()
#             if any(word in classes for word in stop_words):
#                 continue

#             match = re.search(r'(\d+[\d\s\xa0]*[,.]?\d*)', el.text)
#             if match:
#                 clean_num = match.group(1).replace(' ', '').replace(',', '.')
#                 try:
#                     found_price = float(clean_num)
#                     if found_price > 0:
#                         potential_prices.append(found_price)
#                 except ValueError:
#                     continue

#         if potential_prices:
#             top_prices = potential_prices[:5]
#             max_found = max(top_prices)

#             valid_prices = [p for p in top_prices if p >= max_found * 0.3]

#             if valid_prices:
#                 price = min(valid_prices)
#                 parsing_method = "Universal Smart Regex"
#                 logger.info(f"[Target #{target.id} Price was found with {parsing_method}]")

    if price:
        logger.info(f"[Target #{target.id} successfully updated: {price} (via {parsing_method})]")
        old_price = target.current_price
        target.current_price = price
        target.save(update_fields=['title', 'current_price', 'updated_at'])

        PriceHistory.objects.create(
            target=target,
            price=price
        )

        if price <= target.target_price:
            chat_id = None
            if target.user and hasattr(target.user, 'profile') and target.user.profile.telegram_chat_id:
                chat_id = target.user.profile.telegram_chat_id
            elif target.telegram_chat_id:
                chat_id = target.telegram_chat_id

            if chat_id:
                send_telegram_notification(
                    chat_id=target.telegram_chat_id,
                    title=target.title,
                    url=target.url,
                    current_price=price,
                    target_price=target.target_price
                )

        return f"SuccessFully updated Target #{target.id}: new price is {price}"
    
    if target.title:
        target.save(update_fields=['title', 'updated_at'])

    return f"Could not extract price for Target #{target.id}"

@shared_task
def check_all_active_targets():
    active_targets = Target.objects.filter(is_active=True)
    count = 0

    for target in active_targets:
        parse_target_price.delay(target.id)
        count += 1

    return f"Dispatched {count} active targets for price checking."