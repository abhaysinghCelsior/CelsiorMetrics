from django.conf import settings
from django.shortcuts import render, redirect,render_to_response
from django.template import RequestContext
from swMetrics.home.models import UsrLgn,Role,ProjectOwner,Client,MasterProject,Project,Subordinates,AppMetrics,Metrics,MetricsMonth,MetricsMonthStatus
from swMetrics.home.models import MetricsBenchMark,WeightedDefectDensity,QARemovalEfficiency,OnTimeDelivery,WeightedCodeReviewEffectiveness
from swMetrics.home.models import AutomatedUnitTestingEffectiveness,EffortVariance,TmpPswd,DefectSummary
from django.core.exceptions import ValidationError
from django.contrib import messages
import swMetrics.home.genPPTRep as PPT_REP
import swMetrics.home.Generic as G
import schedule
import time
from swMetrics.home.configMet import SCH_FLG,SCH_OPT1,SCH_OPT2,SCH_TM


def WCRE(request):
    context={'FLG':'S'}
    if request.POST.get('WCRE', None) == 'WCRE':
        upd=G.saveWCRE(request)
        M_L=request.session['MAT_LIST']
        M_L.append("WCRE")
        request.session['MAT_LIST']=M_L
        if((upd=='U') or (upd=='C')):
            context['FLG']='N'
        if(upd=='C'):
            messages.success(request, "WCRE ADDED FOR PROJECT"+request.session['PROJECT']+ "Month:"+request.session['MONTH'])
        elif(upd=='V'):
                messages.success(request, "Object or Comments Count can Only Accept Numeric Value")
        elif(upd=='-'):
                messages.success(request, "None of number should be -Ve")
        elif(upd=='N'):
                messages.success(request, "Fields Should Not Be Null")
        elif(upd=='W'):
                messages.success(request, "STATIC, PEER OR ARCH can be only Y OR N")
        elif(upd=='E'):
                messages.success(request, "Files reviewed can't be more than total files &review comments incorporated can't be more than review comments")
        elif(upd=='Z'):
                messages.success(request, "Total Files & Files reviewed can't be Zero")
        elif(upd=='B'):
            messages.success(request, "Data point is outlier(beyond benchmarck), Put Remarks!!")
        else:
            messages.success(request, "WCRE UPDATED FOR PROJECT"+request.session['PROJECT']+ "Month:"+request.session['MONTH'])
    if request.POST.get('WCRE-N', None) == 'WCRE-N':
        return redirect( 'http://127.0.0.1:8000/swMetrics/home_pm' ) 
    return render(request, 'swMetrics/WCRE.html',context)

def DefectSummaryData(request):
        PRJ_KEY=request.session['PROJECT']
        MON=request.session['MONTH']
        RC_CHOICES,DEFECTSOURCE_CHOICES=getRCandDS("Y")
        WDDIns=WeightedDefectDensity.objects.get(Project_Key=PRJ_KEY,Month_of_Metrics=MON)
        DEF_LIST=[]
        idx=0
        while idx < WDDIns.No_Of_Critical_Defects:
                idx=idx+1
                DEF_LIST.append('Critical')
        idx=0
        while idx < WDDIns.No_Of_High_Defects:
                idx=idx+1
                DEF_LIST.append('High')
        idx=0
        while idx < WDDIns.No_Of_Medium_Defects:
                idx=idx+1
                DEF_LIST.append('Medium')
        idx=0
        while idx < WDDIns.No_Of_Low_Defects:
                idx=idx+1
                DEF_LIST.append('Low')
                
        if request.POST.get('Add', None) == 'Add':
                DefectId=request.POST.getlist('DefectId', None)
                DefectSrc_I=request.POST.getlist('DEFECTSOURCE', None)
                RC_I=request.POST.getlist('RC', None)

                ret=G.ValidateDefectSummaryInputs(DefectId, DefectSrc_I,RC_I,request)
                if(ret=='S'):
                        ret=G.addDefectSummary(DefectId, DefectSrc_I,RC_I,DEF_LIST,PRJ_KEY,MON)
                        if(ret=='S'):
                                messages.success(request, "Added/Updated Defect Summary")
                        if(ret=='E'):
                                messages.success(request, "Error in Adding/Updating Defect Summary")
        context={
                'DEFECTSOURCE_CHOICES':DEFECTSOURCE_CHOICES,
                'RC_CHOICES':RC_CHOICES,
                'DEF_LIST':DEF_LIST,
                }
        return render(request, 'swMetrics/DefectSummaryData.html', context)


