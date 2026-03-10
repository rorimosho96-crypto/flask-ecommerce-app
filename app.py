from flask import Flask, render_template, session, redirect, url_for
from flask_session import Session
import sqlite3
import stripe

app = Flask(__name__)
app.secret_key = "supersecretkey"

import os
import stripe
stripe.api_key = os.environ.get("STRIPE_SECERET_KEY")

def get_products():
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    products = c.fetchall()
    conn.close()
    return products

@app.route('/')
def index():
    products = get_products()
    return render_template('index.html', products=products)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if "cart" not in session:
        session["cart"] = {}

    cart = session["cart"]

    if str(product_id) in cart:
        cart[str(product_id)] += 1
    else:
        cart[str(product_id)] = 1

    session["cart"] = cart
    return redirect(url_for('index'))

@app.route('/cart')
def cart():
    cart_items = []
    total = 0

    if "cart" in session:
        conn = sqlite3.connect('products.db')
        c = conn.cursor()

        for pid, qty in session["cart"].items():
            c.execute("SELECT * FROM products WHERE id=?", (pid,))
            product = c.fetchone()

            if product:
                subtotal = qty * product[3]
                total += subtotal

                cart_items.append({
                    "id": product[0],
                    "name": product[1],
                    "price": product[3],
                    "quantity": qty,
                    "subtotal": subtotal
                })

        conn.close()

    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/update_cart/<int:product_id>/<action>')
def update_cart(product_id, action):
    if "cart" in session:
        cart = session["cart"]
        pid = str(product_id)

        if pid in cart:
            if action == "add":
                cart[pid] += 1
            elif action == "subtract":
                cart[pid] -= 1
                if cart[pid] <= 0:
                    del cart[pid]
            elif action == "remove":
                del cart[pid]

        session["cart"] = cart

    return redirect(url_for('cart'))

@app.route('/checkout')
def checkout():
    if "cart" not in session or not session["cart"]:
        return redirect(url_for('index'))

    line_items = []
    conn = sqlite3.connect('products.db')
    c = conn.cursor()

    for pid, qty in session["cart"].items():
        c.execute("SELECT * FROM products WHERE id=?", (pid,))
        product = c.fetchone()
        if product:
            line_items.append({
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": product[1],
                    },
                    "unit_amount": int(product[3] * 100),
                },
                "quantity": qty,
            })
    conn.close()

    session["cart"] = {}

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=line_items,
        mode="payment",
        success_url=url_for('success', _external=True),
        cancel_url=url_for('cart', _external=True)
    )

    return redirect(checkout_session.url, code=303)

@app.route('/success')
def success():
    session.pop("cart", None)   # clears cart after payment
    return render_template("success.html")

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)