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
The Car Rental Booking System simplifies the process of booking vehicles for rent. It is designed for car rental businesses to provide seamless booking experiences to their customers and efficient management for administrators.

## Features
- User authentication for customers and administrators.
- Search and filter cars by model, price and color.
- Real-time booking and availability updates.
- Easy management of customer profiles and rental history.
- Agency dashboard to add, update, or remove vehicles.

## Installation
Steps:

1.Clone the Repository: 'https://github.com/TheanRuXin/Car-Booking/tree/master'

2.Navigate to the project directory: 'Car-Booking'

3.Install Required Python Libraries: Install all dependencies listed in the `requirements.txt` file

4.Set Up the SQLite Database: The system uses SQLite as the database. Ensure the database file (e.g., `Car_Rental.db`) exists in the project directory.

5.Run the Application: 
  1. Start the program for customer: 'first_page.py'
  2. Start the program for agency: 'agency_first_page.py'

6.Use the GUI window to interact with the car rental booking system.

### Notes
- Email Features: Ensure you configure the email settings in your script (`smtplib` section) for features like email notifications.
- PDF Reports: The system generates reports using `reportlab`. Reports will be saved in the project directory.

## Usage
### For Customers:
1. Sign Up and Log In.
2. Search the available cars and select your desired vehicle.
3. Book a car by specifying the rental dates.
4. View your booking and history in the profile section.

### For Agency:
1. Sign Up and Log In 
2. Log In to the admin panel.
2. Add or update car details, including model, price, and availability.
3. Manage car details, customer bookings, ratings and reviews, promotions and history.

## Technologies Used
- Backend: Python
- Frontend: Tkinter
- Database: SQLite 

## Contributing
Guidelines for contributing to the project.
- Fork the repository
- Create a new branch
- Submit a pull request
