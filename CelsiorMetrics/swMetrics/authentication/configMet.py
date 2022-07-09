REP_PATH="D:\Pyramid\Python\PydMetrics\Reports\ "
SMTP=  'smtp.office365.com' # 'smtp.gmail.com' 'smtp.office365.com' 
FROM='abhay.singh@celsiortech.com' #'abhayk007@gmail.com' 'abhay.singh@celsior.com'
PORT=587 # or 587 465 993
EMAIL_BODY="""
Hi PMO

        Please find attacted current report
        Below metrics are not generted!!

"""
EMAIL_TAIL="""
Regards

Celsior Quality Tool
"""
REP_NM="SW_MET"
EXT=".pptx"
MET1_TITLE="""
Weighted Defect Density(WDD)
Measures the quality of development-Weighted defects per hour of development
WDD = (5*No of Critical Defects+3*No of High Defects+1*No of Med defects+0.5*No of Low defects)
                                                                / Development Effort (Hrs.)      
Benchmark:0.025 weighted defects per hour
"""
MET2_TITLE="""
On Time Delivery (OTD)
Measures the percentage of deliveries on time
OTD = (Total Number of tasks delivered on time/ Total Number of tasks delivered)      
Benchmark: 95%
"""
MET3_TITLE="""
QA removal efficiency (QRE)
Measure of the QA team’s ability to remove defects prior to release
QRE = (Defects removed during QA Testing phase/ Total number of defect raised) X 100      
Benchmark: 94%
"""
MET4_TITLE="""
Automated Unit Testing Effectiveness (AUTE)
Measures effectiveness of unit testing in terms of unit testing coverage and Unit test case passed %
AUTE= 5* (Unit Testing Coverage %) * (% of Unit test cases passed)       Benchmark: 4.0
"""
MET5_TITLE="""
Weighted Code Review effectiveness(WCRE)
Measures how strictly the Code Review process has been followed in terms of % of files reviewed
                        and % of review comments incorporated
WCRE=5*(# Files Reviewed/# Files changed)*(# Comments incorporated/ # Review comments)      
Benchmark: 4.0 %
"""
MET6_TITLE="""
Effort Variance(EV)
Measures effort taken to complete the task in comparison to effort planned
EV=( Actual Effort-Planned Effort)/Planned Effort      
Benchmark: 5%Back
"""
SlideNoStartingMet=2
NO_of_MET=6
SCH_FLG="1"
SCH_OPT1="6"
SCH_OPT2=None
SCH_TM="19:35"
