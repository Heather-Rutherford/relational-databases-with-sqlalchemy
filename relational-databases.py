# Instructions:
# 1. Use Python and SQLAlchemy to complete this assignment.
# 2. Make sure you have SQLAlchemy installed (pip install SQLAlchemy).
# 3. Use SQLite for simplicity (sqlite:///example.db).
# 4. Submit your Python script (.py) with all the steps completed.

# Part 1: Setup
# 1. Import necessary modules from SQLAlchemy:
from sqlalchemy import Select, create_engine, Column, Integer, String, ForeignKey, Boolean, func, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Relationship, Session, Mapped, mapped_column, DeclarativeBase, relationship
from typing import List, Optional

# 2. Create an engine and base:
engine = create_engine('sqlite:///shop.db')
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

# Base class for models
class Base(DeclarativeBase):
    pass

# Part 2: Define Tables
# 1. Create a User table with:
#   -- id (primary key)
#   -- name (string)
#   -- email (string, unique)
# Set up relationships: 
# Hint: Use relationship() in the tables 
# to define these connections.
#   -- A User can have many Orders
class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), unique=True)

    # One-to-Many: User -> List of Order objects
    # This is a relationship attribute, not a column in the database
    orders: Mapped[List["Order"]] = relationship(back_populates="user", cascade="all, delete-orphan")

# 2. Create a Product table with:
#   -- id (primary key)
#   -- name (string)
#   -- price (integer)
# Set up relationships:
# Hint: Use relationship() in the tables 
# to define these connections.
#   -- A Product can appear in many Orders
class Product(Base):
    __tablename__ = 'product'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    price: Mapped[int] = mapped_column(Integer)
    
    # One-to-Many: Product -> List of Order objects
    # This is a relationship attribute, not a column in the database
    # orders is a list of Order objects associated with this Product
    orders: Mapped[List["Order"]] = relationship(back_populates="product", cascade="all, delete-orphan")
                        
# 3. Create an Order table with:
#   -- id (primary key)
#   -- user_id (foreign key referencing User.id)
#   -- product_id (foreign key referencing Product.id)
#   -- quantity (integer)
class Order(Base):
    __tablename__ = 'orders'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('product.id'))
    quantity: Mapped[int] = mapped_column(Integer)
    
    # Many-to-One: Order -> User
    user: Mapped['User'] = relationship(back_populates="orders")
    # Many-to-One: Order -> Product
    product: Mapped['Product'] = relationship(back_populates="orders")
    
# Part 3: Create Tables
# 1. Use Base.metadata.create_all() to create the tables 
# in the database.
Base.metadata.create_all(engine)

# Part 4: Insert Data
# Add at least 2 users, 3 products, and 4 orders with different quantities.
session = Session(engine)

# Adding Users
user1 = User(name='Rebecca', email='rebecca@example.com')
user2 = User(name='Rachel', email='rachel@example.com')
user3 = User(name='Jonathan', email='jonathan@example.com')
session.add_all([user1, user2, user3])

# Adding Products
product1 = Product(name='Laptop', price=1000)
product2 = Product(name='Smartphone', price=500)   
product3 = Product(name='Kindle', price=300)
session.add_all([product1, product2, product3])

# Adding Orders
order1 = Order(user=user1, product=product1, quantity=1)
order2 = Order(user=user1, product=product2, quantity=2)
order3 = Order(user=user2, product=product3, quantity=1)
order4 = Order(user=user2, product=product2, quantity=3)
session.add_all([order1, order2, order3, order4])
session.commit()

# Part 5: Queries
# Write Python code to:

# 1. Retrieve all users and print their information.
queryAllUsers = select(User)
users = session.execute(queryAllUsers).scalars().all()
for user in users:
    print(f"User ID: {user.id}, Name: {user.name}, Email: {user.email}.")
    
# 2. Retrieve all products and print their name and price.
queryAllProducts = select(Product)
products = session.execute(queryAllProducts).scalars().all()
for product in products:
    print(f"Product Name: {product.name}, Price: {product.price}.")
    
# 3. Retrieve all orders, showing the user’s name, product name, and quantity.
queryAllOrders = (
    select(User.name, Product.name, Order.quantity)
    .join(Order, User.id == Order.user_id)
    .join(Product, Product.id == Order.product_id)
)
queryAllOrdersResults = session.execute(queryAllOrders).all()
for user_name, product_name, quantity in queryAllOrdersResults:
    print(f"User: {user_name}, Product: {product_name}, Quantity: {quantity}.")
    
# 4. Update a product’s price.
queryUpdateProductPrice = select(Product).where(Product.name == 'Kindle')
queryUpdateProductPriceResult = session.execute(queryUpdateProductPrice).scalars().first()
queryUpdateProductPriceResult.price = 150
session.commit()

# 5. Delete a user by ID.
queryDeleteUser = session.get(User, 2)  # Assuming we want to delete user with ID 2
if queryDeleteUser:
    session.delete(queryDeleteUser)
    session.commit()

# Part 6: Bonus (Optional)
# -- Add a status column to the Order table
# (Boolean to represent shipped or not).
class Order(Base):
    __tablename__ = 'orders'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('product.id'))
    quantity: Mapped[int] = mapped_column(Integer)
    shipped: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Many-to-One: Order -> User
    user: Mapped['User'] = relationship(back_populates="orders")
    # Many-to-One: Order -> Product
    product: Mapped['Product'] = relationship(back_populates="orders")

queryAlterOrdersTable = "ALTER TABLE orders add COLUMN shipped BOOLEAN DEFAULT 0"
with engine.connect() as conn:
    conn.execute(queryAlterOrdersTable)
    conn.commit()
    
# -- Query all orders that are not shipped.
queryUnshippedOrders = select(Order).where(Order.shipped == False)
unshippedOrders = session.execute(queryUnshippedOrders).scalars().all()
for order in unshippedOrders:
    print(f"Unshipped OrderID: {order.id}, UserID: {order.user_id}, ProductID: {order.product_id}, Quantity: {order.quantity}.")
    
# -- Count the total number of orders per user.
queryAllUsersOrdersCount = (
    select(User.name, func.count(Order.id))
    .join(Order, User.id == Order.user_id)
    .group_by(User.id)
)
usersOrdersCount = session.execute(queryAllUsersOrdersCount).all()
for user_name, order_count in usersOrdersCount:
    print(f"User: {user_name}, Total Orders: {order_count}.")

# Close the session
session.close()