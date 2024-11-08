import streamlit as st
import pandas as pd
from datetime import datetime
import os
from pathlib import Path
import smtplib
from email.message import EmailMessage

# Define the folder where CSV files will be saved
OUTPUT_FOLDER = Path("output_files")
OUTPUT_FOLDER.mkdir(exist_ok=True)  # Create folder if it doesn't exist

st.title("Dynamic Order Entry System")

# Load data and initialize options
try:
    options_df = pd.read_csv('products - Sheet1.csv')
    business_partner_options = options_df['A'].dropna().unique().tolist()
    product_map = dict(zip(options_df['C'].dropna(), options_df['B'].dropna()))
    product_options = list(product_map.keys())
except FileNotFoundError:
    st.error("The options.csv file was not found. Make sure the file is in the correct location.")
    business_partner_options = []
    product_options = []
except UnicodeDecodeError:
    st.error("Error decoding the CSV file. Try saving with UTF-8 encoding.")
    business_partner_options = []
    product_options = []

# Initialize session state for the order DataFrame
if "df" not in st.session_state:
    columns = [
        "Document Type*", "Business Partner*", "Warehouse*", "Reference No / PO No",
        "Order Rec Date & Time*", "Expected Delivery Date & Time", "Billing Frequency",
        "Picking Method*", "Description", "Product*", "Sales Order Qty",
        "Free Order Qty", "Returnable", "Order Qty (Consignment/Exchange/Demo)",
        "Net Unit Price", "Lot No", "Freshness %", "From Date", "To Date",
        "Shipping address Pin code", "Invoicing address pincode", "Discount"
    ]
    st.session_state["df"] = pd.DataFrame(columns=columns)

# Dropdown for selecting Business Partner
business_partner = st.selectbox("Business Partner*", business_partner_options)

# Date input
order_date = st.date_input("Order Rec Date & Time*", datetime.today())

# Initialize session state for products if not already initialized
if "products" not in st.session_state:
    st.session_state["products"] = []

# Function to add product
def add_product():
    st.session_state.products.append({"Description": "", "Sales Order Qty": 1, "Product Code": ""})

# Button to add a new product entry
st.button("Add Product", on_click=add_product)

# Display product entries dynamically
for idx, product in enumerate(st.session_state.products):
    cols = st.columns([3, 1])
    product["Description"] = cols[0].selectbox(
        f"Product Description {idx+1}", product_options, key=f"product_desc_{idx}"
    )
    product["Product Code"] = product_map.get(product["Description"], "")
    product["Sales Order Qty"] = cols[1].number_input(
        f"QTY {idx+1}", min_value=1, step=1, key=f"qty_{idx}"
    )

# Collect data and append to DataFrame in session state
if st.button("Submit Order"):
    for product in st.session_state.products:
        new_entry = {
            "Order Rec Date & Time*": order_date,
            "Business Partner*": business_partner,
            "Description": product["Description"],
            "Sales Order Qty": product["Sales Order Qty"],
            "Product*": product["Product Code"],
            "Document Type*": "", "Warehouse*": "", "Reference No / PO No": "",
            "Expected Delivery Date & Time": "", "Billing Frequency": "", "Picking Method*": "",
            "Free Order Qty": "", "Returnable": "", "Order Qty (Consignment/Exchange/Demo)": "",
            "Net Unit Price": "", "Lot No": "", "Freshness %": "", "From Date": "", "To Date": "",
            "Shipping address Pin code": "", "Invoicing address pincode": "", "Discount": ""
        }
        st.session_state["df"] = pd.concat([st.session_state["df"], pd.DataFrame([new_entry])], ignore_index=True)
    st.success("Order submitted successfully!")

# Show the DataFrame
st.write("Current Order Data:", st.session_state["df"])

# Download the DataFrame as CSV
csv = st.session_state["df"].to_csv(index=False)
st.download_button(
    label="Download data as CSV",
    data=csv,
    file_name="order_data.csv",
    mime="text/csv"
)

# Function to send email with attachment
def send_email_with_attachment(receiver_email, file_path):
    sender_email = "amogh.kawle@multiline.tech"  # Replace with your email
    sender_password = "sled wvrx zsmq wlqj"        # Replace with your email password
    subject = "Order Data CSV File"
    body = "Please find the attached order data CSV file."

    # Set up the email
    msg = EmailMessage()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.set_content(body)

    # Attach the file
    with open(file_path, "rb") as f:
        file_data = f.read()
        file_name = os.path.basename(file_path)
        msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename=file_name)

    # Send the email
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)

# Save file and email on button click
if st.button("Save to Output Folder and Send Email"):
    output_path = OUTPUT_FOLDER / "order_data.csv"  # Define the path to save the CSV
    st.session_state["df"].to_csv(output_path, index=False)
    st.success(f"File saved to {output_path}")

    # Send email with attachment
    receiver_email = "amogh.kawle@multiline.tech"  # Replace with the recipient's email address
    try:
        send_email_with_attachment(receiver_email, output_path)
        st.success(f"Email sent to {receiver_email} with the CSV attachment.")
    except Exception as e:
        st.error(f"Failed to send email: {e}")
