# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Create your views here.
from django.shortcuts import render, redirect,render_to_response
from django.contrib.auth import authenticate, login
from .forms import LoginForm, SignUpForm
from django.conf import settings
from django.template import RequestContext
from .models import UsrLgn,Role,ProjectOwner,Client,MasterProject,Project,Subordinates,AppMetrics,Metrics,MetricsMonth,MetricsMonthStatus
from .models import MetricsBenchMark,WeightedDefectDensity,QARemovalEfficiency,OnTimeDelivery,WeightedCodeReviewEffectiveness
from .models import AutomatedUnitTestingEffectiveness,EffortVariance,TmpPswd,DefectSummary
from django.core.exceptions import ValidationError
from django.contrib import messages
import swMetrics.authentication.genPPTRep as PPT_REP
import swMetrics.authentication.Generic as G
import schedule
import time
from swMetrics.authentication.configMet import SCH_FLG,SCH_OPT1,SCH_OPT2,SCH_TM



def WCRE(request,PRJ_KEY):
    context={'FLG':'S'}
    request.session['PROJECT']=PRJ_KEY
    if request.POST.get('WCRE', None) == 'WCRE':
        upd=G.saveWCRE(request)
        if((upd=='U') or (upd=='C')):
            context['FLG']='N'
        if(upd=='C'):
            messages.success(request, "WCRE ADDED FOR PROJECT"+request.session['PROJECT']+ "Month:"+request.session['MONTH'])
        elif(upd=='V'):
                messages.error(request, "Object or Comments Count can Only Accept Numeric Value")
        elif(upd=='-'):
                messages.error(request, "None of number should be -Ve")
        elif(upd=='N'):
                messages.error(request, "Fields Should Not Be Null")
        elif(upd=='W'):
                messages.error(request, "STATIC, PEER OR ARCH can be only Y OR N")
        elif(upd=='E'):
                messages.error(request, "Files reviewed can't be more than total files &review comments incorporated can't be more than review comments")
        elif(upd=='Z'):
                messages.error(request, "Total Files & Files reviewed can't be Zero")
        elif(upd=='B'):
            messages.error(request, "Data point is outlier(beyond benchmarck), Put Remarks!!")
        else:
            messages.success(request, "WCRE UPDATED FOR PROJECT"+request.session['PROJECT']+ "Month:"+request.session['MONTH'])
    return render(request, 'accounts/WCRE.html',context)

def DefectSummaryData(request,PRJ_KEY):
        MON=request.session['MONTH']
        request.session['PROJECT']=PRJ_KEY
        RC_CHOICES,DEFECTSOURCE_CHOICES=G.getRCandDS("Y")
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
                                messages.error(request, "Error in Adding/Updating Defect Summary")
        context={
                'DEFECTSOURCE_CHOICES':DEFECTSOURCE_CHOICES,
                'RC_CHOICES':RC_CHOICES,
                'DEF_LIST':DEF_LIST,
                }
        return render(request, 'accounts/DefectSummaryData.html', context)


def WDD(request,PRJ_KEY):
    context={'FLG':'S'}
    request.session['PROJECT']=PRJ_KEY
    context['FLG']=G.isNext(request.session['PROJECT'],request.session['MONTH'])
    upd='C'
    if request.POST.get('WDD', None) == 'WDD':
        DevHrs=request.POST.get('Dev_Hours', None)
        C=request.POST.get('No_Of_Critical_Defects', None)
        H=request.POST.get('No_Of_High_Defects', None)
        M=request.POST.get('No_Of_Medium_Defects', None)
        L=request.POST.get('No_Of_Low_Defects', None)
        if(C.isnumeric() and H.isnumeric() and M.isnumeric() and L.isnumeric() and G.is_number(DevHrs)):
                DevHrs=float(request.POST.get('Dev_Hours', None))
                C=int(request.POST.get('No_Of_Critical_Defects', None))
                H=int(request.POST.get('No_Of_High_Defects', None))
                M=int(request.POST.get('No_Of_Medium_Defects', None))
                L=int(request.POST.get('No_Of_Low_Defects', None))
                upd=G.saveWDD(request,DevHrs,C,H,M,L,request.session['PROJECT'],request.session['MONTH'])
        else:
                print("Validation failed")
                upd='V' # VALIDATION FAILED
        if(upd=='E'):
            messages.error(request, "Planned Effort Can't be Zero")
        elif(upd=='C'):
            messages.success(request, "WDD ADDED FOR PROJECT"+request.session['PROJECT']+ "Month:"+request.session['MONTH'])
        elif(upd=='V'):
            messages.error(request, "DevHrs only Accept Decimal and Other Fields Only Accept Numeric")
        elif(upd=='B'):
            messages.error(request, "Data point is outlier(beyond benchmarck), Put Remarks!!")
        elif(upd=='-'):
                messages.error(request, "None of number should be -Ve")
        else:
            messages.success(request, "WDD UPDATED FOR PROJECT"+request.session['PROJECT']+ "Month:"+request.session['MONTH'])
    return render(request, 'accounts/WDD.html',context)
                
