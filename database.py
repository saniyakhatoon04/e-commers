import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ecommerce.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Create Categories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            icon TEXT,
            banner_image TEXT
        )
    ''')

    # Create Products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            category_id INTEGER,
            price REAL NOT NULL,
            original_price REAL,
            discount_percent INTEGER,
            description TEXT,
            features TEXT,
            rating REAL DEFAULT 4.5,
            review_count INTEGER DEFAULT 0,
            stock INTEGER DEFAULT 50,
            is_featured INTEGER DEFAULT 0,
            is_bestseller INTEGER DEFAULT 0,
            image_url TEXT,
            gallery_urls TEXT,
            sizes TEXT,
            colors TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')

    # Create Reviews table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            author_name TEXT NOT NULL,
            rating INTEGER NOT NULL,
            title TEXT,
            comment TEXT NOT NULL,
            verified_purchase INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')

    # Create Orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number TEXT UNIQUE NOT NULL,
            customer_name TEXT NOT NULL,
            customer_email TEXT NOT NULL,
            customer_phone TEXT NOT NULL,
            address TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            zip_code TEXT NOT NULL,
            payment_method TEXT NOT NULL,
            subtotal REAL NOT NULL,
            discount REAL DEFAULT 0,
            shipping_cost REAL DEFAULT 0,
            tax REAL DEFAULT 0,
            total REAL NOT NULL,
            status TEXT DEFAULT 'Processing',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create Order Items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            selected_size TEXT,
            selected_color TEXT,
            subtotal REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')

    conn.commit()

    # Seed data if empty
    cursor.execute('SELECT COUNT(*) FROM categories')
    if cursor.fetchone()[0] == 0:
        seed_data(conn)

    conn.close()

def seed_data(conn):
    cursor = conn.cursor()

    categories = [
        ('Electronics', 'electronics', 'fa-laptop', 'https://images.unsplash.com/photo-1498049794561-7780e7231661?w=1200&q=80'),
        ('Fashion & Apparel', 'fashion', 'fa-shirt', 'https://images.unsplash.com/photo-1445205170230-053b83016050?w=1200&q=80'),
        ('Footwear', 'footwear', 'fa-shoe-prints', 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=1200&q=80'),
        ('Home & Kitchen', 'home-kitchen', 'fa-blender', 'https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=1200&q=80'),
        ('Accessories', 'accessories', 'fa-glasses', 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=1200&q=80')
    ]

    cursor.executemany('''
        INSERT INTO categories (name, slug, icon, banner_image)
        VALUES (?, ?, ?, ?)
    ''', categories)

    products = [
        # Electronics
        (
            'Sony WH-1000XM5 Wireless Noise-Cancelling Headphones',
            'sony-wh1000xm5-headphones',
            1,
            348.00,
            399.99,
            13,
            'Industry-leading noise cancellation optimized with two processors and 8 microphones. Magnificent sound quality engineered to perfection with 30-hour battery life and ultra-comfortable lightweight design.',
            json.dumps(['Industry-leading noise cancellation', 'Up to 30-hour battery life with quick charge', 'Crystal clear hands-free calling with 4 beamforming mics', 'Multipoint connection allows switching between devices']),
            4.8,
            248,
            45,
            1,
            1,
            'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80',
            json.dumps([
                'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80',
                'https://images.unsplash.com/photo-1484704849700-f032a568e944?w=800&q=80',
                'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=800&q=80'
            ]),
            json.dumps(['Standard Edition', 'Travel Bundle']),
            json.dumps([
                {'name': 'Silver White', 'hex': '#dcdcdc'},
                {'name': 'Midnight Black', 'hex': '#1c1c1e'},
                {'name': 'Midnight Blue', 'hex': '#1b2a47'}
            ])
        ),
        (
            'Apple MacBook Air 15" M2 Chip 512GB SSD',
            'macbook-air-15-m2',
            1,
            1199.00,
            1399.00,
            14,
            'Strikingly thin design with expansive 15.3-inch Liquid Retina display. Supercharged by the M2 chip offering blazing-fast performance and up to 18 hours of all-day battery life.',
            json.dumps(['Apple M2 chip with 8-core CPU and 10-core GPU', '15.3-inch Liquid Retina display with True Tone', '1080p FaceTime HD camera', 'Six-speaker sound system with Spatial Audio']),
            4.9,
            412,
            25,
            1,
            1,
            'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&q=80',
            json.dumps([
                'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&q=80',
                'https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=800&q=80',
                'https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=800&q=80'
            ]),
            json.dumps(['256GB SSD', '512GB SSD', '1TB SSD']),
            json.dumps([
                {'name': 'Space Gray', 'hex': '#4b4846'},
                {'name': 'Silver', 'hex': '#e0e2e5'},
                {'name': 'Midnight', 'hex': '#1e242d'},
                {'name': 'Starlight', 'hex': '#f0e5d8'}
            ])
        ),
        (
            'Apple Watch Series 9 GPS + Cellular 45mm',
            'apple-watch-series-9',
            1,
            429.00,
            499.00,
            14,
            'Smarter, brighter, and mightier. Featuring the powerful S9 SiP chip, double tap gesture control, precision heart rate monitoring, advanced workout metrics, and sleep tracking.',
            json.dumps(['Always-On Retina display up to 2000 nits', 'Double tap gesture for one-handed navigation', 'Advanced health and safety sensors', 'Water resistant up to 50 meters']),
            4.7,
            189,
            38,
            1,
            0,
            'https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=800&q=80',
            json.dumps([
                'https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=800&q=80',
                'https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=800&q=80'
            ]),
            json.dumps(['41mm', '45mm']),
            json.dumps([
                {'name': 'Midnight', 'hex': '#1c1f24'},
                {'name': 'Starlight', 'hex': '#e4dcd3'},
                {'name': 'Product Red', 'hex': '#ba0c2f'}
            ])
        ),
        (
            'Bose SoundLink Revolve+ II Bluetooth Speaker',
            'bose-soundlink-revolve-plus',
            1,
            249.00,
            329.00,
            24,
            'Deep, loud, and immersive 360-degree sound. Durable water and dust-resistant design (IP55) with flexible fabric handle and up to 17 hours of playtime.',
            json.dumps(['True 360-degree sound coverage', 'IP55 water and dust resistance', 'Built-in microphone for speakerphone calls', 'Up to 17 hours rechargeable battery life']),
            4.6,
            96,
            30,
            0,
            0,
            'https://images.unsplash.com/photo-1545454675-3531b543be5d?w=800&q=80',
            json.dumps([
                'https://images.unsplash.com/photo-1545454675-3531b543be5d?w=800&q=80',
                'https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?w=800&q=80'
            ]),
            json.dumps(['Standard Edition']),
            json.dumps([
                {'name': 'Triple Black', 'hex': '#111111'},
                {'name': 'Lux Gray', 'hex': '#b0b3b8'}
            ])
        ),

        # Fashion & Apparel
        (
            'Men\'s Classic Tailored Oxford Cotton Shirt',
            'mens-tailored-oxford-shirt',
            2,
            49.99,
            75.00,
            33,
            'Expertly woven from 100% premium long-staple Egyptian cotton. Breathable, wrinkle-resistant finish with classic button-down collar and tailored silhouette suitable for formal or casual wear.',
            json.dumps(['100% Long-Staple Egyptian Cotton', 'Wrinkle-resistant easy care fabric', 'Reinforced mother-of-pearl buttons', 'Tailored modern fit']),
            4.6,
            134,
            80,
            1,
            1,
            'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=800&q=80',
            json.dumps([
                'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=800&q=80',
                'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=800&q=80'
            ]),
            json.dumps(['S', 'M', 'L', 'XL', 'XXL']),
            json.dumps([
                {'name': 'Sky Blue', 'hex': '#a0c4ff'},
                {'name': 'Crisp White', 'hex': '#ffffff'},
                {'name': 'Soft Pink', 'hex': '#ffd6e0'},
                {'name': 'Navy Blue', 'hex': '#1d3557'}
            ])
        ),
        (
            'Women\'s Cashmere Blend Oversized Knit Sweater',
            'womens-cashmere-knit-sweater',
            2,
            89.50,
            120.00,
            25,
            'Plush, ultra-soft knit sweater crafted with genuine Mongolian cashmere blend. Relaxed silhouette featuring dropped shoulders, ribbed cuffs, and cozy ribbed turtleneck.',
            json.dumps(['Ultra-soft Mongolian cashmere blend', 'Cozy ribbed mock turtleneck', 'Relaxed slouchy drape', 'Pilling-resistant yarn']),
            4.7,
            167,
            60,
            1,
            0,
            'https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=800&q=80',
            json.dumps([
                'https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=800&q=80',
                'https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=800&q=80'
            ]),
            json.dumps(['XS', 'S', 'M', 'L', 'XL']),
            json.dumps([
                {'name': 'Oatmeal Beige', 'hex': '#e6decb'},
                {'name': 'Heather Gray', 'hex': '#9e9e9e'},
                {'name': 'Warm Terracotta', 'hex': '#c1664b'},
                {'name': 'Cream White', 'hex': '#faf0e6'}
            ])
        ),
        (
            'Vintage Washed Denim Trucker Jacket',
            'vintage-washed-denim-jacket',
            2,
            79.00,
            110.00,
            28,
            'Timeless American heritage trucker jacket crafted from heavy-duty 13.5oz ring-spun cotton denim with vintage faded wash, copper shank hardware, and dual button-flap chest pockets.',
            json.dumps(['100% Heavy-duty cotton denim', 'Antiqued brass shank buttons', 'Adjustable waistband tabs', 'Double-needle contrast stitching']),
            4.5,
            88,
            55,
            0,
            1,
            'https://images.unsplash.com/photo-1576995853123-5a10305d93c0?w=800&q=80',
            json.dumps([
                'https://images.unsplash.com/photo-1576995853123-5a10305d93c0?w=800&q=80',
                'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=800&q=80'
            ]),
            json.dumps(['S', 'M', 'L', 'XL']),
            json.dumps([
                {'name': 'Indigo Blue', 'hex': '#2b4c7e'},
                {'name': 'Faded Light Wash', 'hex': '#8da9c4'},
                {'name': 'Washed Charcoal', 'hex': '#3a3a3a'}
            ])
        ),

        # Footwear
        (
            'Nike Air Max 270 Responsive Running Shoes',
            'nike-air-max-270-running-shoes',
            3,
            159.99,
            180.00,
            11,
            'Boasting Nike\'s biggest heel Air unit yet, the Air Max 270 delivers a super-soft ride that feels as impossible as it looks. Breathable engineered mesh upper hugs the foot.',
            json.dumps(['Large volume 270 Max Air unit in heel', 'Dual-density foam sole for plush comfort', 'Breathable knit mesh upper', 'Stretchy inner sleeve creates snug fit']),
            4.8,
            312,
            40,
            1,
            1,
            'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&q=80',
            json.dumps([
                'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&q=80',
                'https://images.unsplash.com/photo-1607522370275-f14206abe5d3?w=800&q=80',
                'https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=800&q=80'
            ]),
            json.dumps(['US 8', 'US 9', 'US 10', 'US 11', 'US 12']),
            json.dumps([
                {'name': 'Habanero Red', 'hex': '#d90429'},
                {'name': 'Triple Black', 'hex': '#111111'},
                {'name': 'Pure Platinum', 'hex': '#e2e8f0'}
            ])
        ),
        (
            'Adidas Ultraboost Light Performance Sneakers',
            'adidas-ultraboost-light-sneakers',
            3,
            144.00,
            190.00,
            24,
            'Experience epic energy return with the lightest Ultraboost ever made. Features Light BOOST midsole cushioning and Primeknit+ textile upper crafted for maximum support.',
            json.dumps(['Light BOOST midsole foam', 'Linear Energy Push system increases stiffness', 'Continental Rubber outsole', 'Primeknit+ textile upper']),
            4.7,
            145,
            35,
            1,
            0,
            'https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=800&q=80',
            json.dumps([
                'https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=800&q=80',
                'https://images.unsplash.com/photo-1587563871167-1ee9c731aefb?w=800&q=80'
            ]),
            json.dumps(['US 7.5', 'US 8.5', 'US 9.5', 'US 10.5', 'US 11.5']),
            json.dumps([
                {'name': 'Cloud White', 'hex': '#f8f9fa'},
                {'name': 'Core Black', 'hex': '#1c1c1c'},
                {'name': 'Solar Orange', 'hex': '#ff5e00'}
            ])
        ),
        (
            'Handcrafted Full-Grain Leather Chelsea Boots',
            'leather-chelsea-boots-handcrafted',
            3,
            185.00,
            240.00,
            23,
            'Artisan handcrafted from Italian full-grain leather that burnishes beautifully over time. Elastic side gussets and pull tabs ensure effortless slip-on comfort with durable Goodyear welted soles.',
            json.dumps(['Italian full-grain calfskin leather', 'Goodyear welted resoleable construction', 'Shock-absorbing cork bed midsole', 'Reinforced dual elastic side gore']),
            4.9,
            78,
            20,
            0,
            1,
            'https://images.unsplash.com/photo-1638247025967-b4e38f787b76?w=800&q=80',
            json.dumps([
                'https://images.unsplash.com/photo-1638247025967-b4e38f787b76?w=800&q=80',
                'https://images.unsplash.com/photo-1520639888713-7851133b1ed0?w=800&q=80'
            ]),
            json.dumps(['US 8', 'US 9', 'US 10', 'US 11']),
            json.dumps([
                {'name': 'Cognac Brown', 'hex': '#8b4513'},
                {'name': 'Espresso Black', 'hex': '#222222'},
                {'name': 'Suede Tan', 'hex': '#c29b61'}
            ])
        ),

        # Home & Kitchen
        (
            'Ninja Professional Plus Countertop Blender 1400W',
            'ninja-professional-blender-1400w',
            4,
            99.99,
            139.99,
            29,
            'Crush ice into snow in seconds with 1400 peak watts of power. Features Auto-iQ programs that deliver pulse, pause, and blend patterns with precision for smoothies, frozen drinks, and nutrient extracts.',
            json.dumps(['1400 Peak Watts heavy-duty motor', '72 oz Total Crushing Pitcher with stacked blades', '3 Auto-iQ preset programs', 'BPA-free dishwasher safe parts']),
            4.6,
            275,
            65,
            1,
            1,
            'https://images.unsplash.com/photo-1570222094114-d054a817e56b?w=800&q=80',
            json.dumps([
                'https://images.unsplash.com/photo-1570222094114-d054a817e56b?w=800&q=80',
                'https://images.unsplash.com/photo-1585515320310-259814833e62?w=800&q=80'
            ]),
            json.dumps(['Standard Jar (72 oz)', 'Mega Bundle with To-Go Cups']),
            json.dumps([
                {'name': 'Brushed Stainless', 'hex': '#8d99ae'},
                {'name': 'Piano Black', 'hex': '#212529'}
            ])
        ),
        (
            'Nespresso Vertuo Pop+ Deluxe Espresso Machine',
            'nespresso-vertuo-pop-deluxe',
            4,
            129.00,
            169.00,
            24,
            'Centrifusion technology brews the perfect cup of coffee or rich espresso with a silky crema at the touch of a button. Compact and vibrant design fits seamlessly on any kitchen counter.',
            json.dumps(['Brews 5 cup sizes from espresso to 14oz coffee', 'One-touch brewing system', 'Fast 30-second heat up time', 'Bluetooth and Wi-Fi connectivity for alerts']),
            4.5,
            153,
            42,
            1,
            0,
            'https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?w=800&q=80',
            json.dumps([
                'https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?w=800&q=80',
                'https://images.unsplash.com/photo-1520970014086-2208d157c9e2?w=800&q=80'
            ]),
            json.dumps(['Solo Machine', 'Machine + Aeroccino Milk Frother']),
            json.dumps([
                {'name': 'Glossy Black', 'hex': '#141414'},
                {'name': 'Cherry Red', 'hex': '#c1121f'},
                {'name': 'Mint Aqua', 'hex': '#70a9a1'}
            ])
        ),
        (
            'Philips Premium XXL Digital Airfryer 7.3L',
            'philips-xxl-digital-airfryer-73l',
            4,
            179.99,
            249.99,
            28,
            'Twin TurboStar technology extracts and captures excess fat while frying with little to no oil. XXL capacity fits a whole chicken or up to two bags of crispy fries with smart cooking presets.',
            json.dumps(['Fat Removal Technology for healthier meals', 'Rapid Air technology for crispier results', 'Digital touch screen with 5 presets', 'Keep warm mode for up to 30 mins']),
            4.8,
            198,
            30,
            0,
            1,
            'https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?w=800&q=80',
            json.dumps([
                'https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?w=800&q=80'
            ]),
            json.dumps(['XXL (7.3 Liters)']),
            json.dumps([
                {'name': 'Matte Black / Copper', 'hex': '#1f1f1f'},
                {'name': 'White / Silver', 'hex': '#e9ecef'}
            ])
        ),

        # Accessories
        (
            'Ray-Ban Classic Aviator Polarized Sunglasses',
            'ray-ban-classic-aviator-polarized',
            5,
            163.00,
            210.00,
            22,
            'First created in 1937 for US aviators, the iconic Ray-Ban Aviator pairs classic teardrop styling with crystal polarized G-15 lenses that eliminate 99% of reflected glare.',
            json.dumps(['100% UV400 protection polarized lenses', 'Lightweight and durable monel metal frame', 'Adjustable soft silicone nose pads', 'Handmade in Italy with authentic leather case']),
            4.8,
            340,
            50,
            1,
            1,
            'https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=800&q=80',
            json.dumps([
                'https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=800&q=80',
                'https://images.unsplash.com/photo-1508296695146-257a814070b4?w=800&q=80'
            ]),
            json.dumps(['Standard 58mm', 'Large 62mm']),
            json.dumps([
                {'name': 'Gold / G-15 Green', 'hex': '#d4af37'},
                {'name': 'Gunmetal / Grey', 'hex': '#4a4e69'},
                {'name': 'Matte Black / Polarized Black', 'hex': '#111111'}
            ])
        ),
        (
            'Fossil The Minimalist Slim Chronograph Watch',
            'fossil-minimalist-slim-watch',
            5,
            85.00,
            135.00,
            37,
            'A clean, understated aesthetic that pairs effortlessly with any wardrobe. Features a slim 44mm case, sunray dial, Japanese quartz movement, and interchangeable genuine amber leather strap.',
            json.dumps(['44mm slim stainless steel case', 'Genuine amber leather band with buckle', 'Water resistant to 50 meters (165 ft)', 'Scratch-resistant mineral crystal lens']),
            4.6,
            115,
            45,
            0,
            1,
            'https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=800&q=80',
            json.dumps([
                'https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=800&q=80',
                'https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=800&q=80'
            ]),
            json.dumps(['44mm Case']),
            json.dumps([
                {'name': 'Saddle Brown / Navy', 'hex': '#8b5a2b'},
                {'name': 'All Black Stainless', 'hex': '#1e1e1e'},
                {'name': 'Silver / Tan Leather', 'hex': '#c4a482'}
            ])
        ),
        (
            'Bellroy Hide & Seek RFID Protected Leather Wallet',
            'bellroy-hide-and-seek-rfid-wallet',
            5,
            89.00,
            109.00,
            18,
            'Engineered to hold 5-12 cards plus flat bills without unnecessary bulk. Features an ingenious hidden bill compartment for secret notes and advanced RFID blocking lining.',
            json.dumps(['Certified environmentally-tanned leather', 'RFID blocking technology protects cards', 'Hidden bill section and discreet coin pouch', 'Backed by 3-year warranty']),
            4.7,
            92,
            70,
            1,
            0,
            'https://images.unsplash.com/photo-1627123424574-724758594e93?w=800&q=80',
            json.dumps([
                'https://images.unsplash.com/photo-1627123424574-724758594e93?w=800&q=80'
            ]),
            json.dumps(['Slim Standard', 'High Edition']),
            json.dumps([
                {'name': 'Caramel Tan', 'hex': '#9c6644'},
                {'name': 'Black Obsidian', 'hex': '#1c1c1c'},
                {'name': 'Forest Green', 'hex': '#2d4a3e'}
            ])
        )
    ]

    cursor.executemany('''
        INSERT INTO products (
            name, slug, category_id, price, original_price, discount_percent,
            description, features, rating, review_count, stock, is_featured,
            is_bestseller, image_url, gallery_urls, sizes, colors
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', products)

    # Seed Sample Reviews
    reviews = [
        (1, 'Alex Rivera', 5, 'Best noise cancelling headphones on the market!', 'I commute daily on the subway and these completely block out the rumble and crowd noise. Battery life lasts me an entire week. Sound quality is crisp with deep punchy bass. Worth every penny!', 1),
        (1, 'Sarah Chen', 5, 'Super comfortable and crystal clear audio', 'The design is so sleek and lightweight. Doesn\'t squeeze my head like other over-ear headphones. Call quality for Zoom meetings is superb.', 1),
        (1, 'Michael B.', 4, 'Great sound, wish the case folded smaller', 'Phenomenal audio and ANC. The only minor gripe is the ear cups don\'t fold inward like the XM4s, but the case is still slim.', 1),
        (2, 'David Miller', 5, 'The 15 inch screen is a game changer', 'Switching from a 13-inch Air to this 15-inch model was the best upgrade. Completely silent, no fan noise, and handles photo editing and coding with zero stutter.', 1),
        (2, 'Emma Watson', 5, 'Incredible battery life and build quality', 'I can work at coffee shops all day without packing a charger. The Midnight color looks gorgeous in person.', 1),
        (5, 'Marcus Aurelius', 5, 'Crisp collar and fits like a bespoke shirt', 'Fabric has substantial weight without feeling stiff. Looked sharp all day at a 10-hour conference without excessive wrinkles.', 1),
        (8, 'Liam Gallagher', 5, 'Like walking on clouds', 'The heel air bubble makes walking all day an absolute pleasure. Looks super stylish with joggers and jeans. Runs true to size.', 1),
        (11, 'Jessica Taylor', 5, 'Powerhouse blender!', 'Makes frozen smoothies with frozen strawberries and ice in under 20 seconds. Super smooth texture, easy to rinse clean.', 1),
        (14, 'Carlos Ramirez', 5, 'Authentic Ray-Bans, timeless look', 'The green polarized lenses cut the glare when driving into the sun completely. Great heft and classic styling.', 1)
    ]

    cursor.executemany('''
        INSERT INTO reviews (product_id, author_name, rating, title, comment, verified_purchase)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', reviews)

    conn.commit()

# Helper queries
def get_categories():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM categories ORDER BY name ASC')
    categories = cursor.fetchall()
    conn.close()
    return categories

def get_products(category_slug=None, search_query=None, min_price=None, max_price=None, min_rating=None, sort_by=None, limit=None):
    conn = get_db()
    cursor = conn.cursor()

    query = '''
        SELECT p.*, c.name as category_name, c.slug as category_slug
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE 1=1
    '''
    params = []

    if category_slug and category_slug != 'all':
        query += ' AND c.slug = ?'
        params.append(category_slug)

    if search_query:
        query += ' AND (p.name LIKE ? OR p.description LIKE ?)'
        wildcard = f'%{search_query}%'
        params.extend([wildcard, wildcard])

    if min_price is not None:
        query += ' AND p.price >= ?'
        params.append(float(min_price))

    if max_price is not None:
        query += ' AND p.price <= ?'
        params.append(float(max_price))

    if min_rating is not None:
        query += ' AND p.rating >= ?'
        params.append(float(min_rating))

    # Sorting
    if sort_by == 'price_low':
        query += ' ORDER BY p.price ASC'
    elif sort_by == 'price_high':
        query += ' ORDER BY p.price DESC'
    elif sort_by == 'rating':
        query += ' ORDER BY p.rating DESC, p.review_count DESC'
    elif sort_by == 'discount':
        query += ' ORDER BY p.discount_percent DESC'
    elif sort_by == 'newest':
        query += ' ORDER BY p.id DESC'
    else:
        # Default relevance/featured
        query += ' ORDER BY p.is_featured DESC, p.id ASC'

    if limit:
        query += f' LIMIT {int(limit)}'

    cursor.execute(query, params)
    products = cursor.fetchall()
    conn.close()
    return products

def get_product_by_id(product_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.*, c.name as category_name, c.slug as category_slug
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE p.id = ?
    ''', (product_id,))
    product = cursor.fetchone()
    conn.close()
    return product

def get_product_reviews(product_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM reviews
        WHERE product_id = ?
        ORDER BY created_at DESC
    ''', (product_id,))
    reviews = cursor.fetchall()
    conn.close()
    return reviews

def add_product_review(product_id, author_name, rating, title, comment):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO reviews (product_id, author_name, rating, title, comment, verified_purchase)
        VALUES (?, ?, ?, ?, ?, 1)
    ''', (product_id, author_name, rating, title, comment))

    # Recalculate average rating and review count
    cursor.execute('''
        SELECT AVG(rating), COUNT(id) FROM reviews WHERE product_id = ?
    ''', (product_id,))
    avg_rating, count = cursor.fetchone()
    avg_rating = round(avg_rating or 5.0, 1)

    cursor.execute('''
        UPDATE products
        SET rating = ?, review_count = ?
        WHERE id = ?
    ''', (avg_rating, count, product_id))

    conn.commit()
    conn.close()
    return avg_rating, count

def create_order(order_data, items_data):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO orders (
            order_number, customer_name, customer_email, customer_phone,
            address, city, state, zip_code, payment_method,
            subtotal, discount, shipping_cost, tax, total, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Confirmed')
    ''', (
        order_data['order_number'],
        order_data['customer_name'],
        order_data['customer_email'],
        order_data['customer_phone'],
        order_data['address'],
        order_data['city'],
        order_data['state'],
        order_data['zip_code'],
        order_data['payment_method'],
        order_data['subtotal'],
        order_data['discount'],
        order_data['shipping_cost'],
        order_data['tax'],
        order_data['total']
    ))

    order_id = cursor.lastrowid

    for item in items_data:
        cursor.execute('''
            INSERT INTO order_items (
                order_id, product_id, product_name, price,
                quantity, selected_size, selected_color, subtotal
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            order_id,
            item['product_id'],
            item['product_name'],
            item['price'],
            item['quantity'],
            item.get('selected_size', ''),
            item.get('selected_color', ''),
            item['subtotal']
        ))

    conn.commit()
    conn.close()
    return order_id

def get_order_by_number(order_number):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders WHERE order_number = ?', (order_number,))
    order = cursor.fetchone()

    if not order:
        conn.close()
        return None, []

    cursor.execute('''
        SELECT oi.*, p.image_url
        FROM order_items oi
        LEFT JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = ?
    ''', (order['id'],))
    items = cursor.fetchall()
    conn.close()
    return order, items
