import logging
import re
import unicodedata
from decimal import Decimal, InvalidOperation
from difflib import SequenceMatcher
from urllib.parse import urlencode

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


logger = logging.getLogger(__name__)

DEFAULT_MAX_PRODUCTS = 5
WAIT_TIMEOUT = 12
MAX_QUERY_LENGTH = 120
MIN_RELEVANCE_SCORE = 0.35
ACCESSORY_TOKENS = {
    "adaptör",
    "askı",
    "kablo",
    "kapak",
    "kılıf",
    "koruyucu",
    "stand",
    "şarj",
}

# Hem "1.249,90 TL" hem "1249 TL" hem de "1.249 ₺" biçimlerini yakalar.
PRICE_PATTERN = re.compile(
    r"(?P<amount>(?:\d{1,3}(?:[.\s]\d{3})+|\d+)(?:,\d{1,2})?)\s*(?:TL|₺)",
    re.IGNORECASE,
)


def create_driver():
    """Uygulamanın her fiyat araması için güvenli bir Chrome oturumu oluşturur."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1440,1200")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(25)
    return driver


def normalize_text(value):
    """Karşılaştırma için metni Türkçe karakterlerden ve noktalama işaretlerinden arındırır."""
    if not value:
        return ""

    value = value.casefold().replace("ı", "i")
    value = unicodedata.normalize("NFKD", value)
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def calculate_relevance(query, title):
    """Arama ifadesi ile ürün başlığı arasında 0-1 arası uygunluk puanı üretir."""
    normalized_query = normalize_text(query)
    normalized_title = normalize_text(title)
    if not normalized_query or not normalized_title:
        return 0.0

    query_tokens = set(normalized_query.split())
    title_tokens = set(normalized_title.split())
    token_coverage = len(query_tokens & title_tokens) / len(query_tokens)
    text_similarity = SequenceMatcher(None, normalized_query, normalized_title).ratio()
    score = 1.0 if normalized_query in normalized_title else (
        (token_coverage * 0.75) + (text_similarity * 0.25)
    )

    # Kullanıcı aksesuar aramadıysa telefon kılıfı/kablosu gibi sonuçları geriye atar.
    normalized_accessories = {normalize_text(token) for token in ACCESSORY_TOKENS}
    query_has_accessory = any(
        token.startswith(accessory)
        for token in query_tokens
        for accessory in normalized_accessories
    )
    title_has_accessory = any(
        token.startswith(accessory)
        for token in title_tokens
        for accessory in normalized_accessories
    )
    if title_has_accessory and not query_has_accessory:
        score *= 0.25

    # 256 GB aramasında 128 GB gibi farklı kapasite sonuçlarını cezalandırır.
    storage_pattern = re.compile(r"\b\d+\s*(?:gb|tb)\b")
    query_storage = set(storage_pattern.findall(normalized_query))
    title_storage = set(storage_pattern.findall(normalized_title))
    if query_storage and title_storage and query_storage.isdisjoint(title_storage):
        score *= 0.45

    return round(score, 3)


def extract_price(text, prefer_last=False):
    """Fiyat metnini hem görüntülenecek metne hem sayısal değere dönüştürür."""
    # Amazon fiyatın tam ve kuruş kısmını ayrı satırlarda gösterebilir:
    # "42.999\n00 TL" -> "42.999,00 TL"
    text = re.sub(
        r"(?<=\d)\s+(?=\d{2}\s*(?:TL|₺))",
        ",",
        text or "",
        flags=re.IGNORECASE,
    )
    matches = list(PRICE_PATTERN.finditer(text))
    if not matches:
        return None, None

    match = matches[-1] if prefer_last else matches[0]

    raw_amount = match.group("amount").replace(" ", "")
    normalized_amount = raw_amount.replace(".", "").replace(",", ".")

    try:
        numeric_price = Decimal(normalized_amount)
    except InvalidOperation:
        return None, None

    display_price = f"{match.group('amount')} TL"
    return display_price, float(numeric_price)


def find_first_element(element, selectors):
    for selector in selectors:
        try:
            node = element.find_element(By.CSS_SELECTOR, selector)
            if node:
                return node
        except Exception:
            continue
    return None


def find_first_text(element, selectors):
    for selector in selectors:
        try:
            text = element.find_element(By.CSS_SELECTOR, selector).text.strip()
            if text:
                return text
        except Exception:
            continue
    return None


def find_first_attribute(element, selectors, attribute):
    for selector in selectors:
        try:
            node = element if selector is None else element.find_element(By.CSS_SELECTOR, selector)
            value = node.get_attribute(attribute)
            if value:
                return value.strip()
        except Exception:
            continue
    return None


def find_product_container(element, max_levels=6):
    """Bağlantıdan başlayıp ürün adı ve fiyatı içeren en yakın kapsayıcıya çıkar."""
    current = element
    best_candidate = element

    for _ in range(max_levels):
        try:
            current_text = current.text.strip()
            if current_text:
                best_candidate = current
                _, price_value = extract_price(current_text, prefer_last=True)
                if price_value is not None:
                    return current
            current = current.find_element(By.XPATH, "..")
        except Exception:
            break

    return best_candidate


def extract_price_from_selectors(element, selectors):
    """Seçicileri sırayla dener ve gerçekten fiyat içeren ilk alanı döndürür."""
    for selector in selectors:
        try:
            node = element.find_element(By.CSS_SELECTOR, selector)
            for candidate in (node.get_attribute("aria-label"), node.text):
                price_text, price_value = extract_price(candidate)
                if price_value is not None:
                    return price_text, price_value
        except Exception:
            continue

    return extract_price(element.text, prefer_last=True)


def extract_amazon_price(card):
    """Amazon'un aria-label veya ayrı tam/kuruş alanlarından fiyatı okur."""
    for selector in ("span.a-price span.a-offscreen", "span.a-price"):
        price_node = find_first_element(card, [selector])
        if not price_node:
            continue

        for attribute in ("aria-label", "textContent", "innerText"):
            price_text, price_value = extract_price(price_node.get_attribute(attribute))
            if price_value is not None:
                return price_text, price_value

    whole = find_first_attribute(card, [".a-price .a-price-whole"], "textContent")
    fraction = find_first_attribute(card, [".a-price .a-price-fraction"], "textContent")
    if whole:
        whole = re.sub(r"[^\d.]", "", whole)
        fraction = re.sub(r"\D", "", fraction or "00")[:2] or "00"
        price_text, price_value = extract_price(f"{whole},{fraction} TL")
        if price_value is not None:
            return price_text, price_value

    return extract_price(card.text, prefer_last=True)


