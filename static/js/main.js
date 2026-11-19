/**
 * ApexMart E-Commerce Platform - Client Interactive Logic
 * Modern, Responsive, Amazon/Flipkart Inspired
 */

document.addEventListener('DOMContentLoaded', () => {
    initHeroSlider();
    initSearchAutocomplete();
    initGlobalCartDrawer();
    initColorAndSizePickers();
    initQuantitySteppers();
    initProductDetailGallery();
    initReviewForm();
    initTabs();
});

/* ==========================================================================
   1. Toast Notification System
   ========================================================================== */

function showToast(title, message, type = 'success') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = 'toast-msg';

    let iconClass = 'fa-circle-check success';
    if (type === 'warning') iconClass = 'fa-circle-exclamation warning';
    if (type === 'danger') iconClass = 'fa-circle-xmark danger';
    if (type === 'info') iconClass = 'fa-circle-info';

    toast.innerHTML = `
        <i class="fa-solid ${iconClass} toast-icon"></i>
        <div class="toast-content">
            <div class="toast-title">${title}</div>
            <div class="toast-text">${message}</div>
        </div>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 400);
    }, 3500);
}

/* ==========================================================================
   2. Cart Operations (Add, Update, Remove, Buy Now)
   ========================================================================== */

async function addToCart(productId, quantity = 1, size = '', color = '', openDrawer = true) {
    try {
        const response = await fetch('/api/cart/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                product_id: productId,
                quantity: parseInt(quantity) || 1,
                size: size,
                color: color
            })
        });

        const data = await response.json();
        if (data.success) {
            updateCartBadge(data.count);
            showToast('Added to Cart', data.message, 'success');
            if (openDrawer) {
                openCartDrawer();
            }
            return true;
        } else {
            showToast('Error', data.message || 'Could not add to cart', 'danger');
            return false;
        }
    } catch (err) {
        console.error('Add to cart error:', err);
        showToast('Error', 'Network error adding to cart', 'danger');
        return false;
    }
}

async function buyNow(productId, quantity = 1, size = '', color = '') {
    const success = await addToCart(productId, quantity, size, color, false);
    if (success) {
        window.location.href = '/checkout';
    }
}

async function updateCartQuantity(itemKey, newQuantity) {
    try {
        const response = await fetch('/api/cart/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ item_key: itemKey, quantity: parseInt(newQuantity) })
        });
        const data = await response.json();
        if (data.success) {
            updateCartBadge(data.count);
            if (window.location.pathname.includes('/cart')) {
                window.location.reload();
            } else {
                renderCartDrawer();
            }
            showToast('Cart Updated', data.message, 'success');
        }
    } catch (err) {
        console.error('Update cart error:', err);
    }
}

async function removeFromCart(itemKey) {
    try {
        const response = await fetch('/api/cart/remove', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ item_key: itemKey })
        });
        const data = await response.json();
        if (data.success) {
            updateCartBadge(data.count);
            if (window.location.pathname.includes('/cart')) {
                window.location.reload();
            } else {
                renderCartDrawer();
            }
            showToast('Removed', data.message, 'info');
        }
    } catch (err) {
        console.error('Remove from cart error:', err);
    }
}

function updateCartBadge(count) {
    const badges = document.querySelectorAll('.cart-badge-count');
    badges.forEach(b => {
        b.textContent = count;
        b.style.display = count > 0 ? 'inline-block' : 'none';
        b.classList.remove('badgePop');
        void b.offsetWidth; // trigger reflow
        b.classList.add('badgePop');
    });
}

/* ==========================================================================
   3. Wishlist Operations
   ========================================================================== */

async function toggleWishlist(productId, btnElement) {
    try {
        const response = await fetch('/api/wishlist/toggle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: productId })
        });
        const data = await response.json();
        if (data.success) {
            // Update button icon states
            if (btnElement) {
                const icon = btnElement.querySelector('i');
                if (data.in_wishlist) {
                    btnElement.classList.add('active-wishlist');
                    if (icon) {
                        icon.classList.remove('fa-regular');
                        icon.classList.add('fa-solid');
                    }
                } else {
                    btnElement.classList.remove('active-wishlist');
                    if (icon) {
                        icon.classList.remove('fa-solid');
                        icon.classList.add('fa-regular');
                    }
                }
            }

            // Update badge count
            const wishlistBadges = document.querySelectorAll('.wishlist-badge-count');
            wishlistBadges.forEach(b => {
                b.textContent = data.count;
                b.style.display = data.count > 0 ? 'inline-block' : 'none';
            });

            showToast(data.in_wishlist ? 'Wishlist' : 'Removed', data.message, 'info');

            // If on wishlist page and removed, remove element
            if (!data.in_wishlist && window.location.pathname.includes('/wishlist')) {
                const itemCard = btnElement.closest('.product-card');
                if (itemCard) {
                    itemCard.style.opacity = '0';
                    itemCard.style.transform = 'scale(0.8)';
                    setTimeout(() => itemCard.remove(), 300);
                }
            }
        }
    } catch (err) {
        console.error('Wishlist error:', err);
    }
}

/* ==========================================================================
   4. Slide-out Cart Drawer
   ========================================================================== */

function initGlobalCartDrawer() {
    const triggerBtns = document.querySelectorAll('.open-cart-drawer-btn');
    const overlay = document.getElementById('cart-drawer-overlay');
    const closeBtn = document.getElementById('cart-drawer-close');

    triggerBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            // If on full cart page, don't open drawer
            if (window.location.pathname === '/cart' || window.location.pathname === '/checkout') return;
            e.preventDefault();
            openCartDrawer();
        });
    });

    if (overlay) {
        overlay.addEventListener('click', closeCartDrawer);
    }
    if (closeBtn) {
        closeBtn.addEventListener('click', closeCartDrawer);
    }
}

function openCartDrawer() {
    const drawer = document.getElementById('cart-drawer');
    const overlay = document.getElementById('cart-drawer-overlay');
    if (drawer && overlay) {
        renderCartDrawer();
        drawer.classList.add('active');
        overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function closeCartDrawer() {
    const drawer = document.getElementById('cart-drawer');
    const overlay = document.getElementById('cart-drawer-overlay');
    if (drawer && overlay) {
        drawer.classList.remove('active');
        overlay.classList.remove('active');
        document.body.style.overflow = '';
    }
}

async function renderCartDrawer() {
    const body = document.getElementById('cart-drawer-items');
    const footer = document.getElementById('cart-drawer-footer');
    if (!body) return;

    body.innerHTML = `
        <div style="text-align: center; padding: 2rem;">
            <i class="fa-solid fa-spinner fa-spin" style="font-size: 2rem; color: var(--primary-color);"></i>
            <p style="margin-top: 0.5rem; color: var(--text-muted);">Loading cart...</p>
        </div>
    `;

    try {
        const response = await fetch('/api/cart');
        const data = await response.json();

        if (!data.cart || data.cart.length === 0) {
            body.innerHTML = `
                <div class="drawer-empty-state">
                    <i class="fa-solid fa-cart-shopping"></i>
                    <h3 style="font-weight: 700; margin-bottom: 0.5rem;">Your Cart is Empty</h3>
                    <p style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 1.5rem;">Explore top deals and add items you love!</p>
                    <button class="hero-btn" onclick="closeCartDrawer()" style="font-size: 0.9rem; padding: 0.6rem 1.2rem;">Shop Now</button>
                </div>
            `;
            if (footer) footer.style.display = 'none';
            return;
        }

        if (footer) footer.style.display = 'block';

        let html = '';
        data.cart.forEach(item => {
            html += `
                <div class="cart-item-row" style="grid-template-columns: 2fr 1fr auto; padding: 0.85rem 0; border-bottom: 1px solid #f1f5f9;">
                    <div style="display: flex; gap: 0.75rem; align-items: center;">
                        <img src="${item.image_url}" alt="${item.name}" class="cart-thumb" style="width: 55px; height: 55px;">
                        <div>
                            <div style="font-weight: 700; font-size: 0.88rem; line-height: 1.25;">${item.name}</div>
                            <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 2px;">
                                ${item.size ? `Size: ${item.size}` : ''} ${item.color ? `| Color: ${item.color}` : ''}
                            </div>
                            <div style="font-weight: 700; color: var(--primary-color); font-size: 0.9rem; margin-top: 3px;">
                                $${item.price.toFixed(2)}
                            </div>
                        </div>
                    </div>
                    <div class="stepper-box" style="transform: scale(0.85);">
                        <button class="stepper-btn" onclick="updateCartQuantity('${item.item_key}', ${item.quantity - 1})">-</button>
                        <input type="text" class="stepper-input" value="${item.quantity}" readonly>
                        <button class="stepper-btn" onclick="updateCartQuantity('${item.item_key}', ${item.quantity + 1})">+</button>
                    </div>
                    <button class="cart-item-remove-btn" onclick="removeFromCart('${item.item_key}')" title="Remove">
                        <i class="fa-solid fa-trash-can"></i>
                    </button>
                </div>
            `;
        });
        body.innerHTML = html;

        // Update footer totals
        const subtotalEl = document.getElementById('drawer-subtotal');
        const shippingEl = document.getElementById('drawer-shipping');
        const totalEl = document.getElementById('drawer-total');

        if (subtotalEl) subtotalEl.textContent = `$${data.totals.subtotal.toFixed(2)}`;
        if (shippingEl) shippingEl.textContent = data.totals.shipping === 0 ? 'FREE' : `$${data.totals.shipping.toFixed(2)}`;
        if (totalEl) totalEl.textContent = `$${data.totals.total.toFixed(2)}`;

    } catch (err) {
        console.error('Drawer render error:', err);
    }
}

/* ==========================================================================
   5. Coupon Application
   ========================================================================== */

async function applyCoupon() {
    const input = document.getElementById('coupon-code-input');
    if (!input || !input.value.trim()) {
        showToast('Notice', 'Please enter a coupon code', 'warning');
        return;
    }
    const code = input.value.trim().toUpperCase();

    try {
        const response = await fetch('/api/cart/apply-coupon', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code })
        });
        const data = await response.json();
        if (data.success) {
            showToast('Discount Applied!', data.message, 'success');
            setTimeout(() => window.location.reload(), 600);
        } else {
            showToast('Coupon Error', data.message, 'danger');
        }
    } catch (err) {
        console.error('Coupon apply error:', err);
    }
}

/* ==========================================================================
   6. Quick View Product Modal
   ========================================================================== */

let currentQuickViewProduct = null;

async function openQuickView(productId) {
    const modalBackdrop = document.getElementById('quickview-modal-backdrop');
    const modalContainer = document.getElementById('quickview-modal-content');
    if (!modalBackdrop || !modalContainer) return;

    modalBackdrop.classList.add('active');
    modalContainer.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 4rem;">
            <i class="fa-solid fa-spinner fa-spin" style="font-size: 2.5rem; color: var(--primary-color);"></i>
            <p style="margin-top: 1rem; color: var(--text-muted); font-weight: 600;">Loading product details...</p>
        </div>
    `;

    try {
        const response = await fetch(`/api/product/${productId}`);
        const data = await response.json();
        if (!data.success || !data.product) {
            showToast('Error', 'Product details not found', 'danger');
            closeQuickView();
            return;
        }

        const p = data.product;
        currentQuickViewProduct = p;

        let sizesHtml = '';
        if (p.sizes && p.sizes.length > 0) {
            sizesHtml = `
                <div class="selector-group">
                    <div class="selector-label">Select Option / Size: <span id="modal-selected-size" class="selector-selected-val">${p.sizes[0]}</span></div>
                    <div class="size-options-picker">
                        ${p.sizes.map((s, idx) => `
                            <button type="button" class="size-pill-btn ${idx === 0 ? 'active' : ''}" onclick="selectQuickViewSize(this, '${s}')">${s}</button>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        let colorsHtml = '';
        if (p.colors && p.colors.length > 0) {
            colorsHtml = `
                <div class="selector-group">
                    <div class="selector-label">Color: <span id="modal-selected-color" class="selector-selected-val">${p.colors[0].name}</span></div>
                    <div class="color-options-picker">
                        ${p.colors.map((c, idx) => `
                            <button type="button" class="color-option-btn ${idx === 0 ? 'active' : ''}" 
                                    style="background-color: ${c.hex};" 
                                    title="${c.name}" 
                                    onclick="selectQuickViewColor(this, '${c.name}')">
                            </button>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        let galleryHtml = '';
        if (p.gallery_urls && p.gallery_urls.length > 1) {
            galleryHtml = `
                <div style="display: flex; gap: 0.5rem; margin-top: 0.75rem;">
                    ${p.gallery_urls.map((imgUrl, i) => `
                        <img src="${imgUrl}" class="thumb-item ${i === 0 ? 'active' : ''}" 
                             style="width: 50px; height: 50px; object-fit: contain; cursor: pointer; border-radius: 4px; border: 1.5px solid #e2e8f0;" 
                             onclick="switchQuickViewImage(this, '${imgUrl}')">
                    `).join('')}
                </div>
            `;
        }

        modalContainer.innerHTML = `
            <button class="modal-close-btn" onclick="closeQuickView()"><i class="fa-solid fa-xmark"></i></button>
            <div style="background: #f8fafc; padding: 2rem; display: flex; flex-direction: column; align-items: center; justify-content: center; border-right: 1px solid var(--border-color);">
                <img id="quickview-main-img" src="${p.image_url}" alt="${p.name}" style="max-height: 320px; object-fit: contain;">
                ${galleryHtml}
            </div>
            <div style="padding: 2rem; display: flex; flex-direction: column;">
                <span class="product-category-tag">${p.category_name || 'Electronics'}</span>
                <h3 style="font-size: 1.35rem; font-weight: 800; margin-bottom: 0.5rem; line-height: 1.3;">${p.name}</h3>
                
                <div class="product-rating-row" style="margin-bottom: 1rem;">
                    <span class="rating-badge">${p.rating} <i class="fa-solid fa-star"></i></span>
                    <span class="rating-count">(${p.review_count} verified reviews)</span>
                </div>

                <div class="product-price-row" style="margin-bottom: 1rem;">
                    <span class="current-price" style="font-size: 1.75rem;">$${p.price.toFixed(2)}</span>
                    ${p.original_price ? `<span class="original-price">$${p.original_price.toFixed(2)}</span>` : ''}
                    ${p.discount_percent ? `<span class="discount-tag">${p.discount_percent}% OFF</span>` : ''}
                </div>

                <p style="font-size: 0.88rem; color: var(--text-muted); margin-bottom: 1.25rem; line-height: 1.5;">${p.description}</p>

                ${sizesHtml}
                ${colorsHtml}

                <div class="quantity-row" style="margin-bottom: 1.5rem;">
                    <span style="font-weight: 700; font-size: 0.9rem;">Qty:</span>
                    <div class="stepper-box">
                        <button class="stepper-btn" onclick="stepModalQty(-1)">-</button>
                        <input type="text" id="modal-qty-input" class="stepper-input" value="1" readonly>
                        <button class="stepper-btn" onclick="stepModalQty(1)">+</button>
                    </div>
                    <span class="stock-status"><i class="fa-solid fa-circle-check"></i> In Stock</span>
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-top: auto;">
                    <button class="btn-large-cart" style="padding: 0.75rem; font-size: 0.95rem;" onclick="submitModalAddToCart()">
                        <i class="fa-solid fa-cart-shopping"></i> Add to Cart
                    </button>
                    <button class="btn-large-buy" style="padding: 0.75rem; font-size: 0.95rem;" onclick="submitModalBuyNow()">
                        <i class="fa-solid fa-bolt"></i> Buy Now
                    </button>
                </div>
                
                <div style="margin-top: 1rem; text-align: center;">
                    <a href="/product/${p.id}" style="color: var(--primary-color); font-weight: 700; font-size: 0.88rem;">View Full Product Details & Specs →</a>
                </div>
            </div>
        `;

    } catch (err) {
        console.error('Quick view error:', err);
    }
}

function closeQuickView() {
    const modalBackdrop = document.getElementById('quickview-modal-backdrop');
    if (modalBackdrop) {
        modalBackdrop.classList.remove('active');
    }
    currentQuickViewProduct = null;
}

function selectQuickViewSize(btn, size) {
    const container = btn.closest('.size-options-picker');
    container.querySelectorAll('.size-pill-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const label = document.getElementById('modal-selected-size');
    if (label) label.textContent = size;
}

function selectQuickViewColor(btn, colorName) {
    const container = btn.closest('.color-options-picker');
    container.querySelectorAll('.color-option-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const label = document.getElementById('modal-selected-color');
    if (label) label.textContent = colorName;
}

function switchQuickViewImage(thumb, imgUrl) {
    const mainImg = document.getElementById('quickview-main-img');
    if (mainImg) mainImg.src = imgUrl;
    const parent = thumb.parentElement;
    parent.querySelectorAll('.thumb-item').forEach(t => t.style.borderColor = '#e2e8f0');
    thumb.style.borderColor = 'var(--primary-color)';
}

function stepModalQty(delta) {
    const input = document.getElementById('modal-qty-input');
    if (!input) return;
    let val = parseInt(input.value) || 1;
    val += delta;
    if (val < 1) val = 1;
    if (val > 10) val = 10;
    input.value = val;
}

function submitModalAddToCart() {
    if (!currentQuickViewProduct) return;
    const size = document.getElementById('modal-selected-size')?.textContent || '';
    const color = document.getElementById('modal-selected-color')?.textContent || '';
    const qty = parseInt(document.getElementById('modal-qty-input')?.value) || 1;
    closeQuickView();
    addToCart(currentQuickViewProduct.id, qty, size, color, true);
}

function submitModalBuyNow() {
    if (!currentQuickViewProduct) return;
    const size = document.getElementById('modal-selected-size')?.textContent || '';
    const color = document.getElementById('modal-selected-color')?.textContent || '';
    const qty = parseInt(document.getElementById('modal-qty-input')?.value) || 1;
    closeQuickView();
    buyNow(currentQuickViewProduct.id, qty, size, color);
}

/* ==========================================================================
   7. Hero Banner Slider Carousel
   ========================================================================== */

function initHeroSlider() {
    const slides = document.querySelectorAll('.hero-slide');
    const dots = document.querySelectorAll('.slider-dot');
    const prevBtn = document.querySelector('.slider-arrow.prev');
    const nextBtn = document.querySelector('.slider-arrow.next');

    if (!slides.length) return;

    let currentIndex = 0;
    let slideTimer = null;

    function goToSlide(index) {
        slides.forEach(s => s.classList.remove('active'));
        dots.forEach(d => d.classList.remove('active'));

        currentIndex = (index + slides.length) % slides.length;
        slides[currentIndex].classList.add('active');
        if (dots[currentIndex]) {
            dots[currentIndex].classList.add('active');
        }
    }

    function startAutoSlide() {
        stopAutoSlide();
        slideTimer = setInterval(() => {
            goToSlide(currentIndex + 1);
        }, 5000);
    }

    function stopAutoSlide() {
        if (slideTimer) clearInterval(slideTimer);
    }

    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            goToSlide(currentIndex - 1);
            startAutoSlide();
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            goToSlide(currentIndex + 1);
            startAutoSlide();
        });
    }

    dots.forEach((dot, idx) => {
        dot.addEventListener('click', () => {
            goToSlide(idx);
            startAutoSlide();
        });
    });

    startAutoSlide();
}

