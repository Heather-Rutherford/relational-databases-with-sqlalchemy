# Instructions:
# 1. Use Python and SQLAlchemy to complete this assignment.
# 2. Make sure you have SQLAlchemy installed (pip install SQLAlchemy).
# 3. Use SQLite for simplicity (sqlite:///example.db).
# 4. Submit your Python script (.py) with all the steps completed.

# Part 1: Setup
# 1. Import necessary modules from SQLAlchemy:
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean
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
# 2. Retrieve all products and print their name and price.
# 3. Retrieve all orders, showing the user’s name, product name, and quantity.
# 4. Update a product’s price.
# 5. Delete a user by ID.

# Part 6: Bonus (Optional)
# -- Add a status column to the Order table (Boolean to represent shipped or not).
# -- Query all orders that are not shipped.
# -- Count the total number of orders per user.