import sqlite3
import os

def convert_to_binary_data(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        blob_data = file.read()
    return blob_data

def insert_image(name, filename, cursor):


    try:
        # Convert the image to binary data
        binary_data = convert_to_binary_data(filename)
        
        # Insert the image data into the database
        cursor.execute('''
            INSERT INTO assets (assetName, asset)
            VALUES(?, ?)
        ''', (name, binary_data))
        
        # Commit the transaction
        
        print(f"Image '{name}' inserted successfully as a BLOB in the database.")
        
    except sqlite3.Error as error:
        print(f"Failed to insert image into sqlite table: {error}")

def insert_all_images():
    # Connect to the SQLite database
    conn = sqlite3.connect('cards.db')

    # Create a cursor object
    cursor = conn.cursor()
    # Get the path to the assets folder
    assets_folder = 'assets'

    # Iterate over all files in the assets folder
    for filename in os.listdir(assets_folder):
        # Construct the full path to the file
        print(filename)
        file_path = os.path.join(assets_folder, filename)

        name = os.path.splitext(filename)[0].lower()

        # Insert the image into the database
        insert_image(name, file_path, cursor)

    # Close the cursor and the connection
    cursor.close()
    conn.commit()
    conn.close()
    

# Example usage
insert_all_images()