/* ==========================================================================
   8. Search Autocomplete
   ========================================================================== */

function initSearchAutocomplete() {
    const input = document.getElementById('header-search-input');
    const box = document.getElementById('search-suggestions-box');
    if (!input || !box) return;

    let debounceTimeout = null;

    input.addEventListener('input', () => {
        clearTimeout(debounceTimeout);
        const query = input.value.trim();

        if (query.length < 2) {
            box.classList.remove('active');
            box.innerHTML = '';
            return;
        }

        debounceTimeout = setTimeout(async () => {
            try {
                const res = await fetch(`/api/search/suggestions?q=${encodeURIComponent(query)}`);
                const data = await res.json();

                if (data.results && data.results.length > 0) {
                    let html = '';
                    data.results.forEach(item => {
                        html += `
                            <a href="/product/${item.id}" class="suggestion-item">
                                <img src="${item.image}" alt="${item.name}">
                                <div class="suggestion-info">
                                    <div class="suggestion-title">${item.name}</div>
                                    <div class="suggestion-meta">${item.category}</div>
                                </div>
                                <div class="suggestion-price">${item.price}</div>
                            </a>
                        `;
                    });
                    box.innerHTML = html;
                    box.classList.add('active');
                } else {
                    box.classList.remove('active');
                }
            } catch (err) {
                console.error('Search suggestions error:', err);
            }
        }, 250);
    });

    document.addEventListener('click', (e) => {
        if (!input.contains(e.target) && !box.contains(e.target)) {
            box.classList.remove('active');
        }
    });
}

