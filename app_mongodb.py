from flask import Flask, jsonify, session, request
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MongoDB configuration
client = MongoClient('mongodb://localhost:27017/')
db = client['ecommerce']
products_collection = db['products']
orders_collection = db['orders']

@app.route('/')
def index():
    return jsonify(message="Welcome to the e-commerce application!")

@app.route('/products', methods=['GET'])
def get_products():
    products = list(products_collection.find({}, {'_id': 0}))
    return jsonify(products=products)

#JSON data for POST method
# {
#   "product_id": 101,
#   "name": "New Product",
#   "price": 24.99,
#   "description": "Description of the new product",
#   "image_url": "new_product.jpg"
# }

@app.route('/products', methods=['POST'])
def add_product():
    product = request.get_json()
    result = products_collection.insert_one(product)
    return jsonify(message=f"Product added successfully with ID '{result.inserted_id}'!")

@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = request.get_json()
    print("product_id"+str(product_id))
    result = products_collection.update_one({'product_id': product_id}, {'$set': product})
    print(result)
    if result:
        return jsonify(message=f"Product with ID '{product_id}' updated successfully!")
    else:
        return jsonify(error=f"Product with ID '{product_id}' does not exist!")

@app.route('/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = products_collection.find_one({'id': product_id})
    if product:
        if 'cart' not in session:
            session['cart'] = []
        session['cart'].append(product)
        return jsonify(message=f"Product '{product['name']}' added to cart successfully!")
    else:
        return jsonify(error=f"Product with ID '{product_id}' does not exist!")

@app.route('/cart', methods=['GET'])
def view_cart():
    if 'cart' in session:
        cart = session['cart']
        total_price = sum(product['price'] for product in cart)
        return jsonify(cart=cart, total_price=total_price)
    else:
        return jsonify(message="Your cart is empty!")

@app.route('/cart', methods=['DELETE'])
def clear_cart():
    if 'cart' in session:
        session.pop('cart')
        return jsonify(message="Cart cleared successfully!")
    else:
        return jsonify(message="Your cart is already empty!")

@app.route('/orders', methods=['POST'])
def place_order():
    if 'cart' in session:
        cart = session.pop('cart')
        result = orders_collection.insert_one({'cart': cart})
        return jsonify(message="Order placed successfully! Your cart has been cleared.")
    else:
        return jsonify(message="Your cart is empty!")

@app.route('/orders', methods=['GET'])
def get_orders():
    orders = list(orders_collection.find({}, {'_id': 0}))
    return jsonify(orders=orders)

@app.route('/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    order = request.get_json()
    result = orders_collection.update_one({'id': order_id}, {'$set': order})
    if result.modified_count == 1:
        return jsonify(message=f"Order with ID '{order_id}' updated successfully!")
    else:
        return jsonify(error=f"Order with ID '{order_id}' does not exist!")

if __name__ == '__main__':
    app.run()
