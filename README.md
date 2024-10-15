# NestEgg: Your Personal Investment Portfolio Tracker

<p align="left">
    <a href="https://github.com/abeltavares/StockTracker](https://github.com/lucaplayground/nestegg">
        <img src="https://img.shields.io/badge/GitHub-Repository-blue?logo=github" alt="GitHub Repository">
    </a>
    <a href="https://www.djangoproject.com/">
        <img src="https://img.shields.io/badge/Django-5.0-blue?logo=django" alt="Django">
    </a>
    <a href="https://www.python.org/">
        <img src="https://img.shields.io/badge/Python-3.10-blue?logo=python" alt="Python">
    <a href="https://opensource.org/licenses/MIT">
        <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License">
    </a>        
    </a>
</p>

NestEgg is a web application designed to help individual investors manage and track their investment portfolios with ease. It offers a comprehensive suite of tools for monitoring diverse assets across multiple portfolios, providing real-time insights into your investment strategy and performance. 

NestEgg is ideal for long-term individual investors who aren’t concerned with short-term stock price changes (as we don’t track individual profits 😄) but focus on their overall financial growth.

## Table of Contents
1. [Key Features](#key-features)
2. [UI Showcase](#ui-showcase)
3. [Project Structure](#project-structure)
4. [Security Measures](#security-measures)
5. [Setup and Installation](#setup-and-installation)
6. [Usage Guide](#usage-guide)
7. [Production Environment](#production-environment)
8. [Testing with Admin Commands](#testing-with-admin-commands)
9. [Current Limitations and Future Considerations](#current-limitations-and-future-considerations)
10. [Contributing](#contributing)
11. [License](#license)

## Key Features
1. **Multi-Portfolio Management**: Create and manage multiple investment portfolios, allowing you to organise your investments by strategy, goal, or other criteria.
2. **Diverse Asset Tracking**: Track a wide range of assets including stocks, bonds, ETFs, and more from various global markets.
3. **Real-Time Data**: Utilises up-to-date market data to provide accurate valuations of your assets and overall portfolio.
4. **Currency Conversion**: Automatically handles multiple currencies, converting all asset values to your preferred currency for consistent reporting.
5. **Interactive Dashboard**:
- View your total investment value across all portfolios
- Track your investment value history over time
- Analyse your investment distribution by geographic region
- Understand your investment strategy through Passive vs Aggressive asset allocation
6. **Detailed Portfolio Views**: Dive deep into each portfolio, seeing individual asset performances, ratios, and values.
7. **Asset Management**: Easily add, update, or remove assets from your portfolios as your investment strategy evolves.
User-Friendly Interface: Intuitive design makes it easy to navigate and understand your investments at a glance.
9. **Secure and Private**: Built with security in mind, ensuring your sensitive financial data remains protected.

## UI Showcase

### Dashboard

### Portfolio View

### Asset Management

## Project Structure

NestEgg follows a typical Django project structure with some custom applications:

nestegg/
│
├── backend/ # Main Django project directory
│ ├── settings.py # Project settings
│ ├── urls.py # Main URL configuration
│ └── wsgi.py # WSGI application entry point
│
├── accounts/ # Custom user authentication app
│ ├── models.py # Custom user model
│ └── views.py # User-related views
│
├── investments/ # Core investment tracking app
│ ├── models.py # Portfolio and Asset models
│ ├── views.py # Investment-related views
│ └── utils.py # Utility functions for investments
│
├── static/ # Static files (CSS, JS, images)
│
├── templates/ # HTML templates
│
├── manage.py # Django's command-line utility
│
└── requirements.txt # Project dependencies

- The `backend` directory contains the main Django project settings and configurations.
- `accounts` handles user authentication and profiles.
- `investments` is the core app for managing portfolios and assets.
- Static files and templates are organised in their respective directories at the project root level for easy management.

This structure allows for modular development and clear separation of concerns between different parts of the application.

## Security Measures

NestEgg implements several security measures to protect user data and the application:

1. **Password Hashing**: User passwords are securely hashed using Django's built-in password hashing system.

2. **Environment Variables**: Sensitive information such as secret keys and database credentials are stored as environment variables, not in the codebase.

3. **Password Validation**: Django's password validation system is used to enforce strong password policies.

4. **CSRF Protection**: Cross-Site Request Forgery (CSRF) protection is enabled by default in Django and used throughout the application.

5. **SQL Injection Prevention**: Django's ORM is used for database queries, which helps prevent SQL injection attacks.

6. **XSS Protection**: Django's template system automatically escapes user input to prevent Cross-Site Scripting (XSS) attacks.

7. **User Authentication**: A custom user model is used with Django's authentication system to manage user accounts securely.

8. **Session Security**: Django's session framework is used to manage user sessions securely.

## Setup and Installation
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/nestegg.git
   ```
2. Navigate to the project directory:
   ```
   cd nestegg
   ```
3. Create a virtual environment:
   ```
   python -m venv venv
   ```
4. Activate the virtual environment:
   - On Windows: `venv\Scripts\activate`
     
   - On macOS and Linux: `source venv/bin/activate`
5. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
6.Set up the environment variables in the `.env` file:
- `DJANGO_SECRET_KEY`: Your Django secret key.

- `DJANGO_DEBUG`: Set to `False` to turn off debug mode in production..

- `DB_USER`: The username of your PostgreSQL user.

- `DB_PASSWORD`: The password of your PostgreSQL user.

- `DB_PORT`: The port where the PostgreSQL server is listening.

- `DB_HOST`: The host where the PostgreSQL server is running on.

- `DB_NAME`: The name of the database.

- `DJANGO_ALLOWED_HOSTS`: Your allowed hosts, e.g.,'your-domain.com' and 'www.your-domain.com.

- `EXCHANGE_API_KEY`: The API key for the ExchangeRate.
7. Set up the database:
   ```
   python manage.py makemigration
   python manage.py migrate
   ```
8. Create a superuser:
   ```
   python manage.py createsuperuser
   ```
9. Run the development server:
   ```
   python manage.py runserver
   ```

## Production Environment
When deploying NestEgg to a production environment, please consider the following:

1. **Secret Key**: Generate a new secret key and store it as an environment variable.

2. **Debug Mode**: Ensure `DEBUG` is set to `False` in your settings.

3. **Database**: Use a production-grade database like PostgreSQL.

4. **Static Files**: Use a CDN or configure your web server to serve static files.

5. **HTTPS**: Ensure all traffic is served over HTTPS.

6. **Environment Variables**: Store sensitive information (API keys, database credentials) as environment variables.

7. **Logging**: Configure appropriate logging for the production environment.

8. **HTTPS and HSTS**: While the application is designed to work with HTTPS, it doesn't enforce it. Implementing HTTPS and HTTP Strict Transport Security (HSTS) is crucial for a production environment.

7. **Secure Cookies**: The application doesn't currently enforce secure cookies. This should be implemented for production use.

For a detailed guide on deploying Django applications, refer to the [Django deployment checklist](https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/).


## Testing with Admin Commands

NestEgg includes custom Django admin commands to facilitate testing and data population. To use these:

1. Ensure you're in your project's root directory.
2. Run the following command to populate your database with test data:

   ```
   python manage.py populate_fake_data
   ```

This command creates a test user, portfolios, and assets, allowing you to quickly set up a testing environment.


## Current Limitations and Future Considerations

While NestEgg provides robust functionality for tracking investments, there are some current limitations and areas for future improvement:

1. **Mobile Responsiveness**: Some pages with tables, such as the 'Add Assets' page, don't render optimally on small screens. Future updates will focus on improving the mobile experience.

2. **Currency Changes**: If a user changes their default currency, this change is not retroactively applied to the TotalValueHistory. In future versions, we plan to implement a currency conversion feature for historical data.

3. **Asset Coverage**: Currently, NestEgg only supports assets available on Yahoo Finance. We're exploring options to expand our asset coverage in future releases.

4. **Real-time Updates**: Asset prices are updated periodically rather than in real-time. Future versions may include more frequent or real-time price updates.

5. **Rate Limiting**: The application currently lacks rate limiting, which could make it vulnerable to abuse. Implementing rate limiting is a priority for future security enhancements.


## Contributing
Contributions are welcome! Please fork the repository and create a pull request with your changes.

## License
This project is licensed under the [MIT License](LICENSE.txt).
