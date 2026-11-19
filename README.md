# ApexMart - Modern E-Commerce Shopping Platform

A modern, responsive, and full-featured E-Commerce shopping website inspired by **Amazon** and **Flipkart**, built with **Python Flask**, **SQLite**, **HTML5**, **CSS3**, and **Vanilla JavaScript**.

---

## 🌟 Key Features

1. **High-Quality Product Displays**: Rich product imagery with multi-image galleries, zoom transitions, and category tags.
2. **Product Details & Ratings**: Original vs. discounted pricing, savings badges, detailed descriptions, and star ratings with review counts.
3. **Add to Cart & Buy Now**:
   - **Add to Cart**: Adds items to cart with animated toast notifications and updates header badge.
   - **Buy Now**: Adds item and navigates directly to the checkout page.
4. **Product Search & Category Filters**:
   - Live autocomplete search suggestions dropdown.
   - Filter by categories (Electronics, Fashion, Footwear, Home & Kitchen, Accessories).
   - Price range filters (Min/Max inputs).
   - Customer rating filters (4.5+ & 4.0+ stars).
   - Sort by Featured, Price (Low to High / High to Low), Customer Rating, and Discount %.
5. **Interactive Size & Color Selection**: Select custom sizes/options (e.g. S, M, L, XL or storage variants) and color swatches with active visual rings.
6. **Shopping Cart with Quantity Management**:
   - Modern slide-out cart drawer (offcanvas) + dedicated full `/cart` page.
   - Real-time `+` / `-` quantity steppers and item deletion.
7. **Automatic Price & Discount Calculation**:
   - Dynamic subtotal, sales tax (8%), shipping fee (free on orders over $50).
   - Promo code coupon system (`SAVE10` for 10% off, `WELCOME20` for 20% off, `FREESHIP` for free shipping).
8. **Wishlist Functionality**: Save favorite items with animated heart toggles; view, manage, and move items to cart on `/wishlist`.
9. **Customer Reviews & Ratings**:
   - Interactive 5-star rating selector with hover effect.
   - Instant review submission via AJAX with verified buyer badge.
   - Recalculates product average score and review counts automatically.
10. **Multi-Step Checkout Page**:
    - Customer contact information (Name, Email, Phone).
    - Shipping address form (Street, City, State, ZIP, Country).
    - Payment method selector: Credit/Debit Card, UPI / Net Banking, Cash on Delivery.
11. **SQLite Database Persistence**:
    - Fully persistent SQLite database (`ecommerce.db`).
    - Stores `categories`, `products`, `reviews`, `orders`, and `order_items`.
12. **Visual Feedback & Order Confirmation**:
    - Floating animated Toast notifications for every interaction.
    - Post-checkout confirmation page with order reference ID, itemized invoice, and order tracking timeline (Order Placed ➔ Processing ➔ Shipped ➔ Delivered).

---

## 📁 Project Structure

```
e commers/
├── app.py                  # Flask server application & REST API routes
├── database.py             # SQLite models, tables schema & sample seeder
├── requirements.txt        # Python package dependencies (Flask)
├── ecommerce.db            # SQLite database (auto-generated on launch)
├── README.md               # Documentation & setup instructions
├── static/
│   ├── css/
│   │   └── style.css       # Clean, modern Amazon/Flipkart styling
│   ├── js/
│   │   └── main.js         # Interactive cart, drawer, wishlist, toast logic
│   └── images/             # Media assets
└── templates/
    ├── base.html           # Master layout (Header, Nav, Cart Drawer, Footer)
    ├── index.html          # Homepage (Hero carousel, trust perks, catalog)
    ├── product_detail.html # Product showcase, gallery, specs & reviews
    ├── cart.html           # Full shopping cart with order summary
    ├── checkout.html       # Customer address & payment selection
    ├── wishlist.html       # Saved items view
    └── order_success.html  # Order invoice & tracking timeline
```

---

## 🚀 How to Run Locally in VS Code

### Step 1: Open the Project in VS Code
1. Launch **Visual Studio Code**.
2. Go to **File** > **Open Folder...** (or press `Ctrl + K, Ctrl + O`).
3. Select the folder:
   ```
   c:\Users\user\OneDrive\Desktop\e commers
   ```

### Step 2: Open the Integrated Terminal
- Press `` Ctrl + ` `` (Backtick) or go to the top menu: **Terminal** > **New Terminal**.
- Ensure your terminal is PowerShell or Command Prompt.

### Step 3: (Optional but Recommended) Create a Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### Step 4: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 5: Start the Flask Application
```powershell
python app.py
```

You should see output similar to:
```
==================================================
  ApexMart E-Commerce Store Running Locally
  Open: http://127.0.0.1:5000 in your browser
==================================================
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

### Step 6: Open the Website in Your Browser
Hold `Ctrl` and click the link in your terminal, or open your web browser and go to:
```
http://127.0.0.1:5000
```

---

## 🏷️ Test Coupons

You can try entering any of these discount codes in the cart:
- `SAVE10` - 10% Discount on entire cart
- `WELCOME20` - 20% Discount for new shoppers
- `FREESHIP` - Free shipping on any order amount
- `FLAT15` - $15.00 Flat discount

---

## 🛠️ Technologies Used
- **Backend**: Python 3, Flask 3, SQLite 3
- **Frontend**: HTML5 (Jinja2 templates), CSS3 (Modern Flexbox/Grid, CSS Variables), Vanilla JavaScript (ES6+ Fetch API, DOM manipulation)
- **Icons**: Font Awesome 6
- **Typography**: Google Fonts (Inter)
