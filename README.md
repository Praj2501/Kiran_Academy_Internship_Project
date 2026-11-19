# Recruitment & Placement Management System (RPMS)

A Python + MySQL, menu-driven recruitment workflow application, accompanied by the requested technology-neutral 12-page HTML/CSS UI prototype.

## Features implemented
- Candidate registration, search/list and soft deactivation with validation and unique email/mobile constraints.
- Company and job management.
- Eligibility engine: active candidate, open job, deadline, percentage, passing year and backlog criteria.
- Duplicate candidate/job application prevention and application status history.
- Controlled application workflow and invalid-transition protection.
- Interview scheduling and feedback with 0–5 rating validation.
- Offer creation for selected candidates and transactional joining/placement confirmation.
- SQL reporting: technology-wise candidates, open jobs, application status, recruitment funnel, company placements, pending interviews and job aging.
- Parameterized SQL, OOP service layer, DAO/database layer, custom exceptions, activity log file.
- All 17 database tables from the supplied design and 12 static HTML prototype pages.

## Requirements
- Python 3.10+
- MySQL 8.0+

## Setup
1. Install MySQL and create a database user with permission to create/use `rpms_db`.
2. Open a terminal in this project folder and install dependencies:
   `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and enter your local MySQL username/password.
4. Run `sql/database_schema.sql` in MySQL Workbench (or `mysql -u root -p < sql/database_schema.sql`).
5. Optional demo data: run `sql/sample_data.sql` after the schema.
6. Start the application: `python main.py`.
7. Open `recruitment-placement-ui/login.html` in a browser for the separate static prototype.

## Console menu
Candidates → Companies → Jobs → Applications → Interviews → Offers → Placements → Reports.
Use database IDs shown in the listing screens when creating related records. The console app connects to MySQL; the HTML prototype is intentionally static and is not connected to the backend, as specified in the supplied UI document.

## Project structure
- `rpms/dao`: MySQL connectivity / data access
- `rpms/service`: validations and recruitment business logic
- `rpms/model`: model package reserved for typed domain models
- `rpms/util`: configuration and file logger
- `rpms/exception`: domain exceptions
- `sql`: schema, sample data and report queries
- `recruitment-placement-ui`: 12-page responsive prototype
- `tests`: basic verification notes

## Important notes
- Never commit `.env`; it contains local credentials. `.env.example` is safe to share.
- Password hashing fields and role/user tables are included in the schema. This student console version does not yet expose user registration/login or role-based authorization; the prototype login screen is illustrative only.
- Skill mapping tables are included in the normalized schema; eligibility currently enforces the explicit academic/job criteria and not mandatory skill matching. This can be extended in the next iteration.
- Seed job deadlines are example dates and should be adjusted when reusing the demo dataset.
