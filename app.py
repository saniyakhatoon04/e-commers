import os
import json
import uuid
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import database

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'ecommerce-secret-key-development-2026')

# Initialize DB on start
with app.app_context():
    database.init_db()

# Custom Jinja filters
@app.template_filter('from_json')
def from_json_filter(val):
    if not val:
        return []
    try:
        return json.loads(val)
    except Exception:
        return []

@app.template_filter('currency')
def currency_filter(val):
    try:
        return f"${float(val):,.2f}"
    except (ValueError, TypeError):
        return "$0.00"

# Inject global variables to all templates
@app.context_processor
def inject_globals():
    categories = database.get_categories()
    cart = session.get('cart', [])
    cart_count = sum(item.get('quantity', 1) for item in cart)
    wishlist = session.get('wishlist', [])
    wishlist_count = len(wishlist)
    return {
        'all_categories': categories,
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
        'session_cart': cart,
        'session_wishlist': wishlist
    }

def calculate_cart_totals(cart, coupon=None):
    subtotal = sum(item['price'] * item['quantity'] for item in cart)
    discount = 0.0

    if coupon:
        coupon_upper = coupon.strip().upper()
        if coupon_upper == 'SAVE10':
            discount = round(subtotal * 0.10, 2)
        elif coupon_upper == 'WELCOME20':
            discount = round(subtotal * 0.20, 2)
        elif coupon_upper == 'FLAT15':
            discount = min(15.00, subtotal)

    # Free shipping on orders over $50 or with coupon FREESHIP
    if subtotal == 0:
        shipping = 0.0
    elif coupon and coupon.strip().upper() == 'FREESHIP':
        shipping = 0.0
    elif subtotal >= 50.0:
        shipping = 0.0
    else:
        shipping = 9.99

    taxable_amount = max(0.0, subtotal - discount)
    tax = round(taxable_amount * 0.08, 2) if taxable_amount > 0 else 0.0
    total = round(taxable_amount + shipping + tax, 2)

    return {
        'subtotal': round(subtotal, 2),
        'discount': discount,
        'shipping': round(shipping, 2),
        'tax': tax,
        'total': total,
        'coupon': coupon
    }

# ==================== WEB ROUTES ====================

@app.route('/')
def index():
    category_slug = request.args.get('category', 'all')
    search_query = request.args.get('q', '').strip()
    sort_by = request.args.get('sort', 'featured')

    products = database.get_products(
        category_slug=category_slug if category_slug != 'all' else None,
        search_query=search_query if search_query else None,
        sort_by=sort_by
    )

    featured_deals = database.get_products(limit=4, sort_by='discount')
    categories = database.get_categories()

    return render_template(
        'index.html',
        products=products,
        featured_deals=featured_deals,
        categories=categories,
        current_category=category_slug,
        search_query=search_query,
        current_sort=sort_by
    )

@app.route('/products')
def products():
    category_slug = request.args.get('category', 'all')
    search_query = request.args.get('q', '').strip()
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    min_rating = request.args.get('min_rating')
    sort_by = request.args.get('sort', 'featured')

    products_list = database.get_products(
        category_slug=category_slug if category_slug != 'all' else None,
        search_query=search_query if search_query else None,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        sort_by=sort_by
    )

    categories = database.get_categories()

    return render_template(
        'index.html',
        products=products_list,
        categories=categories,
        current_category=category_slug,
        search_query=search_query,
        min_price=min_price or '',
        max_price=max_price or '',
        min_rating=min_rating or '',
        current_sort=sort_by,
        is_catalog=True
    )

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = database.get_product_by_id(product_id)
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('index'))

    reviews = database.get_product_reviews(product_id)
    related_products = database.get_products(category_slug=product['category_slug'], limit=4)
    # Exclude current product from related
    related_products = [p for p in related_products if p['id'] != product_id][:4]

    return render_template(
        'product_detail.html',
        product=product,
        reviews=reviews,
        related_products=related_products
    )

@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    coupon = session.get('coupon', '')
    totals = calculate_cart_totals(cart_items, coupon)

    return render_template(
        'cart.html',
        cart_items=cart_items,
        totals=totals,
        applied_coupon=coupon
    )