def wait_for_cards(driver, selectors, timeout=WAIT_TIMEOUT):
    """Sabit süre beklemek yerine ilk çalışan ürün kartı seçicisini bekler."""
    def locate_cards(current_driver):
        for selector in selectors:
            cards = current_driver.find_elements(By.CSS_SELECTOR, selector)
            if cards:
                return cards
        return False

    return WebDriverWait(driver, timeout).until(locate_cards)


def build_result(site, query, title, price_text, price_value, url=None, image_url=None):
    relevance = calculate_relevance(query, title)
    return {
        # Eski arayüzle uyumluluk için bu üç alan korunuyor.
        "ad": title,
        "fiyat": price_text,
        "site": site,
        # Yeni alanlar sıralama, bağlantı ve daha doğru karşılaştırma için kullanılır.
        "title": title,
        "price": price_value,
        "currency": "TRY",
        "url": url,
        "image_url": image_url,
        "relevance_score": relevance,
    }


def sort_and_limit(results, max_products):
    # Önce sorguya en yakın ürünler, eşitlikte en ucuz ürün gösterilir.
    relevant_results = [
        result
        for result in results
        if result["relevance_score"] >= MIN_RELEVANCE_SCORE
    ]
    return sorted(
        relevant_results,
        key=lambda result: (-result["relevance_score"], result["price"]),
    )[:max_products]


def search_trendyol(driver, product_name, max_products=DEFAULT_MAX_PRODUCTS):
    query = urlencode({"q": product_name})
    driver.get(f"https://www.trendyol.com/sr?{query}")

    cards = wait_for_cards(
        driver,
        ["div.p-card-wrppr", "div[data-testid='product-card']", "a[href*='-p-']"],
    )

    results = []
    seen_urls = set()
    for card in cards:
        url = find_first_attribute(card, [None, "a[href*='-p-']"], "href")
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)

        title = (
            find_first_attribute(card, ["img"], "alt")
            or find_first_text(card, ["span.prdct-desc-cntnr-name", ".prdct-desc-cntnr"])
        )
        price_text, price_value = extract_price(card.text)
        image_url = find_first_attribute(card, ["img"], "src")

        if title and price_value is not None:
            results.append(
                build_result(
                    "Trendyol", product_name, title, price_text, price_value, url, image_url
                )
            )

    logger.info("Trendyol: %s geçerli ürün bulundu", len(results))
    return sort_and_limit(results, max_products)