/* ==========================================================================
   9. Color & Size Pickers (Product Detail & Card)
   ========================================================================== */

function initColorAndSizePickers() {
    // Product Detail Size Pills
    document.querySelectorAll('.detail-size-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const container = this.closest('.size-options-picker');
            container.querySelectorAll('.detail-size-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            const targetLabel = document.getElementById('selected-size-label');
            if (targetLabel) targetLabel.textContent = this.dataset.size;
        });
    });

    // Product Detail Color Swatches
    document.querySelectorAll('.detail-color-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const container = this.closest('.color-options-picker');
            container.querySelectorAll('.detail-color-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            const targetLabel = document.getElementById('selected-color-label');
            if (targetLabel) targetLabel.textContent = this.dataset.color;
        });
    });
}

/* ==========================================================================
   10. Quantity Steppers
   ========================================================================== */

function initQuantitySteppers() {
    document.querySelectorAll('.quantity-stepper-component').forEach(stepper => {
        const minus = stepper.querySelector('.btn-qty-minus');
        const plus = stepper.querySelector('.btn-qty-plus');
        const input = stepper.querySelector('.input-qty-val');

        if (minus && plus && input) {
            minus.addEventListener('click', () => {
                let v = parseInt(input.value) || 1;
                if (v > 1) {
                    input.value = v - 1;
                }
            });
            plus.addEventListener('click', () => {
                let v = parseInt(input.value) || 1;
                if (v < 10) {
                    input.value = v + 1;
                }
            });
        }
    });
}

