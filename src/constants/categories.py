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
                    "name": "Fuel",
                    "nature": Nature.NEED
                },
                {
                    "name": "Vehicle Maintenance",
                    "nature": Nature.NEED
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
                    "name": "Restaurants",
                    "nature": Nature.WANT
                },
                {
                    "name": "Takeout",
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
            "color": "magenta",
            "nature": Nature.WANT,
            "subcategories": [
                {
                    "name": "Clothes",
                    "nature": Nature.NEED
                },
                {
                    "name": "Electronics",
                    "nature": Nature.WANT
                },
                {
                    "name": "Home",
                    "nature": Nature.NEED
                }
            ]
        },
        {
            "name": "Bills",
            "color": "cyan",
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