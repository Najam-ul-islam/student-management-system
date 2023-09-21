import streamlit as st
import sqlite3
import os
import logging

# Define admin credentials (you should replace these with your actual admin credentials)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(message)s')

class CRUDApp:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.db_file = None
        self.table_name = 'items'
        self.columns = ['id INTEGER PRIMARY KEY', 'name TEXT', 'description TEXT']
        self.admin_logged_in = False

    def log_activity(self, activity):
        logging.info(f"Admin: {self.admin_logged_in}, Activity: {activity}")

    def run(self):
        if self.admin_logged_in:
            if self.db_file:
                self.create_crud_tabs()
            else:
                self.create_db_gui()
        else:
            self.admin_login()

    def admin_login(self):
        if not self.admin_logged_in:
            st.title('Admin Login')
            username = st.text_input('Username')
            password = st.text_input('Password', type='password')

            if st.button('Login'):
                if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                    self.admin_logged_in = True
                    self.log_activity("Admin Login")
                    st.success('Admin logged in successfully.')
                else:
                    st.warning('Invalid credentials. Please try again.')

        return self.admin_logged_in

    def create_db_gui(self):
        st.title('Create Database')
        db_name = st.text_input('Enter a database file name (e.g., my_database.db):')

        if db_name:
            self.db_file = db_name

            if st.button('Create Database'):
                self.conn = sqlite3.connect(self.db_file)
                self.cursor = self.conn.cursor()
                self.create_table(self.table_name, self.columns)
                self.log_activity(f"Database Created: {self.db_file}")
                st.success(f"Database '{self.db_file}' created successfully.")




    def create_table(self, table_name, columns):
        try:
            # Create the table with the specified columns
            column_defs = ', '.join(columns)
            create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_defs})"
            self.cursor.execute(create_table_sql)

            self.conn.commit()
        except sqlite3.Error as e:
            st.error(f"Error creating table '{table_name}': {e}")

    # def run(self):
    #     if self.db_file:
    #         if self.admin_login():
    #             self.create_crud_tabs()
    #     else:
    #         st.warning('Please create a database first.')

    # def admin_login(self):
    #     if not self.admin_logged_in:
    #         st.sidebar.title('Admin Login')
    #         username = st.sidebar.text_input('Username')
    #         password = st.sidebar.text_input('Password', type='password')

    #         if st.sidebar.button('Login'):
    #             if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
    #                 self.admin_logged_in = True
    #                 return True
    #             else:
    #                 st.sidebar.warning('Invalid credentials. Please try again.')
    #                 return False
    #     else:
    #         return True

    def create_crud_tabs(self):
        # CRUD operations tabs
        tabs = st.sidebar.radio("Navigation", ("Add Item", "View Items", "Update/Delete Item"))

        if tabs == "Add Item":
            self.add_item_tab()
        elif tabs == "View Items":
            self.view_items_tab()
        elif tabs == "Update/Delete Item":
            self.update_delete_item_tab()

    def add_item_tab(self):
        st.title('Add New Item')
        new_name = st.text_input('Name')
        new_description = st.text_area('Description')
        if st.button('Add'):
            self.create_item(new_name, new_description)

    def view_items_tab(self):
        st.title('View Existing Items')

        # Function to display existing items in a table format
        items = self.read_items()
        if items:
            st.header('Existing Items')
            item_data = [(item[0], item[1], item[2]) for item in items]
            st.table(item_data)
        else:
            st.warning('No items found or there was an issue reading the items.')

    def update_delete_item_tab(self):
        st.title('Update or Delete Item')
        selected_id = st.number_input('Enter the ID of the item to update or delete', min_value=1)
        selected_item = None

        items = self.read_items()

        for item in items:
            if item[0] == selected_id:
                selected_item = item
                break

        if selected_item:
            st.write(f'Selected Item: ID: {selected_item[0]}, Name: {selected_item[1]}, Description: {selected_item[2]}')
            update_name = st.text_input('Update Name', selected_item[1])
            update_description = st.text_area('Update Description', selected_item[2])

            if st.button('Update'):
                self.update_item(selected_id, update_name, update_description)

            if st.button('Delete'):
                self.delete_item(selected_id)
                st.success('Item Deleted!')

    def create_item(self, name, description):
        self.cursor.execute('INSERT INTO items (name, description) VALUES (?, ?)', (name, description))
        self.conn.commit()

    def read_items(self):
        try:
            self.cursor.execute('SELECT * FROM items')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            st.error(f"SQLite error: {e}")
            return []

    def update_item(self, id, name, description):
        self.cursor.execute('UPDATE items SET name=?, description=? WHERE id=?', (name, description, id))
        self.conn.commit()

    def delete_item(self, id):
        self.cursor.execute('DELETE FROM items WHERE id=?', (id,))
        self.conn.commit()

    def close_db(self):
        if self.conn:
            self.conn.close()

if __name__ == "__main__":
    app = CRUDApp()
    app.run()
    if app.conn:
        app.close_db()