@app.route('/wishlist')
def wishlist():
    wishlist_ids = session.get('wishlist', [])
    wishlist_products = []
    for pid in wishlist_ids:
        p = database.get_product_by_id(pid)
        if p:
            wishlist_products.append(p)

    return render_template('wishlist.html', products=wishlist_products)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart_items = session.get('cart', [])
    if not cart_items:
        flash('Your cart is empty. Please add items before checking out.', 'warning')
        return redirect(url_for('index'))

    coupon = session.get('coupon', '')
    totals = calculate_cart_totals(cart_items, coupon)

    if request.method == 'POST':
        customer_name = request.form.get('customer_name', '').strip()
        customer_email = request.form.get('customer_email', '').strip()
        customer_phone = request.form.get('customer_phone', '').strip()
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        zip_code = request.form.get('zip_code', '').strip()
        payment_method = request.form.get('payment_method', 'Credit Card')

        if not all([customer_name, customer_email, customer_phone, address, city, state, zip_code]):
            flash('Please fill in all required shipping and contact details.', 'danger')
            return render_template('checkout.html', cart_items=cart_items, totals=totals)

        # Generate unique order number
        order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"

        order_data = {
            'order_number': order_number,
            'customer_name': customer_name,
            'customer_email': customer_email,
            'customer_phone': customer_phone,
            'address': address,
            'city': city,
            'state': state,
            'zip_code': zip_code,
            'payment_method': payment_method,
            'subtotal': totals['subtotal'],
            'discount': totals['discount'],
            'shipping_cost': totals['shipping'],
            'tax': totals['tax'],
            'total': totals['total']
        }

        items_data = []
        for item in cart_items:
            items_data.append({
                'product_id': item['product_id'],
                'product_name': item['name'],
                'price': item['price'],
                'quantity': item['quantity'],
                'selected_size': item.get('size', ''),
                'selected_color': item.get('color', ''),
                'subtotal': round(item['price'] * item['quantity'], 2)
            })

        # Persist order to SQLite
        database.create_order(order_data, items_data)

        # Clear cart and coupon in session
        session['cart'] = []
        session.pop('coupon', None)
        session.modified = True

        return redirect(url_for('order_success', order_number=order_number))

    return render_template(
        'checkout.html',
        cart_items=cart_items,
        totals=totals
    )

@app.route('/order-success/<order_number>')
def order_success(order_number):
    order, items = database.get_order_by_number(order_number)
    if not order:
        flash('Order not found.', 'danger')
        return redirect(url_for('index'))

    return render_template(
        'order_success.html',
        order=order,
        items=items
    )

# ==================== REST API ENDPOINTS ====================

@app.route('/api/cart', methods=['GET'])
def api_get_cart():
    cart = session.get('cart', [])
    coupon = session.get('coupon', '')
    totals = calculate_cart_totals(cart, coupon)
    cart_count = sum(item.get('quantity', 1) for item in cart)
    return jsonify({
        'success': True,
        'cart': cart,
        'count': cart_count,
        'totals': totals
    })

@app.route('/api/cart/add', methods=['POST'])
def api_add_to_cart():
    data = request.get_json() or {}
    product_id = int(data.get('product_id', 0))
    quantity = int(data.get('quantity', 1))
    size = data.get('size', '').strip()
    color = data.get('color', '').strip()

    if product_id <= 0 or quantity <= 0:
        return jsonify({'success': False, 'message': 'Invalid product or quantity'}), 400

    product = database.get_product_by_id(product_id)
    if not product:
        return jsonify({'success': False, 'message': 'Product not found'}), 404

    # Determine default size/color if not specified
    if not size:
        sizes = json.loads(product['sizes']) if product['sizes'] else []
        size = sizes[0] if sizes else ''

    if not color:
        colors = json.loads(product['colors']) if product['colors'] else []
        color = colors[0]['name'] if colors else ''

    cart = session.get('cart', [])

    # Unique key for item variation
    item_key = f"{product_id}_{size}_{color}"

    existing_item = next((item for item in cart if item['item_key'] == item_key), None)
    if existing_item:
        existing_item['quantity'] += quantity
        existing_item['subtotal'] = round(existing_item['price'] * existing_item['quantity'], 2)
    else:
        cart.append({
            'item_key': item_key,
            'product_id': product['id'],
            'name': product['name'],
            'price': product['price'],
            'original_price': product['original_price'],
            'quantity': quantity,
            'image_url': product['image_url'],
            'size': size,
            'color': color,
            'subtotal': round(product['price'] * quantity, 2)
        })

    session['cart'] = cart
    session.modified = True

    cart_count = sum(item['quantity'] for item in cart)
    totals = calculate_cart_totals(cart, session.get('coupon', ''))

    return jsonify({
        'success': True,
        'message': f'"{product["name"]}" added to cart!',
        'count': cart_count,
        'totals': totals
    })

@app.route('/api/cart/update', methods=['POST'])
def api_update_cart():
    data = request.get_json() or {}
    item_key = data.get('item_key')
    quantity = int(data.get('quantity', 1))

    cart = session.get('cart', [])
    item = next((i for i in cart if i['item_key'] == item_key), None)

    if not item:
        return jsonify({'success': False, 'message': 'Item not in cart'}), 404

    if quantity <= 0:
        cart = [i for i in cart if i['item_key'] != item_key]
    else:
        item['quantity'] = quantity
        item['subtotal'] = round(item['price'] * quantity, 2)

    session['cart'] = cart
    session.modified = True

    totals = calculate_cart_totals(cart, session.get('coupon', ''))
    cart_count = sum(i['quantity'] for i in cart)

    return jsonify({
        'success': True,
        'message': 'Cart updated',
        'count': cart_count,
        'totals': totals,
        'item': item if quantity > 0 else None
    })