def EV(request,PRJ_KEY):
        context={'FLG':'S'}
        request.session['PROJECT']=PRJ_KEY
        if request.POST.get('EV', None) == 'EV':
                upd=G.saveEV(request)
                if((upd=='U') or (upd=='C')):
                    context['FLG']='N'
                G.GEN_MSG(upd,request,'OTD','Planned Effort','Actual Effort')
        return render(request, 'accounts/EV.html',context)

def QRE(request,PRJ_KEY):
        context={'FLG':'S'}
        request.session['PROJECT']=PRJ_KEY
        if request.POST.get('QRE', None) == 'QRE':
                upd=G.saveQRE(request)
                if((upd=='U') or (upd=='C')):
                    context['FLG']='N'
                G.GEN_MSG(upd,request,'QRE','QA Defects','After QA Defects') 
        return render(request, 'accounts/QRE.html',context)
     
def OTD(request,PRJ_KEY):
        context={'FLG':'S'}
        request.session['PROJECT']=PRJ_KEY
        if request.POST.get('OTD', None) == 'OTD':
                upd=G.saveOTD(request)
                if((upd=='U') or (upd=='C')):
                    context['FLG']='N'
                G.GEN_MSG(upd,request,'OTD','Total Delivery','Total Delivery On Time')
        return render(request, 'accounts/OTD.html',context)

def AUTE(request,PRJ_KEY):
        context={'FLG':'S'} 
        request.session['PROJECT']=PRJ_KEY
        if request.POST.get('AUTE', None) == 'AUTE':
                upd=G.saveAUTE(request,PRJ_KEY)
                if((upd=='U') or (upd=='C')):
                    context['FLG']='N'
                G.GEN_MSG(upd,request,'AUTE','Unit_Testing_Coverage','Percentage_Of_Unit_Cases_Passed')
        return render(request, 'accounts/AUTE.html',context)

def home_pm(request,EMP_ID):
        MAT_LIST={}
        MAT_LIST_I=[]
        MAT_LIST_T=[]
        PRJ_LIST = []
        PRJ_LIST_T=[]
        PEND_LIST=[]
        if( 'IN_PROGRESS' not in  request.session):
                print('Home_PM-IF')
                Month_T=MetricsMonth.objects.filter(Status='A').values_list('Month')
                for type in Month_T:
                        for value in type:
                                Month=value

                PRJ_LIST_T=ProjectOwner.objects.filter(Project_PM_EmpId=EMP_ID).values_list('Project_Key')
                msgPend=""
                for type in PRJ_LIST_T:
                        for value in type:
                                PRJ_LIST.append(value)
                                PRJ_Key=value
                                MAT_LIST_I=[]
                                PEND_LIST=[]
                                MAT_LIST_T=AppMetrics.objects.filter(Project_Key=PRJ_Key).values_list('Metrics')
                                for type in MAT_LIST_T:
                                        for value in type:
                                                MAT_LIST_I.append(value)
                                                PRJ=G.getPRJ(value,PRJ_Key,Month)
                                                if PRJ is None:
                                                       PEND_LIST.append(value) 
                                MAT_LIST[PRJ_Key]=MAT_LIST_I
                                if PEND_LIST:
                                        PendStr=","
                                        PendStr=PendStr.join(PEND_LIST)
                                        X=PRJ_Key.split("_")
                                        msgPend=msgPend+"Metrics-"+PendStr+" did not fill for project:"+X[2]+"\n"
                if len(msgPend) >0:
                        messages.error(request, msgPend)
                else:
                        messages.success(request, "All Project's-All metrics have been filled")
                request.session['MAT_LIST'] = MAT_LIST
                request.session['MONTH'] = Month
        
