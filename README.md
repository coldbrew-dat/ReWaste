# ReWaste ♻️

A B2B digital waste exchange platform connecting businesses that generate waste with businesses that can reuse it.

## About the Project

Across Pakistan's manufacturing and industrial sector, businesses regularly generate waste and byproducts such as fabric offcuts, metal shavings, plastic regrind, cardboard, fly ash, and e-waste. Much of this material ends up in landfill simply because there is no easy way for a business to find someone who could actually use it. At the same time, other businesses spend money buying raw materials that could, in many cases, be a byproduct that someone nearby is already discarding.

ReWaste was built to close that gap. It is a circular economy marketplace where registered businesses can list surplus or waste materials for other companies to discover, request, and purchase. This turns what used to be a disposal cost into a potential revenue stream, while reducing the amount of reusable material that ends up in landfill. Beyond listings, the platform also tracks each business's participation over time through a sustainability scoring system, so that consistent engagement with the exchange is recognized rather than a single, one off post.

The project was built end to end as a team project for an internship at the Institute of Transformative Leadership. This covered the database schema and authentication system, the listings and request marketplace, an admin system for platform oversight, and an analytics dashboard with automatically generated monthly reports.

The live demo can be viewed at [coldbrew.pythonanywhere.com](https://coldbrew.pythonanywhere.com/listings).

## Features

The platform allows businesses to sign up using their company name, sector, and city, then log in to manage their own profile and listings. Once logged in, a business can post a waste or surplus material for exchange, specifying its quantity, unit of measurement, price, an optional photo, and a description. Every business can browse the full marketplace of available listings, filtering by material type such as plastic, metal, paper, fabric, glass, wood, or electronics, and by city.

When a business finds a listing it is interested in, it can send an exchange request along with a message explaining what it needs. The seller can then view all incoming requests on their own dashboard and accept or manage them, so that the entire negotiation stays on the platform rather than moving elsewhere.

An admin panel is available to accounts with admin access only, giving full oversight and control over the platform. From this panel, an admin can view every registered business and every listing on the platform. An admin can edit any business's profile information, reset a business's password, and grant or revoke admin access for any account. An admin can also edit or remove any listing on the platform, regardless of which business originally posted it. Deleting a business through the admin panel also removes all of that business's listings, exchange requests, and sustainability score, keeping the database consistent. This gives the platform proper moderation capability rather than relying on individual businesses to manage their own content responsibly.

Every business also has access to a sustainability dashboard. This dashboard calculates a score based on the number of listings posted, the number of completed exchanges, and the total kilograms of waste diverted from landfill. As this score grows, the business moves up through Bronze, Silver, Gold, and Platinum badge tiers, giving a visible incentive to keep participating in the exchange rather than posting once and leaving.

Finally, the dashboard can generate monthly reports built with Pandas and Matplotlib, summarizing a business's exchange activity over time in chart form.

## Tech Stack

The backend is built with Flask and Flask SQLAlchemy. The database is SQLite for local development and PostgreSQL in production, controlled through the DATABASE_URL environment variable. The frontend uses Jinja2 templates with vanilla CSS and JavaScript. Reports are generated using Pandas and Matplotlib. The live version of the app is deployed on PythonAnywhere.

## Project Structure

```
ReWaste/
├── app.py                  App factory, configuration, and blueprint registration
├── models/
│   ├── db.py                SQLAlchemy instance
│   └── models.py             User, Listing, Request, and Score models
├── routes/
│   ├── auth_routes.py        Signup, login, and logout
│   ├── listing_routes.py     Creating, browsing, editing, and deleting listings
│   ├── request_routes.py     The exchange request system
│   ├── admin_routes.py       The admin panel, including full business and listing management
│   └── dashboard_routes.py   The sustainability score and monthly reports
├── reports/
│   └── report_generator.py   Monthly chart and report generation
├── static/                  CSS, JavaScript, and uploaded images
├── templates/                Jinja2 HTML templates
├── schema.sql                Initial database schema reference
├── seed_data.py               Populates sample businesses and listings for demo purposes
└── requirements.txt
```

## Getting Started Locally

To run the project locally, first clone the repository.

```bash
git clone https://github.com/Maheen-fatima123/ReWaste.git
cd ReWaste
```

Then set up a virtual environment.

```bash
python -m venv venv
venv\Scripts\activate      (on Windows)
source venv/bin/activate   (on macOS or Linux)
```

Install the required dependencies.

```bash
pip install -r requirements.txt
```

If you would like to use PostgreSQL instead of the default SQLite database, copy .env.example to .env and set your own SECRET_KEY and DATABASE_URL. This step is optional for local development.

Run the app with the following command.

```bash
python app.py
```

The app will be available at http://127.0.0.1:5000, and the database tables will be created automatically the first time it runs.

If you would like the marketplace to have some data to look at instead of being empty, you can run the seed script.

```bash
python seed_data.py
```

This populates the database with sample businesses, listings, and exchange requests. All company names used in the seed script are fictional and created purely for demonstration purposes.

## Admin Access

An account with admin access can visit the admin panel to oversee the platform. From there, an admin can view all registered businesses, edit any business's details or reset their password, grant or revoke admin rights, and delete a business entirely along with all of their data. An admin can also edit or remove any listing on the platform. This oversight exists to keep the marketplace accurate and to allow moderation of inappropriate or fraudulent content.

## Team

This project was built by three team members as part of an internship at the Institute of Transformative Leadership. Haadiya built the authentication module, the exchange and request system, and the admin panel with full business and listing management capability. Hassan built the sustainability dashboard, the scoring system, and the monthly reports. Maheen built the listings module and managed the Git repository.

## License

This project was built for academic and internship purposes as part of a requirement at the Institute of Transformative Leadership.
