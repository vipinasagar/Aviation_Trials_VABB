# -*- coding: utf-8 -*-
"""
Created on Sat Jun 22 14:27:06 2024

@author: 30092527
"""
from flask import Flask, jsonify
import pandas as pd
#import schedule
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)

# Replace these with the actual URL and your login credentials
login_url = "http://www.acdm.in/cdm/"
data_url = "http://www.acdm.in/cdm/acdm_mumbai.php#"
credentials = {
    "username": "vipinasagar",
    "password": "Airside@2024@"
}

def fetch_data():
    try:
        # Initialize the Selenium webdriver
        driver = webdriver.Chrome()  # Replace with the appropriate webdriver for your browser
        driver.get(login_url)
        
        driver.refresh()

        # Find the username and password fields, and enter the credentials
        username_field = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "username")))
        time.sleep(3)
        password_field = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "password")))
        time.sleep(3)
        username_field.send_keys(credentials["username"])
        password_field.send_keys(credentials["password"])

        # Submit the login form
        login_button = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "submit")))
        login_button.click()
        time.sleep(3)

        # Find the link that leads to the table
        link = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "tile2")))
        link.click()
        # table_url = link.get_attribute('href')

        # Navigate to the table URL
        # driver.get(table_url)

        # Find the table and extract the data
        
        time.sleep(5)
        
        table = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, 'table'))
        )
        rows = table.find_elements(By.TAG_NAME, 'tr')
        
        # Extract the header row
        header_row = rows[0]
        header_columns = header_row.find_elements(By.TAG_NAME, 'th')
        header = [col.text.strip() for col in header_columns]
        
        data = []
        for row in rows:
            columns = row.find_elements(By.TAG_NAME, 'td')
            data.append([col.text.strip() for col in columns])

        # Create a DataFrame and remove duplicates
        df = pd.DataFrame(data,columns = header)
        df = df.drop_duplicates()
        
        df = df[(df['Callsign'] != 'None') & (~df['Callsign'].isnull())]

        # Close the webdriver
        driver.quit()

        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

@app.route('/get_data', methods=['GET'])
def get_data():
    try:
        new_data = fetch_data()
        if new_data is not None:
            # Convert DataFrame to JSON format for API response
            data_json = new_data.to_json(orient='records')
            return jsonify({'data': data_json})
        else:
            return jsonify({'error': 'Failed to fetch data'})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(port=5000)  # Run the Flask app on port 5000
    
# =============================================================================
# output_file = "extracted_data.xlsx"
# 
# def append_data_to_excel(df):
#     try:
#         # Load existing data
#         existing_df = pd.read_excel(output_file)
#     except FileNotFoundError:
#         # If file doesn't exist, create from new DataFrame directly
#         df.to_excel(output_file, index=False)
#         return
# 
#     # Concatenate and remove duplicates
#     combined_df = pd.concat([existing_df, df]).drop_duplicates()
#     
#     # Write back to Excel
#     combined_df.to_excel(output_file, index=False)
# 
# def job():
#     new_data = fetch_data()
#     if new_data is not None:
#         append_data_to_excel(new_data)
# 
# # Schedule the job every minute
# schedule.every(1).minutes.do(job)
# 
# # Run indefinitely
# while True:
#     schedule.run_pending()
#     time.sleep(1)
# 
# =============================================================================
