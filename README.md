# ALL-2-Sales-and-Inventory-management
A user-friendly sales and inventory management system for recording and controlling sales transactions, inventory quantity tracking and low stock notification, purchase orders tracking to suppliers, sales and inventory reports, users access for admin and staff members.

## Table of Contents
1. Introduction
2. Features
3. Installation
4. Usage
5. Contributing
6. License

## Introduction
POS and Managment System simplifies the process of Managment for POS. It is designed for POS and Inventory to provide seamless purchase experiences to their customers and efficient management for administrators.

## Features
- User authentication for customers and administrators.
- Search and filter cars by model, price and color.
- Real-time booking and availability updates.
- Easy management of customer profiles and rental history.
- Agency dashboard to add, update, or remove vehicles.

## Installation
Steps:

1.Clone the Repository: 'https://github.com/TheanRuXin/ALL-2-Sales-and-Inventory-management/'

3.Install Required Python Libraries: Install all dependencies listed in the `requirements.txt` file

4.Set Up the SQLite Database: The system uses SQLite as the database. Ensure the database file (e.g., `Trackwise.db`) exists in the project directory.

5.Run the Application: 
  1. Start the program : 'main.py'

### Notes
- Email Features: Ensure you configure the email settings in your script (`smtplib` section) for features like email notifications.
- PDF Reports: The system generates reports using `reportlab`. Reports will be saved in the project directory.

## Usage
### For Manager:
1. Login as Manager with username "trackwise" and Password "trackwise123".
2. Navigate to Register new user and register account for admin and cashier.
3. View Sales and Inventory report.

### For Admin:
1. Login
2. Login to the admin panel.
3. Register New Product. Add Image
4. Manage the product details and image if any.

### For Cashier:
1. Login 
2. Log In to the cashier panel.
2. Process the sale, choose product and add quantity.
3. Make Payement.
   
## Technologies Used
- Backend: Python
- Frontend: Tkinter
- Database: SQLite 

## Contributing
Guidelines for contributing to the project.
- Fork the repository
- Create a new branch
- Submit a pull request