def GenerateReport(request):
        YR=[]
        FR=[]
        TO=[]
        print("--GenerateReport-------")
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
        

        print(request.POST.get('REP', None))
        if request.POST.get('REP', None) == 'REP':
                Flg,Opt1,Opt2=PPT_REP.valReport(request,YR,FR,TO)
                print("-Option-")
                print(Flg)
                print(Opt1)
                print(Opt2)
                PPT_Name,PPT_TITLE,VALID_MONTH=PPT_REP.getPPTInfo(Flg,Opt1,Opt2)
                SUCC=['1','2','3']
                if Flg in SUCC:
                    MN=G.getOpenMonth()
                    ret=PPT_REP.ProduceRep(MN,Flg,Opt1,Opt2,VALID_MONTH,PPT_Name,PPT_TITLE)
                    if ret==-1:
                        messages.error(request, "InValid Metrics")
                        return render(request, 'swMetrics/GenReport.html', {})
                G.dispReportMsg(Flg,PPT_Name,request)
                
        context={'YR':YR, 'FR':FR,'TO':TO}
        return render(request, 'accounts/GenerateReport.html', context)

def home_pmo(request):
        request.session['PROJECT_COUNT']=G.PrjCount()
        request.session['METRICS_COUNT']=G.MetCount()
        request.session['USER_COUNT']=G.UsrCount()
        request.session['MONTH']=G.getOpenMonth()
        return render(request, 'swMetrics/home_pmo.html',{})


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
        return render_to_response('accounts/contact.html', context)

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

        Client_I=str(request.POST.get('Client', None))
        print('Client_I'+Client_I)
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
                CLIENT_CHOICES,MASTER_PRJ_CHOICES,PRJ_CHOICES=G.resetDropDownKeepSelected(CLIENT_CHOICES,Client_I,MASTER_PRJ_CHOICES,MASTER_PRJ_I,PRJ_CHOICES,PRJ_I)
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
        return render(request, 'accounts/AssignMetrics.html', context)

def AssignRole(request):
        msg = None
        success = False
        form=None
        USER_CHOICES_T=UsrLgn.objects.filter(UsrLgn_Role='B').values_list('UsrLgn_EmpId')
        USER_CHOICES = []
        for type in USER_CHOICES_T:
                for value in type:
                        USER_CHOICES.append(value)
        if request.method == "POST":
                USER_I=str(request.POST.get('USER', None))
                USR=int(USER_I)
                print("After"+USER_I)
                if(USER_I!='None'):
                        for cl in USER_CHOICES:
                                if(cl!=USR):
                                        print("remove"+str(USER_I))
                                        USER_CHOICES.remove(cl)
                print(request.POST.get('Assign', None))
                if request.POST.get('Assign', None) == 'Assign':
                        print('user clicked summary')
                        USER=UsrLgn.objects.get(UsrLgn_EmpId=USR)
                        USER.UsrLgn_Role='P'
                        USER.save()
                        messages.success(request, "User " + str(USER_I) + " can fill data for Metrics ")
   
        context={
                'USER_CHOICES':USER_CHOICES,
                "form": form,
                "msg": msg,
                "success": success
                }
        return render(request, 'accounts/AssignRole.html', context)


