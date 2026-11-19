from rpms.service.rpms_service import RPMSService as S

def show(title, rows):
    print('\n'+title+'\n'+'-'*90)
    if not rows: print('No records found.'); return
    for r in rows:
        print(' | '.join(f'{k}: {v}' for k,v in r.items()))

def ask(label, default=''):
    value=input(f'{label}'+(f' [{default}]' if default else '')+': ').strip()
    return value or default

def main():
    while True:
        print('''\n========== RECRUITMENT & PLACEMENT MANAGEMENT SYSTEM ==========\n1 Candidates  2 Companies  3 Jobs  4 Applications  5 Interviews\n6 Offers  7 Placements  8 Reports  9 Exit''')
        choice=ask('Choose module')
        try:
            if choice=='1':
                sub=ask('1 Add | 2 Search/View | 3 Deactivate')
                if sub=='1':
                    code=S.add_candidate(ask('Full name'),ask('Email'),ask('10-digit mobile'),ask('Qualification','BE'),ask('Passing year'),ask('Percentage','0'),ask('Backlogs','0'),ask('Primary technology','Python'),ask('College'),ask('Location','Pune')); print('Created:',code)
                elif sub=='2': show('CANDIDATES',S.candidates(ask('Search name/email/code (blank for all)')))
                elif sub=='3':
                    cid=ask('Candidate ID'); from rpms.dao.connection import Database as DB
                    DB.execute("UPDATE candidates SET profile_status='INACTIVE' WHERE candidate_id=%s",(cid,)); print('Candidate deactivated.')
            elif choice=='2':
                if ask('1 Add company | 2 View companies')=='1': print('Created:',S.add_company(ask('Company name'),ask('Industry'),ask('Location'),ask('Website')))
                else: show('COMPANIES',S.companies())
            elif choice=='3':
                if ask('1 Create job | 2 View open jobs | 3 View all jobs')=='1': print('Created:',S.add_job(ask('Company ID'),ask('Job title'),ask('Location'),ask('Openings','1'),ask('Min package LPA','0'),ask('Max package LPA','0'),ask('Min percentage','0'),ask('Min passing year','2020'),ask('Max passing year','2030'),ask('Max backlogs','0'),ask('Deadline YYYY-MM-DD')))
                else: show('JOBS',S.jobs(ask('Open only? y/n','y').lower()=='y'))
            elif choice=='4':
                if ask('1 Apply | 2 View applications | 3 Change status')=='1':
                    cid,jid=ask('Candidate ID'),ask('Job ID'); print(S.eligibility(cid,jid)); print('Application:',S.apply(cid,jid))
                elif ask('View/change? 2 or 3','2')=='2': show('APPLICATIONS',S.applications())
                else: S.change_status(ask('Application ID'),ask('New status'),ask('Remarks')); print('Status updated.')
            elif choice=='5':
                if ask('1 Schedule | 2 View | 3 Add feedback')=='1': print('Interview ID:',S.schedule_interview(ask('Application ID'),ask('Round number','1'),ask('Round type','TECHNICAL'),ask('Date YYYY-MM-DD'),ask('Mode ONLINE/OFFLINE','ONLINE'),ask('Interviewer')))
                elif ask('View/feedback? 2 or 3','2')=='2': show('INTERVIEWS',S.interviews())
                else: S.save_feedback(ask('Interview ID'),ask('Technical rating','0'),ask('Communication rating','0'),ask('Problem solving rating','0'),ask('Overall rating','0'),ask('Recommendation NEXT_ROUND/SELECTED/REJECTED/ON_HOLD'),ask('Remarks')); print('Feedback saved.')
            elif choice=='6':
                if ask('1 Create offer | 2 View offers')=='1': print('Offer:',S.create_offer(ask('Application ID'),ask('Designation'),ask('Package LPA'),ask('Offer date YYYY-MM-DD'),ask('Expected joining date YYYY-MM-DD')))
                else: show('OFFERS',S.offers())
            elif choice=='7': S.confirm_joining(ask('Offer ID'),ask('Actual joining date YYYY-MM-DD')); print('Placement confirmed.')
            elif choice=='8':
                for name,rows in S.reports().items(): show(name.replace('_',' ').upper(),rows)
            elif choice=='9': print('Thank you.'); break
            else: print('Choose a valid menu number.')
        except Exception as e: print('ERROR:',e)

if __name__=='__main__': main()
