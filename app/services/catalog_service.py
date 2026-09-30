from urllib.parse import quote_plus


def search_url(
    platform: str,
    query: str
) -> str:

    q = quote_plus(query)

    bases = {

        "Amazon":
            f"https://www.amazon.in/s?k={q}",

        "Flipkart":
            f"https://www.flipkart.com/search?q={q}",

        "IKEA":
            f"https://www.ikea.com/in/en/search/?q={q}",

        "Swiggy":
            f"https://www.swiggy.com/search?query={q}",

        "Zomato":
            f"https://www.zomato.com/search?q={q}",

        "OYO":
            f"https://www.oyorooms.com/search/?location={q}",
    }

    return bases.get(
        platform,
        f"https://www.google.com/search?q={q}"
    )


CATALOG = {

    "home": [

        (
            "LED Ceiling Light",
            "Lighting",
            1299,
            "Amazon"
        ),

        (
            "Modern Floor Lamp",
            "Lighting",
            2499,
            "IKEA"
        ),

        (
            "Compact Study Table",
            "Furniture",
            4999,
            "Amazon"
        ),

        (
            "Minimal Wall Shelf",
            "Decor",
            1799,
            "IKEA"
        ),

        (
            "Dining Chair",
            "Furniture",
            3299,
            "Flipkart"
        ),

        (
            "Decorative Wall Art",
            "Decor",
            1499,
            "Amazon"
        ),

        (
            "Ceiling Fan",
            "Appliance",
            2899,
            "Flipkart"
        ),

        (
            "Storage Cabinet",
            "Furniture",
            6999,
            "IKEA"
        ),
    ],

    "party": [

        (
            "Veg Party Catering",
            "Food",
            399,
            "Swiggy"
        ),

        (
            "Mixed Party Catering",
            "Food",
            549,
            "Zomato"
        ),

        (
            "Birthday Decoration Kit",
            "Decoration",
            1999,
            "Amazon"
        ),

        (
            "Event Decoration Package",
            "Decoration",
            5999,
            "Zomato"
        ),

        (
            "Budget Stay Option",
            "Accommodation",
            1800,
            "OYO"
        ),

        (
            "Premium Stay Option",
            "Accommodation",
            3200,
            "OYO"
        ),
    ],

    "jewelry": [

        (
            "Classic Stud Earrings",
            "Earrings",
            899,
            "Amazon"
        ),

        (
            "Minimal Pendant Necklace",
            "Necklace",
            1699,
            "Flipkart"
        ),

        (
            "Elegant Bracelet",
            "Bracelet",
            2299,
            "Amazon"
        ),

        (
            "Traditional Jhumka",
            "Earrings",
            1999,
            "Flipkart"
        ),

        (
            "Layered Necklace",
            "Necklace",
            3499,
            "Amazon"
        ),

        (
            "Occasion Ring",
            "Ring",
            2499,
            "Flipkart"
        ),
    ],
}


def catalog_for(
    planner: str,
    budget: float,
    query_terms: list[str]
) -> list[dict]:

    rows = []

    terms = " ".join(
        query_terms
    ).lower()

    for (
        title,
        category,
        price,
        platform
    ) in CATALOG.get(
        planner,
        []
    ):

        score = 0

        haystack = (
            f"{title} {category}"
            .lower()
        )

        for term in query_terms:

            if term.lower() in haystack:

                score += 2

        if price <= budget:

            score += 1

        rows.append(
            {
                "title": title,
                "category": category,
                "price": float(price),
                "platform": platform,
                "url": search_url(
                    platform,
                    f"{terms} {title}"
                ),
                "score": score,
            }
        )

    return sorted(
        rows,
        key=lambda x: (
            -x["score"],
            x["price"]
        )
    )