def AssignMetricsOwner(request):
        msg = None
        success = False
        form=None
        PRJ_CHOICES_T=Project.objects.values_list('Project_Key')
        PRJ_CHOICES = []
        USER_CHOICES=[]
        TEMP=[]
        for type in PRJ_CHOICES_T:
                for value in type:
                        PRJ_CHOICES.append(value)
        USER_CHOICES_T=UsrLgn.objects.filter(UsrLgn_Role='P').values_list('UsrLgn_EmpId')
        USER_CHOICES = []
        for type in USER_CHOICES_T:
                for value in type:
                        USER_CHOICES.append(value)
        print(USER_CHOICES)
        if request.method == "POST":
                Project_I=str(request.POST.get('Project', None))
                print('Project_I'+Project_I)
                print(PRJ_CHOICES)
                if(Project_I!=None):
                        PRJ_CHOICES=[Project_I]
                print("------------After----------")
                print(PRJ_CHOICES)


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
                                messages.error(request, "User Id not Given")
                        else:
                                ret=G.saveProjectOwner(Project_I,int(USER_I))
                                if(ret==1):
                                        messages.success(request, "Project " + Project_I + " Has been assigned to "+str(USER_I))
                                else:
                                        messages.info(request, "Project is already assigned")
   
        context={
                'PRJ_CHOICES':PRJ_CHOICES,
                'USER_CHOICES':USER_CHOICES,
                "form": form,
                "msg": msg,
                "success": success
                }
        return render(request, 'accounts/AssignMetricsOwner.html', context)

def FreezeMonth(request):
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
                        messages.error(request, "No Month is open FOR METRICS GENERATION")
                else:
                        MetMnth.Status='I'
                        MetMnth.save()
                        messages.success(request, "MONTH  "+MONTH_I+" CLOSED FOR METRICS GENERATION")
        context={
                'MONTH_CHOICES':MONTH_CHOICES,
                }
        return render(request, 'accounts/FreezeMonth.html', context) 

def InitiateMonth(request):
        MONTH_CHOICES_T=MetricsMonth.objects.all().values_list('Month').order_by('-Month')
        MONTH_CHOICES = []
        ACT_MONTH=""
        print("Triggerting Initiate")
        MONTH_I=str(request.POST.get('MONTH', 'None'))
        for type in MONTH_CHOICES_T:
                for value in type:
                        print("adding:"+value+":")
                        MONTH_CHOICES.append(value)
        if request.method == "POST":
                
                ACT_MONTH=MONTH_I
                if(MONTH_I!='None'):
                        for type in MONTH_CHOICES_T:
                                for value in type:
                                        if(value!=ACT_MONTH):
                                                MONTH_CHOICES.remove(value)
        MONTH = time.strftime("%Y-%m")
        MET_LIST_T=Metrics.objects.all().values_list('Metrics')
        MET_LIST = []
        BENCHMARK_LIST = {}
        BENCHMARK_LIST_T={}
        FLG=''
        request.session['FLG']=None
        
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
                    messages.error(request, "MONTH  "+MetMonthOld.Month+" IS ALREADY Active, Pls Close it")
                else:
                    messages.info(request, "MONTH  "+ACT_MONTH+" IS ALREADY ADDED FOR METRICS GENERATION")
   

                        
        if request.POST.get('ADD', None) == 'ADD':
                print("------------Month in add "+MONTH)
                BENCHMARK_LIST_T=MetricsBenchMark.objects.filter(Month=MONTH)
                
                FLG,ActMonth=G.saveMonth(MONTH)
                request.session['FLG']=FLG
                if FLG=='C':
                        messages.success(request, "MONTH  "+MONTH+" ADDED FOR METRICS GENERATION")
                elif FLG =='I':
                        messages.info(request, "MONTH  "+MONTH+" IS ALREADY ADDED & INACTIVE-BENCH MARK CAN'T BE UPDATED")
                elif FLG =='S':
                        messages.error(request, "MONTH  "+ActMonth+" IS ALREADY Active, Pls Close it")
                else:
                        messages.info(request, "MONTH  "+MONTH+" IS ALREADY ADDED FOR METRICS GENERATION")
        else:
                BENCHMARK_LIST_T=MetricsBenchMark.objects.filter(Month=MONTH_I)

        for BnMrk in BENCHMARK_LIST_T:
                BENCHMARK_LIST[BnMrk.Metrics]=BnMrk.BenchMark
        #Reset to 0
        if not BENCHMARK_LIST:
                for key in MET_LIST:
                        BENCHMARK_LIST[key]=0
        print(BENCHMARK_LIST)
        if request.POST.get('BNHMRK', None) == 'BNHMRK':

                for key in MET_LIST:
                        MON_BEN=request.POST.get(key, None)
                        if(request.session['FLG']=='C'):
                                ret=G.saveBenchMark(MONTH,key,float(MON_BEN))
                        else:
                                ret=G.saveBenchMark(ACT_MONTH,key,float(MON_BEN))
                if((request.session['FLG']=='A') or  (request.session['FLG']=='B')):
                     messages.success(request, "BENCH MARK UPDATED FOR THE "+ACT_MONTH)
                elif(ret=='C'):
                        messages.success(request, "BENCH MARK SET FOR THE "+MONTH)
                elif(ret=='I'):
                        messages.error(request, "MONTH "+MONTH +" IS INACTIVE-BENCH MARK CAN'T BE UPDATED")
                else:
                        messages.success(request, "BENCH MARK UPDATED FOR THE "+MONTH)
                request.session['FLG']=None
        
        print("---------------")
        print( request.POST.get('SET-BNHMRK', None))
        if request.POST.get('SET-BNHMRK', None) == 'SET-BNHMRK':
                OpenMnth=G.getOpenMonth()
                print("Inside set benchmark OpenMnth:"+OpenMnth+" MONTH:"+MONTH_I)
                if(OpenMnth==MONTH_I):
                        request.session['FLG']='B'
                else:
                        messages.error(request, "MONTH "+MONTH_I +" IS NOT OPEN MONTH-BENCH MARK CAN'T BE UPDATED")

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

        return render(request, 'accounts/InitiateMonth.html', context)    




