from datetime import date
from rpms.dao.connection import Database as DB
from rpms.exception.errors import CandidateNotFoundError, JobNotFoundError, CandidateNotEligibleError, WorkflowError
from rpms.util.logger import log_activity

class RPMSService:
    @staticmethod
    def add_candidate(name,email,mobile,qualification,passing_year,percentage,backlogs,technology,college='',location=''):
        if not name.strip(): raise ValueError('Candidate name is required.')
        if '@' not in email: raise ValueError('Enter a valid email address.')
        if len(''.join(x for x in mobile if x.isdigit())) != 10: raise ValueError('Mobile number must contain 10 digits.')
        if percentage is not None and not 0 <= float(percentage) <= 100: raise ValueError('Percentage must be between 0 and 100.')
        if int(backlogs) < 0: raise ValueError('Backlog count cannot be negative.')
        year = date.today().year
        code = f'CAN-{year}-{int(DB.fetch_all("SELECT COUNT(*) n FROM candidates")[0]["n"])+1:04d}'
        DB.execute('''INSERT INTO candidates(candidate_code,full_name,email,mobile,qualification,college,passing_year,percentage,backlog_count,primary_technology,current_location) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                   (code,name.strip(),email.strip().lower(),mobile,qualification,college,int(passing_year),percentage,int(backlogs),technology,location))
        log_activity(f'Candidate created: {code} - {name}')
        return code

    @staticmethod
    def candidates(search=''):
        like=f'%{search}%'
        return DB.fetch_all('''SELECT candidate_id,candidate_code,full_name,email,mobile,qualification,passing_year,percentage,backlog_count,primary_technology,profile_status,placement_status FROM candidates WHERE full_name LIKE %s OR email LIKE %s OR candidate_code LIKE %s ORDER BY candidate_id DESC''',(like,like,like))

    @staticmethod
    def add_company(name,industry,location,website=''):
        code=f'COM-{int(DB.fetch_all("SELECT COUNT(*) n FROM companies")[0]["n"])+1:03d}'
        DB.execute('INSERT INTO companies(company_code,company_name,industry,location,website) VALUES(%s,%s,%s,%s,%s)',(code,name,industry,location,website))
        log_activity(f'Company created: {code} - {name}'); return code

    @staticmethod
    def companies(): return DB.fetch_all('SELECT * FROM companies ORDER BY company_name')

    @staticmethod
    def add_job(company_id,title,location,openings,min_package,max_package,min_percentage,min_year,max_year,max_backlogs,deadline,employment='FULL_TIME'):
        if int(openings)<=0: raise ValueError('Number of openings must be greater than zero.')
        if min_package is not None and max_package is not None and float(min_package)>float(max_package): raise ValueError('Minimum package cannot exceed maximum package.')
        if date.fromisoformat(deadline)<date.today(): raise ValueError('Deadline cannot be in the past.')
        code=f'JOB-{int(DB.fetch_all("SELECT COUNT(*) n FROM jobs")[0]["n"])+1:04d}'
        DB.execute('''INSERT INTO jobs(job_code,company_id,job_title,employment_type,location,openings,min_package_lpa,max_package_lpa,min_percentage,min_passing_year,max_passing_year,max_backlogs,posted_date,application_deadline,status) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,CURDATE(),%s,'OPEN')''',
          (code,int(company_id),title,employment,location,int(openings),min_package,max_package,min_percentage,min_year,max_year,int(max_backlogs),deadline))
        log_activity(f'Job created: {code} - {title}'); return code

    @staticmethod
    def jobs(open_only=False):
        q='''SELECT j.*,c.company_name FROM jobs j JOIN companies c ON c.company_id=j.company_id'''
        if open_only: q+=" WHERE j.status='OPEN' AND j.application_deadline>=CURDATE()"
        return DB.fetch_all(q+' ORDER BY j.job_id DESC')

    @staticmethod
    def eligibility(candidate_id,job_id):
        c=DB.fetch_all('SELECT * FROM candidates WHERE candidate_id=%s',(candidate_id,))
        j=DB.fetch_all('SELECT * FROM jobs WHERE job_id=%s',(job_id,))
        if not c: raise CandidateNotFoundError('Candidate not found.')
        if not j: raise JobNotFoundError('Job not found.')
        c,j=c[0],j[0]; reasons=[]
        if c['profile_status']!='ACTIVE': reasons.append('Candidate profile is not active')
        if j['status']!='OPEN': reasons.append('Job is not open')
        if j['application_deadline']<date.today(): reasons.append('Application deadline has passed')
        if j['min_percentage'] is not None and (c['percentage'] is None or float(c['percentage'])<float(j['min_percentage'])): reasons.append(f"Minimum percentage is {j['min_percentage']}%")
        if j['min_passing_year'] is not None and c['passing_year']<j['min_passing_year']: reasons.append('Passing year is below requirement')
        if j['max_passing_year'] is not None and c['passing_year']>j['max_passing_year']: reasons.append('Passing year is above requirement')
        if c['backlog_count']>j['max_backlogs']: reasons.append(f"Maximum allowed backlogs: {j['max_backlogs']}")
        return not reasons, ('Eligible' if not reasons else '; '.join(reasons))

    @staticmethod
    def apply(candidate_id,job_id,source='INTERNAL'):
        ok,reason=RPMSService.eligibility(candidate_id,job_id)
        if not ok: raise CandidateNotEligibleError(reason)
        if DB.fetch_all('SELECT application_id FROM applications WHERE candidate_id=%s AND job_id=%s',(candidate_id,job_id)):
            raise ValueError('Candidate has already applied for this job.')
        code=f'APP-{int(DB.fetch_all("SELECT COUNT(*) n FROM applications")[0]["n"])+1:05d}'
        conn=DB.connect()
        try:
            cur=conn.cursor()
            cur.execute('''INSERT INTO applications(application_code,candidate_id,job_id,eligibility_status,eligibility_reason,application_status,source) VALUES(%s,%s,%s,'ELIGIBLE',%s,'APPLIED',%s)''',(code,candidate_id,job_id,reason,source))
            aid=cur.lastrowid
            cur.execute("INSERT INTO application_history(application_id,old_status,new_status,remarks,changed_by) VALUES(%s,NULL,'APPLIED','Application submitted',NULL)",(aid,))
            conn.commit()
        except: conn.rollback(); raise
        finally: cur.close(); conn.close()
        log_activity(f'Application created: {code}'); return code

    @staticmethod
    def applications():
        return DB.fetch_all('''SELECT a.application_id,a.application_code,c.full_name,j.job_title,co.company_name,a.eligibility_status,a.application_status,a.applied_at FROM applications a JOIN candidates c ON c.candidate_id=a.candidate_id JOIN jobs j ON j.job_id=a.job_id JOIN companies co ON co.company_id=j.company_id ORDER BY a.application_id DESC''')

    @staticmethod
    def change_status(application_id,new_status,remarks=''):
        allowed={'APPLIED':'SHORTLISTED','SHORTLISTED':'INTERVIEW_SCHEDULED','INTERVIEW_SCHEDULED':'INTERVIEWED','INTERVIEWED':'SELECTED','SELECTED':'OFFERED','OFFERED':'JOINED'}
        row=DB.fetch_all('SELECT application_status FROM applications WHERE application_id=%s',(application_id,))
        if not row: raise ValueError('Application not found.')
        old=row[0]['application_status']; new_status=new_status.upper()
        if new_status=='REJECTED': pass
        elif allowed.get(old)!=new_status: raise WorkflowError(f'Invalid transition: {old} -> {new_status}')
        conn=DB.connect()
        try:
            cur=conn.cursor(); cur.execute('UPDATE applications SET application_status=%s,updated_at=NOW() WHERE application_id=%s',(new_status,application_id))
            cur.execute('INSERT INTO application_history(application_id,old_status,new_status,remarks,changed_by) VALUES(%s,%s,%s,%s,NULL)',(application_id,old,new_status,remarks))
            conn.commit()
        except: conn.rollback(); raise
        finally: cur.close(); conn.close()
        log_activity(f'Application {application_id}: {old} -> {new_status}')

    @staticmethod
    def schedule_interview(application_id,round_no,round_type,scheduled_date,mode,interviewer=''):
        if date.fromisoformat(scheduled_date)<date.today(): raise ValueError('Interview date cannot be in the past.')
        iid=DB.execute('''INSERT INTO interview_rounds(application_id,round_number,round_type,scheduled_date,mode,interviewer_name) VALUES(%s,%s,%s,%s,%s,%s)''',(application_id,round_no,round_type,scheduled_date,mode,interviewer))
        log_activity(f'Interview scheduled: {iid}'); return iid

    @staticmethod
    def interviews(): return DB.fetch_all('''SELECT i.*,a.application_code,c.full_name,j.job_title FROM interview_rounds i JOIN applications a ON a.application_id=i.application_id JOIN candidates c ON c.candidate_id=a.candidate_id JOIN jobs j ON j.job_id=a.job_id ORDER BY i.scheduled_date''')

    @staticmethod
    def save_feedback(interview_id,technical,communication,problem,overall,recommendation,remarks=''):
        for score in (technical,communication,problem,overall):
            if score is not None and not 0<=float(score)<=5: raise ValueError('Ratings must be between 0 and 5.')
        DB.execute('''INSERT INTO interview_feedback(interview_id,technical_rating,communication_rating,problem_solving_rating,overall_rating,recommendation,remarks) VALUES(%s,%s,%s,%s,%s,%s,%s)''',(interview_id,technical,communication,problem,overall,recommendation,remarks))
        DB.execute("UPDATE interview_rounds SET status='COMPLETED' WHERE interview_id=%s",(interview_id,))

    @staticmethod
    def create_offer(application_id,designation,package,offer_date,joining_date=None):
        app=DB.fetch_all('SELECT application_status FROM applications WHERE application_id=%s',(application_id,))
        if not app or app[0]['application_status'] not in ('SELECTED','OFFERED'): raise ValueError('Only selected applications can receive offers.')
        code=f'OFF-{int(DB.fetch_all("SELECT COUNT(*) n FROM offers")[0]["n"])+1:04d}'
        DB.execute('INSERT INTO offers(offer_code,application_id,designation,offered_package_lpa,offer_date,expected_joining_date) VALUES(%s,%s,%s,%s,%s,%s)',(code,application_id,designation,package,offer_date,joining_date))
        RPMSService.change_status(application_id,'OFFERED','Offer created')
        return code

    @staticmethod
    def offers(): return DB.fetch_all('''SELECT o.*,a.application_code,c.full_name FROM offers o JOIN applications a ON a.application_id=o.application_id JOIN candidates c ON c.candidate_id=a.candidate_id ORDER BY o.offer_id DESC''')

    @staticmethod
    def confirm_joining(offer_id,actual_date):
        conn=DB.connect()
        try:
            cur=conn.cursor(dictionary=True)
            cur.execute('''SELECT o.*,a.candidate_id,a.job_id,j.company_id FROM offers o JOIN applications a ON a.application_id=o.application_id JOIN jobs j ON j.job_id=a.job_id WHERE o.offer_id=%s''',(offer_id,))
            r=cur.fetchone()
            if not r: raise ValueError('Offer not found.')
            cur2=conn.cursor()
            cur2.execute("UPDATE offers SET offer_status='ACCEPTED' WHERE offer_id=%s",(offer_id,))
            cur2.execute('''INSERT INTO placements(candidate_id,company_id,job_id,offer_id,designation,final_package_lpa,expected_joining_date,actual_joining_date,joining_status) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,'JOINED')''',(r['candidate_id'],r['company_id'],r['job_id'],offer_id,r['designation'],r['offered_package_lpa'],r['expected_joining_date'],actual_date))
            cur2.execute("UPDATE candidates SET placement_status='PLACED' WHERE candidate_id=%s",(r['candidate_id'],))
            cur2.execute("UPDATE applications SET application_status='JOINED' WHERE application_id=%s",(r['application_id'],))
            cur2.execute("INSERT INTO application_history(application_id,old_status,new_status,remarks,changed_by) VALUES(%s,'OFFERED','JOINED','Joining confirmed',NULL)",(r['application_id'],))
            conn.commit()
        except: conn.rollback(); raise
        finally: conn.close()

    @staticmethod
    def reports():
        return {
          'candidates_by_technology':DB.fetch_all('SELECT COALESCE(primary_technology,"Not specified") technology,COUNT(*) total FROM candidates GROUP BY primary_technology ORDER BY total DESC'),
          'applications_by_status':DB.fetch_all('SELECT application_status,COUNT(*) total FROM applications GROUP BY application_status'),
          'company_placements':DB.fetch_all("SELECT c.company_name,COUNT(*) placed FROM placements p JOIN companies c ON c.company_id=p.company_id WHERE p.joining_status='JOINED' GROUP BY c.company_id,c.company_name ORDER BY placed DESC"),
          'open_jobs':DB.fetch_all("SELECT j.job_code,j.job_title,c.company_name,j.location,j.application_deadline FROM jobs j JOIN companies c ON c.company_id=j.company_id WHERE j.status='OPEN'"),
          'funnel':DB.fetch_all('SELECT COUNT(*) applications,SUM(application_status IN (\'SHORTLISTED\',\'INTERVIEW_SCHEDULED\',\'INTERVIEWED\',\'SELECTED\',\'OFFERED\',\'JOINED\')) shortlisted,SUM(application_status IN (\'INTERVIEW_SCHEDULED\',\'INTERVIEWED\')) interviewed,SUM(application_status IN (\'SELECTED\',\'OFFERED\',\'JOINED\')) selected,SUM(application_status=\'JOINED\') joined FROM applications')
        }
