
from django.core.management.base import BaseCommand
from products.models import Category, Product
import random

class Command(BaseCommand):
    help = "Populates the database with Indian restaurant menu items"

    def handle(self, *args, **kwargs):
        # Category.objects.all().delete()
        # Product.objects.all().delete()
        menu_data = {
            "South Indian": [
                ("Dosa", "A crispy and savory fermented crepe made from rice batter and black lentils."),
                ("Idli", "Steamed rice cakes served with sambar and coconut chutney."),
                ("Vada", "Fried savory doughnuts made from urad dal."),
                ("Uttapam", "Thick pancake with toppings like onions, tomatoes, and chilies."),
            ],
            "North Indian": [
                ("Butter Chicken", "Creamy tomato-based chicken curry."),
                ("Chole Bhature", "Spicy chickpeas with deep-fried bread."),
                ("Palak Paneer", "Cottage cheese in spinach gravy."),
                ("Rajma", "Kidney bean curry served with rice."),
            ],
            "Biryani": [
                ("Hyderabadi Biryani", "Aromatic rice with marinated meat and saffron."),
                ("Veg Biryani", "Spiced vegetable rice cooked with herbs."),
                ("Chicken Dum Biryani", "Slow-cooked chicken biryani with rich flavors."),
            ],
            "Desserts": [
                ("Gulab Jamun", "Fried milk balls soaked in sugar syrup."),
                ("Rasgulla", "Soft, spongy balls in light syrup."),
                ("Kheer", "Rice pudding with cardamom and saffron."),
            ],
            "Drinks": [
                ("Masala Chai", "Spiced Indian tea."),
                ("Lassi", "Traditional yogurt drink, sweet or salted."),
                ("Filter Coffee", "South Indian strong brewed coffee."),
            ]
        }

        image_map = {
            "Dosa": "https://source.unsplash.com/400x300/?dosa",
            "Idli": "https://source.unsplash.com/400x300/?idli",
            "Vada": "https://source.unsplash.com/400x300/?vada",
            "Uttapam": "https://source.unsplash.com/400x300/?uttapam",
            "Butter Chicken": "https://source.unsplash.com/400x300/?butter-chicken",
            "Chole Bhature": "https://source.unsplash.com/400x300/?chole-bhature",
            "Palak Paneer": "https://source.unsplash.com/400x300/?palak-paneer",
            "Rajma": "https://source.unsplash.com/400x300/?rajma",
            "Hyderabadi Biryani": "https://source.unsplash.com/400x300/?biryani",
            "Veg Biryani": "https://source.unsplash.com/400x300/?veg-biryani",
            "Chicken Dum Biryani": "https://source.unsplash.com/400x300/?chicken-biryani",
            "Gulab Jamun": "https://source.unsplash.com/400x300/?gulab-jamun",
            "Rasgulla": "https://source.unsplash.com/400x300/?rasgulla",
            "Kheer": "https://source.unsplash.com/400x300/?kheer",
            "Masala Chai": "https://source.unsplash.com/400x300/?masala-chai",
            "Lassi": "https://source.unsplash.com/400x300/?lassi",
            "Filter Coffee": "https://source.unsplash.com/400x300/?filter-coffee",
        }

        for category_name, items in menu_data.items():
            category, _ = Category.objects.get_or_create(
                name=category_name,
                defaults={
                    'description': f"{category_name} dishes",
                    'status': 'ACTIVE'
                }
            )

            for name, description in items:
                price = round(random.uniform(50, 350), 2)  # realistic INR price
                image_url = image_map.get(name, "https://source.unsplash.com/400x300/?indian-food")

                Product.objects.get_or_create(
                    name=name,
                    category=category,
                    defaults={
                        'description': description,
                        'price': price,
                        'image_url': image_url,
                        'status': 'ACTIVE'
                    }
                )

        self.stdout.write(self.style.SUCCESS("✅ Indian food menu populated successfully."))
