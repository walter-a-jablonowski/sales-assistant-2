import sqlite3
from datetime import datetime, timedelta
import random

def init_database():
  conn = sqlite3.connect('sales.db')
  cursor = conn.cursor()
  
  cursor.execute('DROP TABLE IF EXISTS order_items')
  cursor.execute('DROP TABLE IF EXISTS orders')
  cursor.execute('DROP TABLE IF EXISTS products')
  cursor.execute('DROP TABLE IF EXISTS customers')
  
  cursor.execute('''
    CREATE TABLE customers
    (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      email TEXT NOT NULL,
      phone TEXT,
      city TEXT,
      country TEXT,
      created_at TEXT NOT NULL
    )
  ''')
  
  cursor.execute('''
    CREATE TABLE products
    (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      category TEXT NOT NULL,
      price REAL NOT NULL,
      stock_quantity INTEGER NOT NULL,
      created_at TEXT NOT NULL
    )
  ''')
  
  cursor.execute('''
    CREATE TABLE orders
    (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      customer_id INTEGER NOT NULL,
      order_date TEXT NOT NULL,
      status TEXT NOT NULL,
      amount_sum REAL NOT NULL,
      FOREIGN KEY (customer_id) REFERENCES customers(id)
    )
  ''')
  
  cursor.execute('''
    CREATE TABLE order_items
    (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      order_id INTEGER NOT NULL,
      product_id INTEGER NOT NULL,
      quantity INTEGER NOT NULL,
      unit_price REAL NOT NULL,
      subsum REAL NOT NULL,
      FOREIGN KEY (order_id) REFERENCES orders(id),
      FOREIGN KEY (product_id) REFERENCES products(id)
    )
  ''')
  
  customers = [
    ('Acme Corporation', 'contact@acme.com', '+1-555-0101', 'New York', 'USA'),
    ('Global Tech Solutions', 'info@globaltech.com', '+1-555-0102', 'San Francisco', 'USA'),
    ('European Imports Ltd', 'sales@euroimports.com', '+44-20-5550103', 'London', 'UK'),
    ('Asia Pacific Trading', 'orders@aptrading.com', '+65-5550104', 'Singapore', 'Singapore'),
    ('Midwest Manufacturing', 'purchasing@midwest.com', '+1-555-0105', 'Chicago', 'USA'),
    ('Coastal Distributors', 'info@coastal.com', '+1-555-0106', 'Miami', 'USA'),
    ('Northern Enterprises', 'contact@northern.com', '+1-555-0107', 'Toronto', 'Canada'),
    ('Southern Supplies Co', 'sales@southern.com', '+1-555-0108', 'Atlanta', 'USA'),
    ('Pacific Rim Industries', 'orders@pacificrim.com', '+61-2-5550109', 'Sydney', 'Australia'),
    ('Alpine Trading GmbH', 'info@alpine.de', '+49-89-5550110', 'Munich', 'Germany'),
  ]
  
  base_date = datetime.now() - timedelta(days=365)
  for i, (name, email, phone, city, country) in enumerate(customers):
    created = base_date + timedelta(days=i*30)
    cursor.execute(
      'INSERT INTO customers (name, email, phone, city, country, created_at) VALUES (?, ?, ?, ?, ?, ?)',
      (name, email, phone, city, country, created.isoformat())
    )
  
  products = [
    ('Laptop Pro 15"', 'Electronics', 1299.99, 45),
    ('Wireless Mouse', 'Electronics', 29.99, 200),
    ('USB-C Hub', 'Electronics', 49.99, 150),
    ('Office Chair Deluxe', 'Furniture', 399.99, 30),
    ('Standing Desk', 'Furniture', 599.99, 25),
    ('Monitor 27" 4K', 'Electronics', 449.99, 60),
    ('Keyboard Mechanical', 'Electronics', 129.99, 100),
    ('Desk Lamp LED', 'Furniture', 79.99, 80),
    ('Webcam HD', 'Electronics', 89.99, 120),
    ('Headphones Noise-Canceling', 'Electronics', 249.99, 75),
    ('Tablet 10"', 'Electronics', 499.99, 50),
    ('Printer All-in-One', 'Electronics', 299.99, 40),
    ('Paper A4 (500 sheets)', 'Office Supplies', 8.99, 500),
    ('Pen Set (12 pack)', 'Office Supplies', 12.99, 300),
    ('Bundle', 'Office Supplies', 19.99, 250),
  ]
  
  for i, (name, category, price, stock) in enumerate(products):
    created = base_date + timedelta(days=i*5)
    cursor.execute(
      'INSERT INTO products (name, category, price, stock_quantity, created_at) VALUES (?, ?, ?, ?, ?)',
      (name, category, price, stock, created.isoformat())
    )
  
  order_statuses = ['completed', 'completed', 'completed', 'completed', 'processing', 'shipped']
  
  order_id = 1
  for days_ago in range(180, 0, -7):
    num_orders = random.randint(2, 5)
    for _ in range(num_orders):
      customer_id = random.randint(1, 10)
      order_date = datetime.now() - timedelta(days=days_ago + random.randint(0, 6))
      status = random.choice(order_statuses)
      
      num_items = random.randint(1, 5)
      amount_sum = 0
      order_items_data = []
      
      selected_products = random.sample(range(1, 16), num_items)
      for product_id in selected_products:
        cursor.execute('SELECT price FROM products WHERE id = ?', (product_id,))
        unit_price = cursor.fetchone()[0]
        quantity = random.randint(1, 10)
        subsum = unit_price * quantity
        amount_sum += subsum
        order_items_data.append((product_id, quantity, unit_price, subsum))
      
      cursor.execute(
        'INSERT INTO orders (customer_id, order_date, status, amount_sum) VALUES (?, ?, ?, ?)',
        (customer_id, order_date.isoformat(), status, round(amount_sum, 2))
      )
      
      for product_id, quantity, unit_price, subsum in order_items_data:
        cursor.execute(
          'INSERT INTO order_items (order_id, product_id, quantity, unit_price, subsum) VALUES (?, ?, ?, ?, ?)',
          (order_id, product_id, quantity, unit_price, round(subsum, 2))
        )
      
      order_id += 1
  
  conn.commit()
  conn.close()
  
  print('Database initialized successfully!')
  print(f'Created {len(customers)} customers')
  print(f'Created {len(products)} products')
  print(f'Created {order_id - 1} orders with multiple order items')

if __name__ == '__main__':
  init_database()