def login_view(request):
    form = LoginForm(request.POST or None)
    msg = None
    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                try:
                        USER=UsrLgn.objects.get(UsrLgnName=username)
                except UsrLgn.DoesNotExist:
                        USER=None
                if USER is None:
                        messages.error(request, username+ " is invalid User")
                else:
                        request.session['EmpId']=USER.UsrLgn_EmpId
                        if(USER.UsrLgn_Role=='B'):
                                messages.info(request, "Request PMO for metrics generation role")
                        else:
                                if(USER.UsrLgn_Role=='O'):
                                        request.session['Role'] = "PMO"
                                if(USER.UsrLgn_Role=='P'):
                                        request.session['Role'] = "PM"
                                        home_pm(request,USER.UsrLgn_EmpId)
                                return redirect("/")
            else:
                messages.error(request,'Invalid credentials')
        else:
            messages.error(request,'Error validating the form')

    return render(request, "accounts/login.html", {"form": form, "msg": msg})


def register_view(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            Email = form.cleaned_data.get("email")
            EmpId = form.cleaned_data.get("EmpId")
            print(EmpId)
            
            user = authenticate(username=username, password=raw_password)
            print(user)

            msg = 'User created - please <a href="/login">login</a>.'
            success = True
            USR_Obj=UsrLgn(UsrLgnName=username,UsrLgn_Email=Email,UsrLgn_EmpId=EmpId)
            USR_Obj.save(force_insert=True)

            # return redirect("/login/")

        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})

def index(request):
    request.session['PROJECT_COUNT']=G.PrjCount()
    request.session['METRICS_COUNT']=G.MetCount()
    request.session['USER_COUNT']=G.UsrCount()
    request.session['MONTH']=G.getOpenMonth()
    msg = None
    success = False
    form=None
    return render(request, "accounts/index.html", {"form": form, "msg": msg, "success": success})




def logout(request):
    msg = None
    success = False
    form=None
    return render(request, "accounts/logout.html", {"form": form, "msg": msg, "success": success})


def home(request):
    return render(request, "accounts/home.html", {})



def ContactUs(request):
    return render(request, "accounts/ContactUs.html", {})

