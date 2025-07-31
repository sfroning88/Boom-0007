# Boom-0007
Project Abstract
Goal: 
Build a backend service + dashboard tool that simplifies and automates the messy client transition from QuickBooks Desktop to QuickBooks Online. It will:
Connect to the client’s QBO account.
Fetch and store financial data.
Display data in the admin dashboard.
Allow staff to trigger and verify syncs.
Prepare the data for downstream reporting and AI agents.

Why It Matters: 
Today, clients store their messy QB Desktop exports in Google Drive and our team manually decodes them. This is slow, error-prone, and doesn’t scale. Migrating to QBO gives us API access to structured financial data. Automating this unlocks faster onboarding, cleaner data, and intelligent tools powered by real financials.

QuickBooks Migration Assistant
Core Use Case:
For each client, pull structured financial data from their QBO account and organize it in Supabase for internal tools, financial reports, and agent automation.

Capabilities (MVP):
Authenticate with a client’s QBO account (OAuth2.0).
Pull core datasets: Chart of Accounts, P&L, Transactions, Invoices.
Store data into Supabase tables with appropriate client relations.
Manual refresh option.
Display synced data on a dashboard tab.
Simple logs for debugging.

Requirements (MVP):
Upload Clean Customer List
https://www.loom.com/share/30e03d325b074acd8af45f8b8e6b9daa
Scrub QBD export and clean up list with consistent naming conventions, customer hierarchy, and complete information
We can probably extract this information using OCR on signed contract documents (PDFs). Can also ask the owner what their customer onboarding process looks like so we can automate the data entry process.
Upload Clean Vendor List
https://www.loom.com/share/2ab7a828b1804c0494e894adab3dcf5e
Scrub QBD export and clean up list with consistent naming conventions and complete information
We can probably extract this information using OCR on incoming invoices. Should ask the owner what their vendor onboarding process looks like so we can automate the data entry process.
Potentially do automated vendor outreach to request W-9 forms for compliance clean up. 
In the future, we can run a recurring campaign that references historical purchasing data to build a tailored outreach to request vendor terms → value added agent
Chart of Accounts Set-Up (this might be a hard one; likely requires a fair bit of human intervention early on)
https://www.loom.com/share/f41917f570d7448b857ee2c1b927325d
Define rules for “best-in-class” Chart of Accounts
Review historical COA and P&L to produce a new and improved COA
Upload COA (I didn’t cover that in my Loom but if you click the dropdown on the ‘New’ button it gives you the ability to upload)
NOTE: this will likely be a hard one and require a fair bit of human intervention early on
Connect Bank Accounts
https://www.loom.com/share/49c26cce066b4899b5528f8fffca5229
Set beginning balance entries (via Chart of Accounts as of start date)
Delete beginning balance entries (automatic entries from connecting bank accounts)
Automatic Bill Entry [priority]
https://www.loom.com/share/a6f3afdb3abc41d09b3ba1e371cdcaae
Create list of all bills that need to be imported
Map fields so that bills are created automatically in QBO
Automatic Invoice Creation [priority]
https://www.loom.com/share/57be961ec5494e83b79f8cfbeff72eba
Must set beginning balances for customers before entering invoices
Enter invoices for each customer to show total amount owed over time
Applying Payments to Invoices
https://www.loom.com/share/71977f8ae56c4ca19268c5ba30199d1e

Files Required from QBD
Files Required from QBD
Customer List
AR Aging (as of start date)
Vendor List
AP Aging (as of start date)

Future Capabilities:
Auto-refresh using refresh tokens.
Trigger post-sync processing agents (e.g., cleanup, categorization).
Graph insights, anomaly detection, memory graph relationships.

Tech Stack
| Layer              		| Tool/Service                		| Purpose                                 		|
| -------------------------------- | -------------------------------------------- | -------------------------------------------------------- |
| **Frontend**      	| Next.js + React            		| Admin UI tab to connect + view data     	|
| **Backend**       	| FastAPI (Python)         		| QBO OAuth + data fetch logic            	|
| **Database**       	| Supabase Postgres     		| Store financial data per client         	|
| **Auth**         		| Supabase Auth            		| Admin users + client linking            	|
| **Queue (Future)**	| Redis + Background Worker 	| Long-running syncs or auto-refresh jobs 	|
| **Storage**        	| Google Drive              		| Reference old files if needed           	|
| **Integration**    	| QBO REST API              		| Auth, data access                     	  	|
| **Docs**           		| README / Notion           		| Internal usage guide                    		|

MVP Plan of Attack
Phase 1: QBO OAuth Integration
Register QBO sandbox app to get client ID/secret.
Build FastAPI route (ALT: use Flask/local setup on dummy business) to:
Start OAuth flow.
Capture callback.
Exchange code for access/refresh tokens.
Store tokens encrypted in Supabase (linked to client ID).

Phase 2: Fetch Financial Data
Define Supabase tables: chart_of_accounts, transactions, pnl_reports, invoices.
Write FastAPI service to:
Pull each dataset via QBO API.
Store/overwrite data in Supabase.
Test locally with mock data and real sandbox pulls.

Phase 3: Dashboard UI (Admin Tool)
Add a tab under each client’s dashboard for “QuickBooks”.
Display basic sync info (last synced, datasets available).
Add button: “Connect QBO” → triggers OAuth.
Add button: “Sync Data” → triggers FastAPI endpoint.
Show sample financial tables.

Phase 4: Documentation & Review
Write README/Notion doc: setup, usage, architecture.
Build simple admin log/debug view for fetched data.
Schedule internal demo with stakeholders.
Collect feedback for next version.

Stretch Goals (After MVP)
Auto-refresh daily using QBO refresh tokens + Redis jobs.
Use parsed data in downstream agents (e.g., financial cleanup, Q&A).
Generate dashboards with charts and metrics.
Map unstructured Google Drive files to structured records (hybrid migration).
Trigger alerts for anomalies, duplicate entries, or major changes.