def WDD(request):
    context={'FLG':'S'}
    context['FLG']=isNext(request.session['PROJECT'],request.session['MONTH'])
    upd='C'
    if request.POST.get('WDD', None) == 'WDD':
        DevHrs=request.POST.get('Dev_Hours', None)
        C=request.POST.get('No_Of_Critical_Defects', None)
        H=request.POST.get('No_Of_High_Defects', None)
        M=request.POST.get('No_Of_Medium_Defects', None)
        L=request.POST.get('No_Of_Low_Defects', None)
        if(C.isnumeric() and H.isnumeric() and M.isnumeric() and L.isnumeric() and is_number(DevHrs)):
                DevHrs=float(request.POST.get('Dev_Hours', None))
                C=int(request.POST.get('No_Of_Critical_Defects', None))
                H=int(request.POST.get('No_Of_High_Defects', None))
                M=int(request.POST.get('No_Of_Medium_Defects', None))
                L=int(request.POST.get('No_Of_Low_Defects', None))
                upd=G.saveWDD(request,DevHrs,C,H,M,L,request.session['PROJECT'],request.session['MONTH'])
                M_L=request.session['MAT_LIST']
                M_L.append("WDD")
                request.session['MAT_LIST']=M_L

        else:
                print("Validation failed")
                upd='V' # VALIDATION FAILED
        if(upd=='E'):
            messages.success(request, "Planned Effort Can't be Zero")
        elif(upd=='C'):
            messages.success(request, "WDD ADDED FOR PROJECT"+request.session['PROJECT']+ "Month:"+request.session['MONTH'])
        elif(upd=='V'):
            messages.success(request, "DevHrs only Accept Decimal and Other Fields Only Accept Numeric")
        elif(upd=='B'):
            messages.success(request, "Data point is outlier(beyond benchmarck), Put Remarks!!")
        elif(upd=='-'):
                messages.success(request, "None of number should be -Ve")
        else:
            messages.success(request, "WDD UPDATED FOR PROJECT"+request.session['PROJECT']+ "Month:"+request.session['MONTH'])
    if request.POST.get('WDD-N', None) == 'WDD-N':
        return redirect( 'http://127.0.0.1:8000/swMetrics/home_pm' ) 
    return render(request, 'swMetrics/WDD.html',context)
                
def EV(request):
        context={'FLG':'S'}
        if request.POST.get('EV', None) == 'EV':
                upd=G.saveEV(request)
                M_L=request.session['MAT_LIST']
                M_L.append("EV")
                request.session['MAT_LIST']=M_L
                if((upd=='U') or (upd=='C')):
                    context['FLG']='N'
                G.GEN_MSG(upd,request,'OTD','Planned Effort','Actual Effort')
        if request.POST.get('EV-N', None) == 'EV-N':
                return redirect( 'http://127.0.0.1:8000/swMetrics/home_pm' ) 
        return render(request, 'swMetrics/EV.html',context)

          
def QRE(request):
        context={'FLG':'S'}
        if request.POST.get('QRE', None) == 'QRE':
                upd=G.saveQRE(request)
                M_L=request.session['MAT_LIST']
                M_L.append("QRE")
                request.session['MAT_LIST']=M_L
                if((upd=='U') or (upd=='C')):
                    context['FLG']='N'
                GEN_MSG(upd,request,'QRE','QA Defects','After QA Defects')
        if request.POST.get('QRE-N', None) == 'QRE-N':
                return redirect( 'http://127.0.0.1:8000/swMetrics/home_pm' ) 
        return render(request, 'swMetrics/QRE.html',context)
     
def OTD(request):
        context={'FLG':'S'}
        print("OTD")
        if request.POST.get('OTD', None) == 'OTD':
                upd=G.saveOTD(request)
                M_L=request.session['MAT_LIST']
                M_L.append("OTD")
                request.session['MAT_LIST']=M_L
                if((upd=='U') or (upd=='C')):
                    context['FLG']='N'
                GEN_MSG(upd,request,'OTD','Total Delivery','Total Delivery On Time')
        if request.POST.get('OTD-N', None) == 'OTD-N':
                print("To HOME_PM")
                return redirect( 'http://127.0.0.1:8000/swMetrics/home_pm' )
        print(context)
        return render(request, 'swMetrics/OTD.html',context)

