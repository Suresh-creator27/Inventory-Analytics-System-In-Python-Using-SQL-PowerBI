import streamlit as st
import mysql.connector
import hashlib
from mysql.connector import Error

# Establish MySQL Connection
def create_connection():
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",
            user="root",      # Replace with your MySQL username
            password="23112165",      # Replace with your MySQL password
            database="inventory"
        )
        return conn
    except Error as e:
        st.error(f"Error connecting to MySQL: {e}")
        return None

# Initialize Database and Tables
def init_db():
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",  # Ensure this is 'localhost' or '127.0.0.1'
            user="root",
            password="23112165",  # Replace with actual password
            database="inventory"  # Ensure this database exists
        )
        if conn.is_connected():
            print("Connected to database")
            return conn
        else:
            print("Failed to connect to database")
            return None

    except Error as e:
        print(f"Error initializing database: {e}")
        return None

init_db()

# Create User
def create_user(username, password):
    if not username or not password:
        st.warning("Username and Password cannot be empty!")
        return False
    
    conn = create_connection()
    if conn:
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        try:
            with conn.cursor() as cursor:
                cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', 
                               (username, hashed_pw))
                conn.commit()
                return True
        except Error as e:
            st.error(f"Database error: {e}")
            return False
        finally:
            conn.close()

# Verify User Login
def verify_user(username, password):
    conn = create_connection()
    if conn:
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        try:
            with conn.cursor() as cursor:
                cursor.execute('SELECT password FROM users WHERE username = %s', (username,))
                result = cursor.fetchone()
                return result and result[0] == hashed_pw
        except Error as e:
            st.error(f"Database error: {e}")
        finally:
            conn.close()
    return False

# Add Product
def add_product(name, quantity, price, supplier):
    conn = create_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute('INSERT INTO products (name, quantity, price, supplier) VALUES (%s, %s, %s, %s)',
                               (name, quantity, price, supplier))
                conn.commit()
        except Error as e:
            st.error(f"Database error: {e}")
        finally:
            conn.close()

# Get All Products
def get_products():
    conn = create_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM products')
                return cursor.fetchall()
        except Error as e:
            st.error(f"Database error: {e}")
        finally:
            conn.close()
    return []

# Update Product
def update_product(product_id, name, quantity, price, supplier):
    conn = create_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute('''
                    UPDATE products 
                    SET name = %s, quantity = %s, price = %s, supplier = %s
                    WHERE id = %s
                ''', (name, quantity, price, supplier, product_id))
                conn.commit()
        except Error as e:
            st.error(f"Database error: {e}")
        finally:
            conn.close()

# Delete Product
def delete_product(product_id):
    conn = create_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute('DELETE FROM products WHERE id = %s', (product_id,))
                conn.commit()
        except Error as e:
            st.error(f"Database error: {e}")
        finally:
            conn.close()

# Main Streamlit Application
def main():
    st.title("📦 Inventory Management System")

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ''

    if not st.session_state.logged_in:
        menu = st.selectbox("Menu", ["Login", "Register"])
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')

        if menu == "Login" and st.button("Login"):
            if verify_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Logged in successfully!")
            else:
                st.error("Invalid credentials")

        elif menu == "Register" and st.button("Register"):
            if create_user(username, password):
                st.success("Account created! Please login")
            else:
                st.error("Username already exists")
        return

    st.subheader(f"Welcome {st.session_state.username}")

    menu = st.sidebar.selectbox("Menu", ["Add Product", "View Products", "Update Product", "Delete Product"])

    if menu == "Add Product":
        with st.form("add_form"):
            name = st.text_input("Product Name")
            quantity = st.number_input("Quantity", min_value=0)
            price = st.number_input("Price", min_value=0.0)
            supplier = st.text_input("Supplier")
            if st.form_submit_button("Add Product"):
                add_product(name, quantity, price, supplier)
                st.success("Product added successfully!")

    elif menu == "View Products":
        products = get_products()
        if products:
            for product in products:
                st.write(f"*ID:* {product[0]} | *Name:* {product[1]} | *Quantity:* {product[2]} | *Price:* ${product[3]} | *Supplier:* {product[4]}")
        else:
            st.info("No products available")

    elif menu == "Update Product":
        products = get_products()
        product_ids = [p[0] for p in products]
        selected_id = st.selectbox("Select Product ID", product_ids)
        product = next(p for p in products if p[0] == selected_id)

        with st.form("update_form"):
            name = st.text_input("Name", value=product[1])
            quantity = st.number_input("Quantity", value=product[2])
            price = st.number_input("Price", value=product[3])
            supplier = st.text_input("Supplier", value=product[4])
            if st.form_submit_button("Update Product"):
                update_product(selected_id, name, quantity, price, supplier)
                st.success("Product updated successfully!")

    elif menu == "Delete Product":
        products = get_products()
        product_ids = [p[0] for p in products]
        selected_id = st.selectbox("Select Product ID to Delete", product_ids)
        if st.button("Delete"):
            delete_product(selected_id)
            st.success("Product deleted successfully!")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ''
        st.experimental_rerun()

if __name__ == "__main__":
    main()