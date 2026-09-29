from urllib.parse import quote_plus


PLATFORM_SEARCH_URLS = {
    "Amazon": "https://www.amazon.in/s?k={query}",
    "Flipkart": "https://www.flipkart.com/search?q={query}",
    "IKEA": "https://www.ikea.com/in/en/search/?q={query}",
    "Swiggy": "https://www.swiggy.com/search?query={query}",
    "Zomato": "https://www.zomato.com/search?query={query}",
    "OYO": "https://www.oyorooms.com/search?location={query}",
}


def marketplace_url(
    platform: str,
    query: str
) -> str:

    template = PLATFORM_SEARCH_URLS.get(
        platform,
        "https://www.google.com/search?q={query}",
    )

    return template.format(
        query=quote_plus(query)
    )


def make_catalog_item(
    title: str,
    category: str,
    platform: str,
    price: float,
    reason: str,
    query: str,
):
    return {
        "title": title,
        "category": category,
        "platform": platform,
        "price": round(float(price), 2),
        "reason": reason,
        "url": marketplace_url(
            platform,
            query,
        ),
    }