def AUTE(request):
        context={'FLG':'S'} 
        if request.POST.get('AUTE', None) == 'AUTE':
                upd=G.saveAUTE(request)
                M_L=request.session['MAT_LIST']
                M_L.append("AUTE")
                request.session['MAT_LIST']=M_L
                if((upd=='U') or (upd=='C')):
                    context['FLG']='N'
                GEN_MSG(upd,request,'AUTE','Unit_Testing_Coverage','Percentage_Of_Unit_Cases_Passed')
        if request.POST.get('AUTE-N', None) == 'AUTE-N':
                return redirect( 'http://127.0.0.1:8000/swMetrics/home_pm' ) 
        return render(request, 'swMetrics/AUTE.html',context)

def home_pm(request):
        context={}
        MAT_LIST=[]
        print('Home_PM')
        if( 'IN_PROGRESS' not in  request.session):
                print('Home_PM-IF')
                Month_T=MetricsMonth.objects.filter(Status='A').values_list('Month')
                for type in Month_T:
                        for value in type:
                                Month=value
                EMP_ID=request.session['EmpId']
                print("Home_pm:"+str(Month)+"Month:" +Month)
                PRJ_LIST_T=ProjectOwner.objects.filter(Project_PM_EmpId=EMP_ID).values_list('Project_Key')
                PRJ_LIST = []
                for type in PRJ_LIST_T:
                        for value in type:
                                PRJ_LIST.append(value)

                context={
                'PRJ_LIST':PRJ_LIST,
                'Month':Month
                }
                PRJ_Key=request.POST.get('Assign', None)
                request.session['PRJ_LIST'] = PRJ_LIST
                #print("PRJ_Key from submit:"+PRJ_Key+":")
                MAT_LIST = []
                request.session['MONTH'] = Month
                if (PRJ_Key is not None) :
                        print("inside if")
                        request.session['PROJECT'] = PRJ_Key
                        request.session['IN_PROGRESS'] = 'Y'
                        request.session['MAT_LIST']=[]
                        request.session['PRJ_LIST'] = PRJ_LIST
                        MAT_LIST_T=AppMetrics.objects.filter(Project_Key=PRJ_Key).values_list('Metrics')
                        print(MAT_LIST_T)
                        for type in MAT_LIST_T:
                                for value in type:
                                        print(value)
                                        MAT_LIST.append(value)
                        print('user clicked summary-home_pm')
                        request.session['MAT_LIST-COMP']=MAT_LIST
        if(('IN_PROGRESS' in  request.session) and (request.session['IN_PROGRESS']=='Y')):
                print('Home_PM-IF-2')
                MET_ALREADY_GEN=request.session['MAT_LIST']
                MAT_LIST=request.session['MAT_LIST-COMP']
                print(MAT_LIST)
                print(MET_ALREADY_GEN)
                for mat in MAT_LIST:
                        if mat not in MET_ALREADY_GEN:
                                print(mat)
                                link='http://127.0.0.1:8000/swMetrics/home_pm/'+mat
                                return redirect( link)

                messages.success(request, "Metrics data filled the Project "+request.session['PROJECT']+" For Month:"+request.session['MONTH'])
                del request.session['IN_PROGRESS']
                for mat in MET_ALREADY_GEN:
                        del mat
                context['PRJ_LIST']=request.session['PRJ_LIST'] 
                """
                del request.session['MONTH']
                del request.session['PROJECT']
                """
        return render(request, 'swMetrics/home_pm.html',context)

def GenReport(request):
        YR=[]
        FR=[]
        TO=[]
        messages.success(request, "")
        FR.append("None")
        TO.append("None")
        YR.append("None")
        for key in MetricsMonth.objects.all().order_by('-Month'):
            FR.append(key.Month)
            TO.append(key.Month)
            MN=key.Month.split("-")
            if MN[0] not in YR:
                YR.append(MN[0])
        

        if request.POST.get('REP', None) == 'REP':
                Flg,Opt1,Opt2=PPT_REP.valReport(request,YR,FR,TO)
                PPT_Name,PPT_TITLE,VALID_MONTH=PPT_REP.getPPTInfo(Flg,Opt1,Opt2)
                SUCC=['1','2','3']
                if Flg in SUCC:
                    ret=PPT_REP.ProduceRep(request.session['MONTH'],Flg,Opt1,Opt2,VALID_MONTH,PPT_Name,PPT_TITLE)
                    if ret==-1:
                        messages.success(request, "InValid Metrics")
                        return render(request, 'swMetrics/GenReport.html', {})
                G.dispReportMsg(Flg,PPT_Name,request)
                
        context={'YR':YR, 'FR':FR,'TO':TO}
        return render(request, 'swMetrics/GenReport.html', context)

