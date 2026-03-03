import sqlite3

conn = sqlite3.connect('products.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    image_url TEXT
)
''')

products = [
    ("Red Sneakers", "Comfortable running shoes", 79.99, "static/images/sneakers1.jpg"),
    ("Blue T-Shirt", "100% Cotton T-shirt", 19.99, "static/images/tshirt1.jpg"),
    ("Smart Watch", "Fitness tracking watch", 149.99, "static/images/watch1.jpg")
]

c.executemany(
    "INSERT INTO products (name, description, price, image_url) VALUES (?, ?, ?, ?)",
    products
)

conn.commit()
conn.close()

print("Database initialized successfully!")