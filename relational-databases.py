# Instructions:
# 1. Use Python and SQLAlchemy to complete this assignment.
# 2. Make sure you have SQLAlchemy installed (pip install SQLAlchemy).
# 3. Use SQLite for simplicity (sqlite:///example.db).
# 4. Submit your Python script (.py) with all the steps completed.

# Part 1: Setup
# 1. Import necessary modules from SQLAlchemy:
from decimal import Decimal
from sqlalchemy import Numeric, create_engine, Integer, String, ForeignKey, Boolean, func, select
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import List, Optional

# 2. Create an engine
engine = create_engine('sqlite:///shop.db')

# 3. Define a declarative base
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
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    
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
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    quantity: Mapped[int] = mapped_column(Integer)
    # Part 6: Bonus (Optional) - Add a status column to the Order table (Boolean to represent shipped or not).
    shipped: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Many-to-One: Order -> User
    user: Mapped['User'] = relationship(back_populates="orders")
    # Many-to-One: Order -> Product
    product: Mapped['Product'] = relationship(back_populates="orders")
    
# Part 3: Create Tables
# 1. Use Base.metadata.create_all() to create the tables 
# in the database.
Base.metadata.create_all(engine)

# Create a session to interact with the database.
Session = sessionmaker(bind=engine)

# Part 4: Insert Data
# Add at least 2 users, 3 products, and 4 orders with different quantities.
with Session() as session:
    try:
        # Adding Users
        user1 = User(name='Rebecca', email='rebecca@example.com')
        user2 = User(name='Rachel', email='rachel@example.com')
        user3 = User(name='Jonathan', email='jonathan@example.com')
        session.add_all([user1, user2, user3])

        # Adding Products
        product1 = Product(name='Laptop', price=Decimal('1000.00'))
        product2 = Product(name='Smartphone', price=Decimal('500.00'))   
        product3 = Product(name='Kindle', price=Decimal('300.00'))
        session.add_all([product1, product2, product3])

        # Adding Orders
        order1 = Order(user=user1, product=product1, quantity=1, shipped=True)
        order2 = Order(user=user1, product=product2, quantity=2, shipped=False)
        order3 = Order(user=user3, product=product3, quantity=1, shipped=False)
        order4 = Order(user=user2, product=product2, quantity=3, shipped=True)
        session.add_all([order1, order2, order3, order4])
        session.commit()
        print("✓ Data inserted successfully")
    except IntegrityError as e:
        session.rollback()
        print(f"✗ Error: Duplicate or invalid data - {e.orig}")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"✗ Database error during insert: {e}")

    # Part 5: Queries
    # Write Python code to:

    # 1. Retrieve all users and print their information.
    try:
        queryAllUsers = select(User)
        users = session.execute(queryAllUsers).scalars().all()
        print("\nAll Users:")
        for user in users:
            print(f"User ID: {user.id}, Name: {user.name}, Email: {user.email}.")
    except SQLAlchemyError as e:
        print(f"✗ Error retrieving users: {e}")
        
    # 2. Retrieve all products and print their name and price.
    try:
        queryAllProducts = select(Product)
        products = session.execute(queryAllProducts).scalars().all()
        print("\nAll Products:")
        for product in products:
            print(f"Product Name: {product.name}, Price: {product.price}.")
    except SQLAlchemyError as e:
        print(f"✗ Error retrieving products: {e}")
        
    # 3. Retrieve all orders, showing the user's name, product name, and quantity.
    try:
        queryAllOrders = (
            select(User.name, Product.name, Order.quantity)
            .join(Order, User.id == Order.user_id)
            .join(Product, Product.id == Order.product_id)
        )
        queryAllOrdersResults = session.execute(queryAllOrders).all()
        print("\nAll Orders:")
        for user_name, product_name, quantity in queryAllOrdersResults:
            print(f"User: {user_name}, Product: {product_name}, Quantity: {quantity}.")
    except SQLAlchemyError as e:
        print(f"✗ Error retrieving orders: {e}")
        
    # 4. Update a product's price.
    try:
        queryUpdateProductPrice = select(Product).where(Product.name == 'Kindle')
        queryUpdateProductPriceResult = session.execute(queryUpdateProductPrice).scalars().first()
        if queryUpdateProductPriceResult:
            queryUpdateProductPriceResult.price = Decimal('150.00')
            session.commit()
            print("\n")
            print(f"✓ Updated {queryUpdateProductPriceResult.name} price to {queryUpdateProductPriceResult.price}")
        else:
            print("✗ Product 'Kindle' not found")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"✗ Error updating product price: {e}")

    # 5. Delete a user by ID.
    try:
        queryDeleteUser = session.get(User, 2)  # Assuming we want to delete user with ID 2
        if queryDeleteUser:
            session.delete(queryDeleteUser)
            session.commit()
            print("\n")
            print(f"✓ Deleted user: {queryDeleteUser.name}")
        else:
            print("✗ User with ID 2 not found")
    except IntegrityError as e:
        session.rollback()
        print(f"✗ Cannot delete user: has related orders (foreign key constraint) - {e.orig}")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"✗ Error deleting user: {e}")

    # Part 6: Bonus (Optional)
    # -- Add a status column to the Order table
    # (Boolean to represent shipped or not).
    # This was done in the Order table definition above.
        
    # -- Query all orders that are not shipped.
    try:
        queryUnshippedOrders = select(Order).where(Order.shipped == False)
        unshippedOrders = session.execute(queryUnshippedOrders).scalars().all()
        print("\nUnshipped Orders:")
        for order in unshippedOrders:
            print(f"Unshipped OrderID: {order.id}, UserID: {order.user_id}, ProductID: {order.product_id}, Quantity: {order.quantity}.")
    except SQLAlchemyError as e:
        print(f"✗ Error querying unshipped orders: {e}")
        
    # -- Count the total number of orders per user.
    try:
        queryAllUsersOrdersCount = (
            select(User.name, func.count(Order.id))
            .join(Order, User.id == Order.user_id)
            .group_by(User.id)
        )
        usersOrdersCount = session.execute(queryAllUsersOrdersCount).all()
        print("\nTotal Orders per User:")
        for user_name, order_count in usersOrdersCount:
            print(f"User: {user_name}, Total Orders: {order_count}.")
    except SQLAlchemyError as e:
        print(f"✗ Error counting orders: {e}")

# Session automatically closed by context manager

# Optional: Drop all tables from the database
# Uncomment the lines below to delete all tables when script runs
# WARNING: This will permanently delete all data!

print("\n⚠️  Dropping all tables...")
Base.metadata.drop_all(engine)
print("✓ All tables dropped successfully")