def home_pmo(request):
        request.session['PROJECT_COUNT']=G.PrjCount()
        request.session['METRICS_COUNT']=G.MetCount()
        request.session['USER_COUNT']=G.UsrCount()
        request.session['MONTH']=G.getOpenMonth()
        return render(request, 'swMetrics/home_pmo.html',{})

"""
def index(request):
        print("Index")
        return render_to_response('home/index.html', {})
"""

def home(request):
        context={
                'Usr_Id':request.session['Usr_Id'],
                'Role':request.session['Role']
                }
        return render_to_response('swMetrics/home.html', context)
       
def contact(request):
        context={
                'Usr_Id':request.session['Usr_Id'],
                'Role':request.session['Role']
                }
        return render_to_response('swMetrics/contact.html', context)

def AssignMetrics(request):
        CLIENT_CHOICES_T=Client.objects.values_list('Client')
        CLIENT_CHOICES = []
        MASTER_PRJ_CHOICES=[]
        PRJ_CHOICES=[]
        METRICS_CHOICES=[]
        PRJ_KEY=""
        for type in CLIENT_CHOICES_T:
                for value in type:
                        CLIENT_CHOICES.append(value)
        print("AssignMetrics")
        print(CLIENT_CHOICES)
        if request.method == "POST":
                Client_I=str(request.POST.get('Client', None))
                print('Client_I'+Client_I)
                MASTER_PRJ_CHOICES_T=MasterProject.objects.filter(Client=Client_I).values_list('MasterProject')
                MASTER_PRJ_CHOICES = []
                for type in MASTER_PRJ_CHOICES_T:
                      for value in type:
                         MASTER_PRJ_CHOICES.append(value)
                print(MASTER_PRJ_CHOICES)
                MASTER_PRJ_I=str(request.POST.get('MasterProject', None))
                print('MASTER_PRJI'+MASTER_PRJ_I)
                PRJ_CHOICES_T=Project.objects.filter(Project_MasterProject=MASTER_PRJ_I).values_list('Project')
                PRJ_CHOICES = []
                for type in PRJ_CHOICES_T:
                      for value in type:
                         PRJ_CHOICES.append(value)
                print(PRJ_CHOICES)
                PRJ_I=str(request.POST.get('Project', None))
                print('PRJ_I'+PRJ_I)
                METRICS_CHOICES_T=Metrics.objects.values_list('Metrics')
                METRICS_CHOICES = []
                for type in METRICS_CHOICES_T:
                      for value in type:
                         METRICS_CHOICES.append(value)
                print(METRICS_CHOICES)
                CLIENT_CHOICES,MASTER_PRJ_CHOICES,PRJ_CHOICES=resetDropDownKeepSelected(CLIENT_CHOICES,Client_I,MASTER_PRJ_CHOICES,MASTER_PRJ_I,PRJ_CHOICES,PRJ_I)
                MAT_I=request.POST.getlist('Metrics', None)
                MAT=" & ".join(str(x) for x in MAT_I)
                PRJ_KEY=Client_I+"_"+MASTER_PRJ_I+"_"+PRJ_I
                if request.POST.get('Assign', None) == 'Assign':
                        print('user clicked summary')
                        G.saveAppMetrics(MAT_I,PRJ_KEY)
                        messages.success(request, "Metrics "+ MAT +" have been allocated to the Project "+PRJ_KEY)
        AppMetricsList=AppMetrics.objects.all().values_list('Project_Key').order_by('Project_Key')
        APP_METRICS_PRJ = []
        for type in AppMetricsList:
                for value in type:
                        APP_METRICS_PRJ.append(value)
        AppMetricsList=AppMetrics.objects.all().values_list('Metrics').order_by('Project_Key')
        APP_METRICS = []
        for type in AppMetricsList:
                for value in type:
                        APP_METRICS.append(value)

        for idx in APP_METRICS_PRJ:
                print("-------------")
                print(idx)

   
        context={
                'CLIENT_CHOICES':CLIENT_CHOICES,
                'MASTER_PRJ_CHOICES':MASTER_PRJ_CHOICES,
                'PRJ_CHOICES':PRJ_CHOICES,
                'METRICS_CHOICES':METRICS_CHOICES,
                'APP_METRICS_PRJ':APP_METRICS_PRJ,
                'APP_METRICS':APP_METRICS
                }
        return render(request, 'swMetrics/AssignMetrics.html', context)

