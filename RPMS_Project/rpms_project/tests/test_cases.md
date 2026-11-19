# Manual test cases

| ID | Scenario | Input / Action | Expected result |
|---|---|---|---|
| TC01 | Add valid candidate | Unique email/mobile; percentage 75; backlogs 0 | Candidate code generated and record saved |
| TC02 | Duplicate email | Reuse an existing email | MySQL UNIQUE error; no duplicate record |
| TC03 | Invalid percentage | Percentage 105 | Validation error; record not saved |
| TC04 | Negative backlog | Backlogs -1 | Validation error |
| TC05 | Add valid company | New company name | Company code generated |
| TC06 | Create job | Existing company, positive openings, valid deadline | Job code generated |
| TC07 | Invalid package range | Min package > max package | Validation error |
| TC08 | Eligible candidate applies | Meets all job criteria | Application created as APPLIED / ELIGIBLE |
| TC09 | Ineligible candidate applies | Below minimum percentage or excess backlogs | Application blocked with reason |
| TC10 | Duplicate application | Same candidate and job twice | Second application blocked |
| TC11 | Invalid workflow jump | APPLIED → JOINED | WorkflowError; status unchanged |
| TC12 | Valid workflow | APPLIED → SHORTLISTED | Status and history saved |
| TC13 | Schedule interview | Future date and unique round number | Interview created |
| TC14 | Past interview | Date before today | Validation error |
| TC15 | Feedback rating | Rating 6 | Validation error |
| TC16 | Create offer | Selected application | Offer created; status moves to OFFERED |
| TC17 | Confirm joining | Valid offer and actual date | Placement created; candidate marked PLACED; application JOINED |
| TC18 | Reports | Run reports menu | Aggregated reports returned |
