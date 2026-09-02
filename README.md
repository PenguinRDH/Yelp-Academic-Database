# Yelp Database Application

A desktop application built with Python and Qt Creator that interfaces with a Yelp-style relational database. Created as a final project for a database systems course.

## Overview

This application provides a graphical interface for querying and interacting with a database modeled on Yelp's business, review, and user data. It was built to demonstrate database design, SQL querying, and application-database integration skills.

## Tech Stack

- **Language:** Python
- **GUI Framework:** Qt Creator (PyQt6)
- **Database:** PostgreSQL

## Project Structure

All final source code is located in the `Final/` folder.

```
Final/
├── app.py
├── source.ui
└── InsertStatements.py (Python code to process the Yelp data into SQL statements)
```

## Getting Started

### Prerequisites

- Python 3.x
- PyQt6
- A running PostgreSQL server with a database matching the project's schema

### Installation

1. Clone or download this repository.
2. Navigate to the `Final/` folder.
3. Install required Python packages:
   ```
   pip install -r requirements.txt
   ```
4. Set up the database using the provided schema/scripts.
5. Update database connection settings (host, username, password) as needed.

### Running the Application

From within the `Final/` folder:

```
python app.py
```

## Features

- Browse and search Yelp-style business listings
- View and filter reviews
- Query the database through a Qt-based GUI
- (Add other features specific to your implementation)

## Author

Built as a final project for a database class.

## Notes

This project was developed for educational purposes as part of coursework.
