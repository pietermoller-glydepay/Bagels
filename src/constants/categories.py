from models.category import Nature

DEFAULT_CATEGORIES = [
        {
            "name": "Income",
            "color": "bright_green", 
            "nature": Nature.MUST,
            "subcategories": [
                {
                    "name": "Salary",
                    "nature": Nature.MUST
                },
                {
                    "name": "Investments",
                    "nature": Nature.WANT
                },
                {
                    "name": "Side Hustle", 
                    "nature": Nature.WANT
                }
            ]
        },
        {
            "name": "Transport",
            "color": "yellow",
            "nature": Nature.NEED,
            "subcategories": [
                {
                    "name": "Public Transport",
                    "nature": Nature.NEED
                },
                {
                    "name": "Taxi",
                    "nature": Nature.WANT
                }
            ]
        },
        {
            "name": "Food",
            "color": "red",
            "nature": Nature.MUST,
            "subcategories": [
                {
                    "name": "Groceries",
                    "nature": Nature.MUST
                },
                {
                    "name": "Dine out",
                    "nature": Nature.NEED
                },
                {
                    "name": "Takeout",
                    "nature": Nature.WANT
                },
                {
                    "name": "Snacks",
                    "nature": Nature.WANT
                }
            ]
        },
        {
            "name": "Subscriptions",
            "color": "blue",
            "nature": Nature.NEED,
            "subcategories": [
                {
                    "name": "Streaming Services",
                    "nature": Nature.WANT
                },
                {
                    "name": "Software",
                    "nature": Nature.NEED
                },
                {
                    "name": "Gym",
                    "nature": Nature.WANT
                }
            ]
        },
        {
            "name": "Shopping",
            "color": "cyan",
            "nature": Nature.WANT,
            "subcategories": [
                {
                    "name": "Clothes",
                    "nature": Nature.NEED
                },
                {
                    "name": "Gifts",
                    "nature": Nature.WANT
                }
            ]
        },
        {
            "name": "Bills",
            "color": "magenta",
            "nature": Nature.MUST,
            "subcategories": [
                {
                    "name": "Utilities",
                    "nature": Nature.MUST
                },
                {
                    "name": "Rent/Mortgage",
                    "nature": Nature.MUST
                },
                {
                    "name": "Insurance",
                    "nature": Nature.MUST
                }
            ]
        }
    ]