/* ==========================================================================
   11. Product Detail Gallery Switcher
   ========================================================================== */

function initProductDetailGallery() {
    const thumbs = document.querySelectorAll('.detail-thumb');
    const mainImg = document.getElementById('detail-main-image');

    if (!thumbs.length || !mainImg) return;

    thumbs.forEach(thumb => {
        thumb.addEventListener('click', function() {
            thumbs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            const newSrc = this.getAttribute('data-full-img');
            if (newSrc) {
                mainImg.src = newSrc;
            }
        });
    });
}

/* ==========================================================================
   12. Tabs (Specifications vs Reviews)
   ========================================================================== */

function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-nav-btn');
    const panes = document.querySelectorAll('.tab-content-pane');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            tabBtns.forEach(b => b.classList.remove('active'));
            panes.forEach(p => p.classList.remove('active'));

            this.classList.add('active');
            const targetPane = document.getElementById(targetId);
            if (targetPane) {
                targetPane.classList.add('active');
            }
        });
    });
}

/* ==========================================================================
   13. Customer Review Form
   ========================================================================== */

function initReviewForm() {
    const starContainer = document.getElementById('interactive-star-rating');
    const stars = starContainer ? starContainer.querySelectorAll('i') : [];
    const ratingInput = document.getElementById('review-rating-value');
    const reviewForm = document.getElementById('product-review-form');

    if (stars.length && ratingInput) {
        stars.forEach(star => {
            star.addEventListener('mouseover', function() {
                const hoverVal = parseInt(this.getAttribute('data-rating'));
                stars.forEach(s => {
                    const r = parseInt(s.getAttribute('data-rating'));
                    if (r <= hoverVal) {
                        s.classList.add('hovered');
                    } else {
                        s.classList.remove('hovered');
                    }
                });
            });

            star.addEventListener('mouseout', function() {
                stars.forEach(s => s.classList.remove('hovered'));
            });

            star.addEventListener('click', function() {
                const selectedVal = parseInt(this.getAttribute('data-rating'));
                ratingInput.value = selectedVal;
                stars.forEach(s => {
                    const r = parseInt(s.getAttribute('data-rating'));
                    if (r <= selectedVal) {
                        s.classList.add('selected');
                        s.classList.remove('fa-regular');
                        s.classList.add('fa-solid');
                    } else {
                        s.classList.remove('selected');
                        s.classList.remove('fa-solid');
                        s.classList.add('fa-regular');
                    }
                });
            });
        });
    }

    if (reviewForm) {
        reviewForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const productId = this.getAttribute('data-product-id');
            const author = document.getElementById('review-author-name').value.trim();
            const rating = parseInt(document.getElementById('review-rating-value').value) || 5;
            const title = document.getElementById('review-title-input').value.trim();
            const comment = document.getElementById('review-comment-input').value.trim();

            if (!author || !comment) {
                showToast('Validation Error', 'Please enter your name and comments', 'warning');
                return;
            }

            try {
                const res = await fetch(`/api/reviews/${productId}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        author_name: author,
                        rating: rating,
                        title: title,
                        comment: comment
                    })
                });

                const data = await res.json();
                if (data.success) {
                    showToast('Review Submitted', data.message, 'success');

                    // Prepend new review card
                    const list = document.getElementById('customer-reviews-container');
                    if (list) {
                        const newCard = document.createElement('div');
                        newCard.className = 'review-item-card';

                        let starsHtml = '';
                        for (let i = 1; i <= 5; i++) {
                            starsHtml += `<i class="fa-${i <= rating ? 'solid' : 'regular'} fa-star"></i>`;
                        }

                        newCard.innerHTML = `
                            <div class="review-header">
                                <div class="reviewer-meta">
                                    <div class="reviewer-avatar">${author.charAt(0).toUpperCase()}</div>
                                    <div>
                                        <div class="reviewer-name">${author}</div>
                                        <span class="verified-badge"><i class="fa-solid fa-circle-check"></i> Verified Buyer</span>
                                    </div>
                                </div>
                                <div class="review-stars">${starsHtml}</div>
                            </div>
                            ${title ? `<div class="review-title">${title}</div>` : ''}
                            <div class="review-comment">${comment}</div>
                        `;
                        list.prepend(newCard);
                    }

                    // Reset form
                    reviewForm.reset();
                    if (ratingInput) ratingInput.value = '5';
                    stars.forEach((s, idx) => {
                        s.classList.remove('selected', 'fa-regular');
                        s.classList.add('fa-solid');
                    });
                } else {
                    showToast('Error', data.message, 'danger');
                }
            } catch (err) {
                console.error('Submit review error:', err);
                showToast('Error', 'Failed to submit review', 'danger');
            }
        });
    }
}