def AssignRole(request):
        USER_CHOICES_T=UsrLgn.objects.filter(UsrLgn_Role='B').values_list('UsrLgn_EmpId')
        USER_CHOICES = []
        for type in USER_CHOICES_T:
                for value in type:
                        USER_CHOICES.append(value)
        if request.method == "POST":
                USER_I=str(request.POST.get('USER', None))
                USR=int(USER_I)
                if(USER_I!='None'):
                        for cl in USER_CHOICES:
                                if(cl!=USR):
                                        print("remove"+str(USER_I))
                                        USER_CHOICES.remove(cl)
                print("After"+USER_I)
                if request.POST.get('Assign', None) == 'Assign':
                        print('user clicked summary')
                        USER=UsrLgn.objects.get(UsrLgn_EmpId=USR)
                        USER.UsrLgn_Role='P'
                        USER.save()
                        messages.success(request, "User " + str(USER_I) + " can fill data for Metrics ")
   
        context={
                'USER_CHOICES':USER_CHOICES,
                }
        return render(request, 'home/AssignRole.html', context)


def AssignMetricsOwner(request):
        PRJ_CHOICES_T=Project.objects.values_list('Project_Key')
        PRJ_CHOICES = []
        USER_CHOICES=[]
        TEMP=[]
        for type in PRJ_CHOICES_T:
                for value in type:
                        PRJ_CHOICES.append(value)
        if request.method == "POST":
                Project_I=str(request.POST.get('Project', None))
                print('Project_I'+Project_I)
                print(PRJ_CHOICES)
                if(Project_I!=None):
                        PRJ_CHOICES=[Project_I]
                print("------------After----------")
                print(PRJ_CHOICES)

                USER_CHOICES_T=UsrLgn.objects.filter(UsrLgn_Role='P').values_list('UsrLgn_EmpId')
                USER_CHOICES = []
                for type in USER_CHOICES_T:
                      for value in type:
                         USER_CHOICES.append(value)
                print(USER_CHOICES)
                USER_I=request.POST.get('USER', None)
                if(USER_I!=None):
                        print("Inside if"+str(USER_I))
                        for cl in USER_CHOICES:
                                if str(cl) != str(USER_I):
                                        print("remove"+str(USER_I)+" :"+str(cl))
                                        USER_CHOICES.remove(cl)

                if request.POST.get('Assign', None) == 'Assign':
                        print('user clicked summary:'+USER_I)
                        if USER_I==None:
                                messages.success(request, "User Id not Given")
                        else:
                                ret=G.saveProjectOwner(Project_I,int(USER_I))
                                if(ret==1):
                                        messages.success(request, "Project " + Project_I + " Has been assigned to "+str(USER_I))
                                else:
                                        messages.success(request, "Project is already assigned")
   
        context={
                'PRJ_CHOICES':PRJ_CHOICES,
                'USER_CHOICES':USER_CHOICES,
                }
        return render(request, 'swMetrics/AssignMetricsOwner.html', context)

def CloseMonth(request):
        MONTH_CHOICES_T=MetricsMonth.objects.filter(Status='A').values_list('Month').order_by('-Month')
        MONTH_CHOICES = []
        for type in MONTH_CHOICES_T:
                for value in type:
                        MONTH_CHOICES.append(value)
        if request.POST.get('CLOSE', None) == 'CLOSE':
                print('Cloes Month')
                MONTH_I=str(request.POST.get('MONTH', None))
                try:
                    MetMnth=MetricsMonth.objects.get(Month=MONTH_I,Status='A')
                except MetricsMonth.DoesNotExist:
                    MetMnth=None
                if MetMnth is None:
                        messages.success(request, "No Month is open FOR METRICS GENERATION")
                else:
                        MetMnth.Status='I'
                        MetMnth.save()
                        messages.success(request, "MONTH  "+MONTH_I+" CLOSED FOR METRICS GENERATION")
        context={
                'MONTH_CHOICES':MONTH_CHOICES,
                }
        return render(request, 'swMetrics/CloseMonth.html', context) 

