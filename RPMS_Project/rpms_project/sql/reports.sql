USE rpms_db;
-- Candidates by technology
SELECT COALESCE(primary_technology,'Not specified') technology,COUNT(*) total FROM candidates GROUP BY primary_technology ORDER BY total DESC;
-- Open jobs by company
SELECT c.company_name,j.job_code,j.job_title,j.location,j.application_deadline FROM jobs j JOIN companies c USING(company_id) WHERE j.status='OPEN';
-- Applications by status
SELECT application_status,COUNT(*) total FROM applications GROUP BY application_status;
-- Recruitment funnel
SELECT COUNT(*) applications,SUM(application_status IN ('SHORTLISTED','INTERVIEW_SCHEDULED','INTERVIEWED','SELECTED','OFFERED','JOINED')) shortlisted,SUM(application_status IN ('INTERVIEW_SCHEDULED','INTERVIEWED')) interviewed,SUM(application_status IN ('SELECTED','OFFERED','JOINED')) selected,SUM(application_status='JOINED') joined FROM applications;
-- Company-wise placements
SELECT c.company_name,COUNT(*) placed FROM placements p JOIN companies c USING(company_id) WHERE p.joining_status='JOINED' GROUP BY c.company_id,c.company_name ORDER BY placed DESC;
-- Technology-wise placements
SELECT ca.primary_technology,COUNT(*) placed FROM placements p JOIN candidates ca USING(candidate_id) WHERE p.joining_status='JOINED' GROUP BY ca.primary_technology;
-- Pending interviews
SELECT i.*,a.application_code FROM interview_rounds i JOIN applications a USING(application_id) WHERE i.status='SCHEDULED' ORDER BY scheduled_date;
-- Job aging
SELECT job_code,job_title,DATEDIFF(CURDATE(),posted_date) age_days FROM jobs WHERE status='OPEN';