@app.route('/api/cart/remove', methods=['POST'])
def api_remove_from_cart():
    data = request.get_json() or {}
    item_key = data.get('item_key')

    cart = session.get('cart', [])
    cart = [i for i in cart if i['item_key'] != item_key]

    session['cart'] = cart
    session.modified = True

    totals = calculate_cart_totals(cart, session.get('coupon', ''))
    cart_count = sum(i['quantity'] for i in cart)

    return jsonify({
        'success': True,
        'message': 'Item removed from cart',
        'count': cart_count,
        'totals': totals
    })

@app.route('/api/cart/clear', methods=['POST'])
def api_clear_cart():
    session['cart'] = []
    session.pop('coupon', None)
    session.modified = True
    return jsonify({'success': True, 'message': 'Cart cleared', 'count': 0})

@app.route('/api/cart/apply-coupon', methods=['POST'])
def api_apply_coupon():
    data = request.get_json() or {}
    code = data.get('code', '').strip().upper()

    valid_coupons = {
        'SAVE10': '10% discount applied!',
        'WELCOME20': '20% welcome discount applied!',
        'FREESHIP': 'Free shipping applied!',
        'FLAT15': '$15 discount applied!'
    }

    if code in valid_coupons:
        session['coupon'] = code
        session.modified = True
        cart = session.get('cart', [])
        totals = calculate_cart_totals(cart, code)
        return jsonify({
            'success': True,
            'message': valid_coupons[code],
            'coupon': code,
            'totals': totals
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Invalid coupon code. Try SAVE10, WELCOME20, or FREESHIP'
        }), 400

@app.route('/api/wishlist/toggle', methods=['POST'])
def api_toggle_wishlist():
    data = request.get_json() or {}
    product_id = int(data.get('product_id', 0))

    if product_id <= 0:
        return jsonify({'success': False, 'message': 'Invalid product'}), 400

    wishlist = session.get('wishlist', [])
    if product_id in wishlist:
        wishlist.remove(product_id)
        in_wishlist = False
        message = 'Removed from wishlist'
    else:
        wishlist.append(product_id)
        in_wishlist = True
        message = 'Added to your wishlist!'

    session['wishlist'] = wishlist
    session.modified = True

    return jsonify({
        'success': True,
        'in_wishlist': in_wishlist,
        'count': len(wishlist),
        'message': message
    })

@app.route('/api/product/<int:product_id>')
def api_get_product(product_id):
    product = database.get_product_by_id(product_id)
    if not product:
        return jsonify({'success': False, 'message': 'Product not found'}), 404

    reviews = database.get_product_reviews(product_id)

    product_dict = dict(product)
    product_dict['features'] = json.loads(product['features']) if product['features'] else []
    product_dict['gallery_urls'] = json.loads(product['gallery_urls']) if product['gallery_urls'] else []
    product_dict['sizes'] = json.loads(product['sizes']) if product['sizes'] else []
    product_dict['colors'] = json.loads(product['colors']) if product['colors'] else []
    product_dict['reviews'] = [dict(r) for r in reviews]

    return jsonify({
        'success': True,
        'product': product_dict
    })

@app.route('/api/reviews/<int:product_id>', methods=['POST'])
def api_add_review(product_id):
    data = request.get_json() or {}
    author_name = data.get('author_name', '').strip()
    rating = int(data.get('rating', 5))
    title = data.get('title', '').strip()
    comment = data.get('comment', '').strip()

    if not author_name or not comment:
        return jsonify({'success': False, 'message': 'Author name and review comments are required'}), 400

    if rating < 1 or rating > 5:
        return jsonify({'success': False, 'message': 'Rating must be between 1 and 5'}), 400

    avg_rating, count = database.add_product_review(product_id, author_name, rating, title, comment)

    return jsonify({
        'success': True,
        'message': 'Thank you! Your review has been submitted successfully.',
        'new_rating': avg_rating,
        'review_count': count
    })

@app.route('/api/search/suggestions')
def api_search_suggestions():
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return jsonify({'results': []})

    products = database.get_products(search_query=q, limit=6)
    results = [{
        'id': p['id'],
        'name': p['name'],
        'price': f"${p['price']:,.2f}",
        'image': p['image_url'],
        'category': p['category_name']
    } for p in products]

    return jsonify({'results': results})

if __name__ == '__main__':
    import webbrowser
    import threading

    print("==================================================")
    print("  ApexMart E-Commerce Store Running Locally")
    print("  Open: http://127.0.0.1:5000 in your browser")
    print("==================================================")

    def open_browser():
        webbrowser.open('http://127.0.0.1:5000')

    # Automatically open the browser tab
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
        threading.Timer(1.2, open_browser).start()

    app.run(debug=True, host='0.0.0.0', port=5000)