def search_hepsiburada(driver, product_name, max_products=DEFAULT_MAX_PRODUCTS):
    query = urlencode({"q": product_name})
    driver.get(f"https://www.hepsiburada.com/ara?{query}")

    cards = wait_for_cards(
        driver,
        [
            "div[class*='productCardRoot']",
            "li[data-test-id='product-card-item']",
            "div[data-test-id='product-card']",
            "li[class*='productListContent']",
            "a[href*='-p-HB']",
            "a[href*='-p-']",
        ],
    )

    results = []
    seen_urls = set()
    for card in cards:
        url = find_first_attribute(card, [None, "a[href*='-p-']"], "href")
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)

        container = find_product_container(card)

        title = (
            find_first_attribute(card, [None], "title")
            or find_first_attribute(container, ["a[href*='-p-']", "img"], "title")
            or find_first_attribute(container, ["img"], "alt")
            or find_first_text(
                container,
                [
                    "[data-test-id^='title-']",
                    "[data-test-id='product-card-name']",
                    "h3[data-test-id='product-card-name']",
                    "h3",
                    "h2",
                ],
            )
        )
        price_text, price_value = extract_price_from_selectors(
            container,
            [
                "[data-test-id^='final-price-']",
                "div[class*='finalPrice__']",
                "[data-test-id='price-current-price']",
                "[data-test-id='product-price']",
            ],
        )
        image_url = find_first_attribute(container, ["img"], "src")

        if title and price_value is not None:
            results.append(
                build_result(
                    "Hepsiburada", product_name, title, price_text, price_value, url, image_url
                )
            )

    logger.info("Hepsiburada: %s geçerli ürün bulundu", len(results))
    return sort_and_limit(results, max_products)


def search_amazon(driver, product_name, max_products=DEFAULT_MAX_PRODUCTS):
    query = urlencode({"k": product_name})
    driver.get(f"https://www.amazon.com.tr/s?{query}")

    cards = wait_for_cards(
        driver,
        [
            "div[data-component-type='s-search-result']",
            "div[data-asin]:not([data-asin=''])",
        ],
    )

    results = []
    seen_products = set()
    for card in cards:
        title = (
            find_first_text(
                card,
                [
                    "[data-cy='title-recipe'] h2",
                    "h2.a-size-base-plus",
                    "h2.a-size-medium",
                    "h2 span",
                    "h2",
                ],
            )
            or find_first_attribute(card, ["img.s-image"], "alt")
        )
        url = find_first_attribute(
            card,
            [
                "[data-cy='title-recipe'] a[href*='/dp/']",
                "h2 a[href*='/dp/']",
                "a.a-link-normal[href*='/dp/']",
                "a[href*='/dp/']",
            ],
            "href",
        )
        product_key = url or normalize_text(title)
        if not product_key or product_key in seen_products:
            continue
        seen_products.add(product_key)

        price_text, price_value = extract_amazon_price(card)
        image_url = find_first_attribute(card, ["img.s-image", "img"], "src")

        if title and price_value is not None:
            results.append(
                build_result(
                    "Amazon", product_name, title, price_text, price_value, url, image_url
                )
            )

    logger.info("Amazon: %s geçerli ürün bulundu", len(results))
    return sort_and_limit(results, max_products)


def compare_price(product_name, max_products=DEFAULT_MAX_PRODUCTS):
    """Üç mağazayı tarar; tek mağazadaki hata diğer sonuçları engellemez."""
    if not isinstance(product_name, str):
        raise ValueError("Ürün adı metin olmalıdır")

    product_name = " ".join(product_name.split())
    if not product_name:
        raise ValueError("Ürün adı gereklidir")
    if len(product_name) > MAX_QUERY_LENGTH:
        raise ValueError(f"Ürün adı en fazla {MAX_QUERY_LENGTH} karakter olabilir")
    if not isinstance(max_products, int) or not 1 <= max_products <= 20:
        raise ValueError("Ürün sayısı 1 ile 20 arasında olmalıdır")

    driver = None
    results = {"trendyol": [], "hepsiburada": [], "amazon": []}
    searches = (
        ("trendyol", search_trendyol),
        ("hepsiburada", search_hepsiburada),
        ("amazon", search_amazon),
    )

    try:
        driver = create_driver()
        for site_key, search_function in searches:
            try:
                results[site_key] = search_function(driver, product_name, max_products)
            except TimeoutException:
                logger.warning("%s sonuçları zaman aşımına uğradı", site_key)
            except WebDriverException:
                logger.exception("%s taranırken tarayıcı hatası oluştu", site_key)
            except Exception:
                logger.exception("%s taranırken beklenmeyen hata oluştu", site_key)
    finally:
        if driver is not None:
            try:
                driver.quit()
            except WebDriverException:
                logger.warning("Tarayıcı oturumu kapatılırken hata oluştu")

    return results