def InitiateMonth(request):
        MONTH_CHOICES_T=MetricsMonth.objects.all().values_list('Month').order_by('-Month')
        MONTH_CHOICES = []
        ACT_MONTH=""
        print("Triggerting Initiate")

        for type in MONTH_CHOICES_T:
                for value in type:
                        print("adding:"+value+":")
                        MONTH_CHOICES.append(value)
        if request.method == "POST":
                MONTH_I=str(request.POST.get('MONTH', 'None'))
                ACT_MONTH=MONTH_I
                print(MONTH_I)
                print(MONTH_CHOICES)
                if(MONTH_I!='None'):
                        for type in MONTH_CHOICES_T:
                                for value in type:
                                        if(value!=ACT_MONTH):
                                                MONTH_CHOICES.remove(value)
        MONTH = time.strftime("%Y-%m")
        print(MONTH)
        print(MONTH_CHOICES)
        MET_LIST_T=Metrics.objects.all().values_list('Metrics')
        MET_LIST = []
        BENCHMARK_LIST = {}
        BENCHMARK_LIST_T={}
        FLG=''
        for type in MET_LIST_T:
                for value in type:
                        MET_LIST.append(value)

           #.values_list('Metrics','BenchMark')
  

        if request.POST.get('ACTIVE', None) == 'ACTIVE':
                print('ACTIVATE'+ACT_MONTH)
                try:
                        MetMonthOld=MetricsMonth.objects.get(Status='A')
                except MetricsMonth.DoesNotExist:
                        MetMonthOld=None
                if MetMonthOld is None:
                    print("if")
                    MetMonth=MetricsMonth(Month=ACT_MONTH)
                    MetMonth.Status='A'
                    MetMonth.save()
                    FLG='A'
                    request.session['FLG']='A'
                    BENCHMARK_LIST_T=MetricsBenchMark.objects.filter(Month=ACT_MONTH)   #.values_list('Metrics','BenchMark')
                    messages.success(request, "MONTH  "+ACT_MONTH+" ADDED FOR METRICS GENERATION")
                elif(MetMonthOld.Month!=MONTH_I):
                    messages.success(request, "MONTH  "+MetMonthOld.Month+" IS ALREADY Active, Pls Close it")
                else:
                    messages.success(request, "MONTH  "+ACT_MONTH+" IS ALREADY ADDED FOR METRICS GENERATION")
   

                        
        if request.POST.get('ADD', None) == 'ADD':
                print("------------Month in add "+MONTH)
                BENCHMARK_LIST_T=MetricsBenchMark.objects.filter(Month=MONTH)
                
                FLG,ActMonth=saveMonth(MONTH)
                request.session['FLG']=FLG
                if FLG=='C':
                        messages.success(request, "MONTH  "+MONTH+" ADDED FOR METRICS GENERATION")
                elif FLG =='I':
                        messages.success(request, "MONTH  "+MONTH+" IS ALREADY ADDED & INACTIVE-BENCH MARK CAN'T BE UPDATED")
                elif FLG =='S':
                        messages.success(request, "MONTH  "+ActMonth+" IS ALREADY Active, Pls Close it")
                else:
                        messages.success(request, "MONTH  "+MONTH+" IS ALREADY ADDED FOR METRICS GENERATION")

        for BnMrk in BENCHMARK_LIST_T:
                BENCHMARK_LIST[BnMrk.Metrics]=BnMrk.BenchMark
        #Reset to 0
        if not BENCHMARK_LIST:
                for key in MET_LIST:
                        BENCHMARK_LIST[key]=0
        print(BENCHMARK_LIST)
        if request.POST.get('BNHMRK', None) == 'BNHMRK':
                print("FLG in bench"+request.session['FLG'])
                for key in MET_LIST:
                        MON_BEN=request.POST.get(key, None)
                        if(request.session['FLG']=='A'):
                                ret=G.saveBenchMark(ACT_MONTH,key,float(MON_BEN))
                        else:
                                ret=G.saveBenchMark(MONTH,key,float(MON_BEN))
                if(request.session['FLG']=='A'):
                     messages.success(request, "BENCH MARK UPDATED FOR THE "+ACT_MONTH)
                elif(ret=='C'):
                        messages.success(request, "BENCH MARK SET FOR THE "+MONTH)
                elif(ret=='I'):
                        messages.success(request, "MONTH "+MONTH +" IS INACTIVE-BENCH MARK CAN'T BE UPDATED")
                else:
                        messages.success(request, "BENCH MARK UPDATED FOR THE "+MONTH)

        if(request.session['FLG'] is None):
                request.session['FLG']='E' 
        context={
                'MONTH_CHOICES':MONTH_CHOICES,
                'MONTH':MONTH,
                'MET_LIST':MET_LIST,
                'BENCHMARK_LIST':BENCHMARK_LIST,
                'FLG':FLG,
                'ACT_MONTH':ACT_MONTH
                }
        return render(request, 'swMetrics/InitiateMonth.html', context)    


