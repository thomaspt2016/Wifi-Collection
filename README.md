Wi-Fi Payment Management Portal
Project Overview
The Wi-Fi Payment Management Portal is a robust and scalable web application designed to streamline the management of Wi-Fi services and payments for multi-tenant environments. Originally developed as a proof-of-concept using a Python-based Streamlit application with Google Sheets, this project has been re-architected into a secure, full-featured web application using the Django framework.

This portal efficiently manages Wi-Fi payments for over 600 users across three buildings, providing a sophisticated, role-based access control (RBAC) system for clients, co-agents, and owners. It automates key administrative tasks such as bill generation and plan-based code distribution, and includes a secure payment facility. The system also offers integrated data visualization for in-depth payment analysis and a ticket-raising facility to enhance user support.

Key Features
Role-Based Access Control (RBAC): Secure access for different user types—Clients, Co-Agents, and Owners—ensuring data privacy and appropriate administrative privileges.

Automated Bill Generation: Automatically generates and distributes bills to users based on their selected Wi-Fi plans.

Secure Payment Facility: A streamlined and secure process for users to pay for their Wi-Fi services.

Payment Data Analysis: Integrated charts and dashboards provide owners with insights into payment trends, collection rates, and user statistics.

Plan-based Code Distribution: Automates the distribution of Wi-Fi access codes to users upon payment, linked directly to their chosen plan.

Ticket Raising System: A built-in support system that allows users to raise tickets for issues, improving communication and problem resolution.

Scalable Architecture: Migration from a basic Streamlit app to a Django-based solution ensures the application is highly scalable, maintainable, and secure.

Technologies Used
The project is built using a modern and efficient tech stack:

Frontend: HTML, CSS, JavaScript

Styling & Components: Tailwind CSS, Flowbite

Backend: Python, Django

Database: SQLite

Getting Started
Follow these instructions to set up the project on your local machine.

Prerequisites
Python 3.8+

pip (Python package installer)

Installation
Clone the repository:

Bash

git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
Create and activate a virtual environment:
It's recommended to use a virtual environment to manage dependencies.

Bash

python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
Install the required packages:

Bash

pip install -r requirements.txt
Run database migrations:

Bash

python manage.py migrate
Create a superuser (for admin access):

Bash

python manage.py createsuperuser
Follow the prompts to create an admin account.

Run the development server:

Bash

python manage.py runserver
The application will now be running at http://127.0.0.1:8000/. You can access the Django admin panel at http://127.0.0.1:8000/admin using the superuser credentials you created.

Usage
Owner/Admin: Log in to the admin panel to manage users, plans, and view analytics.

Co-Agent: Access the portal to manage users and payments for their assigned building(s).

Client: Log in to view their bill, make payments, and raise support tickets.

Contributing
We welcome contributions! If you would like to contribute, please fork the repository and create a new branch for your feature. Ensure your code follows the project's coding standards and includes appropriate tests. Submit a pull request with a detailed description of your changes.

License
This project is licensed under the MIT License. See the LICENSE file for details.
