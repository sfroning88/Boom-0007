# Boom-0007<br>

*Goal:*<br>
Build a backend service + dashboard tool that simplifies and automates the messy client transition from QuickBooks Desktop to QuickBooks Online. It will:<br>
-> Connect to the client’s QBO account.<br>
-> Fetch and store financial data.<br>
-> Display data in the admin dashboard.<br>
-> Allow staff to trigger and verify syncs.<br>
-> Prepare the data for downstream reporting and AI agents.<br>

*Why It Matters:*<br>
Today, clients store their messy QB Desktop exports in Google Drive and our team manually decodes them. This is slow, error-prone, and doesn’t scale. Migrating to QBO gives us API access to structured financial data. Automating this unlocks faster onboarding, cleaner data, and intelligent tools powered by real financials.<br>

*QuickBooks Migration Assistant*<br>
Core Use Case:<br>
For each client, pull structured financial data from their QBO account and organize it in Supabase for internal tools, financial reports, and agent automation.<br>

*Capabilities (MVP):*<br>
Authenticate with a client’s QBO account (OAuth2.0).<br>
Pull core datasets: Chart of Accounts, P&L, Transactions, Invoices.<br>
Store data into Supabase tables with appropriate client relations.<br>
Manual refresh option.<br>
Display synced data on a dashboard tab.<br>
Simple logs for debugging.<br>

*Requirements (MVP):*<br>
Upload Clean Customer List<br>
-> Scrub QBD export and clean up list with consistent naming conventions, customer hierarchy, and complete information<br>
-> We can probably extract this information using OCR on signed contract documents (PDFs). Can also ask the owner what their customer onboarding process looks like so we can automate the data entry process.<br>
Upload Clean Vendor List<br>
-> Scrub QBD export and clean up list with consistent naming conventions and complete information<br>
-> We can probably extract this information using OCR on incoming invoices. Should ask the owner what their vendor onboarding process looks like so we can automate the data entry process.<br>
-> Potentially do automated vendor outreach to request W-9 forms for compliance clean up.<br>
-> In the future, we can run a recurring campaign that references historical purchasing data to build a tailored outreach to request vendor terms → value added agent<br>
Chart of Accounts Set-Up<br>
-> Define rules for “best-in-class” Chart of Accounts<br>
-> Review historical COA and P&L to produce a new and improved COA<br>
-> Upload COA (I didn’t cover that in my Loom but if you click the dropdown on the ‘New’ button it gives you the ability to upload)<br>
-> NOTE: this will likely be a hard one and require a fair bit of human intervention early on<br>
Connect Bank Accounts<br>
-> Set beginning balance entries (via Chart of Accounts as of start date)<br>
-> Delete beginning balance entries (automatic entries from connecting bank accounts)<br>
Automatic Bill Entry [priority]<br>
-> Create list of all bills that need to be imported<br>
-> Map fields so that bills are created automatically in QBO<br>
Automatic Invoice Creation [priority]<br>
-> Must set beginning balances for customers before entering invoices<br>
-> Enter invoices for each customer to show total amount owed over time<br>
Applying Payments to Invoices<br>

*Files Required from QBD:*<br>
-> Customer List<br>
-> AR Aging (as of start date)<br>
-> Vendor List<br>
-> AP Aging (as of start date)<br>

*Future Capabilities:*<br>
-> Auto-refresh using refresh tokens.<br>
-> Trigger post-sync processing agents (e.g., cleanup, categorization).<br>
-> Graph insights, anomaly detection, memory graph relationships.<br>

*Tech Stack*<br>
| Layer              		           | Tool/Service                		              | Purpose                                 		             |<br>
| -------------------------------- | -------------------------------------------- | -------------------------------------------------------- |<br>
| **Frontend**      	             | Next.js + React            		              | Admin UI tab to connect + view data     	               |<br>
| **Backend**       	             | FastAPI (Python)         		                | QBO OAuth + data fetch logic            	               |<br>
| **Database**       	             | Supabase Postgres     		                    | Store financial data per client         	               |<br>
| **Auth**         		             | Supabase Auth            		                | Admin users + client linking            	               |<br>
| **Queue (Future)**	             | Redis + Background Worker 	                  | Long-running syncs or auto-refresh jobs 	               |<br>
| **Storage**        	             | Google Drive              		                | Reference old files if needed           	               |<br>
| **Integration**    	             | QBO REST API              		                | Auth, data access                     	  	             |<br>
| **Docs**           		           | README / Notion           		                | Internal usage guide                    		             |<br>

*MVP Plan of Attack*<br>
Phase 1: QBO OAuth Integration<br>
-> Register QBO sandbox app to get client ID/secret.<br>
-> Build FastAPI route (ALT: use Flask/local setup on dummy business) to:<br>
-> Start OAuth flow.<br>
-> Capture callback.<br>
-> Exchange code for access/refresh tokens.<br>
-> Store tokens encrypted in Supabase (linked to client ID).<br>

Phase 2: Fetch Financial Data<br>
-> Define Supabase tables: chart_of_accounts, transactions, pnl_reports, invoices.<br>
-> Write FastAPI service to:<br>
-> Pull each dataset via QBO API.<br>
-> Store/overwrite data in Supabase.<br>
-> Test locally with mock data and real sandbox pulls.<br>

Phase 3: Dashboard UI (Admin Tool)<br>
-> Add a tab under each client’s dashboard for “QuickBooks”.<br>
-> Display basic sync info (last synced, datasets available).<br>
-> Add button: “Connect QBO” → triggers OAuth.<br>
-> Add button: “Sync Data” → triggers FastAPI endpoint.<br>
-> Show sample financial tables.<br>

Phase 4: Documentation & Review<br>
-> Write README/Notion doc: setup, usage, architecture.<br>
-> Build simple admin log/debug view for fetched data.<br>
-> Schedule internal demo with stakeholders.<br>
-> Collect feedback for next version.<br>

Stretch Goals (After MVP)<br>
-> Auto-refresh daily using QBO refresh tokens + Redis jobs.<br>
-> Use parsed data in downstream agents (e.g., financial cleanup, Q&A).<br>
-> Generate dashboards with charts and metrics.<br>
-> Map unstructured Google Drive files to structured records (hybrid migration).<br>
-> Trigger alerts for anomalies, duplicate entries, or major changes.<br>
