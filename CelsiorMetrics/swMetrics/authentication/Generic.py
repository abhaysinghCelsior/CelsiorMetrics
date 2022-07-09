from cryptography.fernet import Fernet
from base64 import b64encode, b64decode
from .models import UsrLgn,Role,ProjectOwner,Client,MasterProject,Project,Subordinates,AppMetrics,Metrics,MetricsMonth,MetricsMonthStatus
from .models import MetricsBenchMark,WeightedDefectDensity,QARemovalEfficiency,OnTimeDelivery,WeightedCodeReviewEffectiveness
from .models import AutomatedUnitTestingEffectiveness,EffortVariance,TmpPswd,DefectSource,RC,DefectSummary
from django.core.exceptions import ValidationError
from django.contrib import messages
from swMetrics.home.configMet import REP_PATH
OBJ={'WDD':WeightedDefectDensity,'OTD':OnTimeDelivery,'QRE':QARemovalEfficiency,'AUTE':AutomatedUnitTestingEffectiveness,'WCRE':WeightedCodeReviewEffectiveness,'EV':EffortVariance}

def ValidateWCRE(request):
    REV_OPT=['Y','N','y','n']
    S=request.POST.get('Static_CR', None)
    P=request.POST.get('Peer_CR', None)
    A=request.POST.get('Arch_CR', None)
    NoObjs=request.POST.get('No_Of_Object', None)
    ObjStRev=request.POST.get('No_Of_Object_StaticReview', None)
    ObjPrRev=request.POST.get('No_Of_Object_PeerReviewed', None)
    ObjArRev=request.POST.get('No_Of_Object_ArchReviewed', None)
    TotCom=request.POST.get('No_Of_ReviewComments', None)
    TotComIn=request.POST.get('No_Of_ReviewComments_Incorporated', None)


    if ((S not in REV_OPT) or (P not in REV_OPT) or (A not in REV_OPT)):
         return 'W' # option wrong
    if((S =='') or (A =='') or (P =='') or (NoObjs =='') or (ObjStRev =='') or (ObjPrRev =='') or (ObjArRev=='') or (TotCom =='') or (TotComIn =='')):
        return 'N' #Field are Mandatory
    if ((not NoObjs.isnumeric()) and (not ObjStRev.isnumeric()) and (not ObjPrRev.isnumeric()) and (not ObjArRev.isnumeric()) and (not TotCom.isnumeric()) and (not TotComIn.isnumeric())):
        return 'V' # VALIDATION FAILED
    NoObjs=int(request.POST.get('No_Of_Object', None))
    ObjStRev=int(request.POST.get('No_Of_Object_StaticReview', None))
    ObjPrRev=int(request.POST.get('No_Of_Object_PeerReviewed', None))
    ObjArRev=int(request.POST.get('No_Of_Object_ArchReviewed', None))
    TotCom=int(request.POST.get('No_Of_ReviewComments', None))
    TotComIn=int(request.POST.get('No_Of_ReviewComments_Incorporated', None))
    if ((NoObjs<0) or (ObjStRev<0) or (ObjPrRev<0) or (ObjArRev<0) or (TotCom<0) or (TotComIn<0)):
        return '-' # -Ve number
    if((ObjStRev>NoObjs) or (ObjPrRev>NoObjs) or (ObjArRev >NoObjs) or (TotComIn >TotCom)):
        return 'E' # Can't Exceed
    if((NoObjs==0) or ((S.upper()=='Y') and (ObjStRev==0))or ((A.upper()=='Y') and (ObjArRev==0))or ((P.upper()=='Y') and (ObjPrRev==0))):
        return 'Z' # Zero comments
    return 'S' # Successful

def clearRequest(request):
        if( 'IN_PROGRESS' in  request.session):
                del request.session['IN_PROGRESS']
        
        if('MAT_LIST' in request.session):
                MET_ALREADY_GEN=request.session['MAT_LIST']
                for mat in MET_ALREADY_GEN:
                        del mat
        if('MAT_LIST-COMP' in request.session):
                MAT_LIST=request.session['MAT_LIST-COMP']
                for mat in MAT_LIST:
                        del mat

def saveWCRE(request):
    try:
        ret = ValidateWCRE(request)
        print(ret)
        SUCS=['S']
        if ret not in SUCS :
            return ret
        S=request.POST.get('Static_CR', None)
        P=request.POST.get('Peer_CR', None)
        A=request.POST.get('Arch_CR', None)
        NoObjs=int(request.POST.get('No_Of_Object', None))
        ObjStRev=int(request.POST.get('No_Of_Object_StaticReview', None))
        ObjPrRev=int(request.POST.get('No_Of_Object_PeerReviewed', None))
        ObjArRev=int(request.POST.get('No_Of_Object_ArchReviewed', None))
        TotCom=int(request.POST.get('No_Of_ReviewComments', None))
        TotComIn=int(request.POST.get('No_Of_ReviewComments_Incorporated', None))
        MON=request.session['MONTH']
        PRJ_KEY=request.session['PROJECT']
        WCRE_Obj_old=WeightedCodeReviewEffectiveness.objects.get(Project_Key=PRJ_KEY,Month_of_Metrics=MON)

    except WeightedCodeReviewEffectiveness.DoesNotExist:
        WCRE_Obj_old=None
    WCRE_I=0
    NoOfReview=0
    if(S.upper()=='Y'):
        NoOfReview=NoOfReview+1
        WCRE_I=WCRE_I+(ObjStRev/NoObjs)
    if(P.upper()=='Y'):
        NoOfReview=NoOfReview+1
        WCRE_I=WCRE_I+(ObjPrRev/NoObjs)
    if(A.upper()=='Y'):
        NoOfReview=NoOfReview+1
        WCRE_I=WCRE_I+(ObjArRev/NoObjs)
    WCRE_I=WCRE_I*5/NoOfReview
    if(TotCom>0):
        WCRE_I=WCRE_I*(TotComIn/TotCom)
    print(WCRE_I)
    BnMrk_DP= MetricsBenchMark.objects.get(Metrics='WCRE',Month=request.session['MONTH'])
    Remarks=request.POST.get('Remarks', None)
    if((WCRE_I<BnMrk_DP.BenchMark) and ((Remarks is None) or (len(Remarks.strip())==0))):
        return 'B'
            
    if WCRE_Obj_old is None:
        WCRE_Obj=WeightedCodeReviewEffectiveness(Project_Key=PRJ_KEY,Month_of_Metrics=MON,Static_CR = S, Peer_CR = P, Arch_CR = A, No_Of_Object = NoObjs, No_Of_Object_StaticReview  = ObjStRev,No_Of_Object_PeerReviewed=ObjPrRev,    No_Of_Object_ArchReviewed  = ObjArRev, No_Of_ReviewComments  = TotCom, No_Of_ReviewComments_Incorporated  = TotComIn)
        WCRE_Obj.WCRE=WCRE_I
        WCRE_Obj.Remarks=Remarks
        
        WCRE_Obj.save(force_insert=True)
        print("WCRE - CREATE")
        return 'C'
    else:
        WCRE_Obj_old.Static_CR = S
        WCRE_Obj_old.Peer_CR = P
        WCRE_Obj_old.Arch_CR = A
        WCRE_Obj_old.No_Of_Object = NoObjs
        WCRE_Obj_old.No_Of_Object_StaticReview  = ObjStRev
        WCRE_Obj_old.No_Of_Object_PeerReviewed=ObjPrRev
        WCRE_Obj_old.No_Of_Object_ArchReviewed  = ObjArRev
        WCRE_Obj_old.No_Of_ReviewComments  = TotCom
        WCRE_Obj_old.No_Of_ReviewComments_Incorporated  = TotComIn
        WCRE_Obj_old.WCRE=WCRE_I
        WCRE_Obj_old.Remarks=Remarks
        WCRE_Obj_old.save()
        print("WCRE - update")
        return 'U'

def saveWDD(request,DevHrs,C,H,M,L,PRJ_KEY,MON):
    if(DevHrs==0):
        return 'E'
    Remarks=request.POST.get('Remarks', None)
    try:
        WDD_Obj_old=WeightedDefectDensity.objects.get(Project_Key=PRJ_KEY,Month_of_Metrics=MON)
    except WeightedDefectDensity.DoesNotExist:
        WDD_Obj_old=None
    WDD_I=(5*C+3*H+M+L*0.5)/DevHrs
    
    BnMrk_DP= MetricsBenchMark.objects.get(Metrics='WDD',Month=request.session['MONTH'])

    if( (DevHrs<0) or (C<0) or (H<0) or (M<0) or (L<0)):
            return "-" #-Ve

    if((WDD_I>BnMrk_DP.BenchMark) and ((Remarks is None) or (len(Remarks.strip())==0))):
        return 'B'
    if WDD_Obj_old is None:
        WDD_Obj=WeightedDefectDensity(Project_Key=PRJ_KEY,Month_of_Metrics=MON,Dev_Hours = DevHrs, No_Of_Critical_Defects =C,No_Of_High_Defects= H,No_Of_Medium_Defects = M,No_Of_Low_Defects= L)
        WDD_Obj.WDD=WDD_I
        WDD_Obj.Remarks=Remarks
        WDD_Obj.save(force_insert=True)
        return 'C'
    else:
        WDD_Obj_old.Dev_Hours = DevHrs
        WDD_Obj_old.No_Of_Critical_Defects =C
        WDD_Obj_old.No_Of_High_Defects= H
        WDD_Obj_old.No_Of_Medium_Defects = M
        WDD_Obj_old.No_Of_Low_Defects= L
        WDD_Obj_old.WDD=WDD_I
        WDD_Obj_old.Remarks=Remarks
        WDD_Obj_old.save()
        return 'U'

def ValidateDefectSummaryInputs(DefectId, DefectSrc_I,RC_I,request):
        DefectId1=DefectId
        DefectId1.sort()
        last=""
        for valDefId in DefectId1:
                if((valDefId=='DefectId') or (len(valDefId.strip())==0)):
                        messages.error(request, "One of defect Number is not Given")
                        return "E"
                if(last==valDefId):
                        messages.error(request, "Defect Numbers should be Unique")
                        return "E"
                last=valDefId
        for valDefSrc in DefectSrc_I:
                if(valDefSrc=="None"):
                        messages.error(request, "Defect Source is not selected for one of the Defect")
                        return "E"
        for valRC in RC_I:
                if(valRC=="None"):
                        messages.error(request, "Route Cause is not selected for one of the Defect")
                        return "E"
        return "S"

def addOneRowDefSum(P_DefId,P_DefSrc,P_RC,P_Severity,PRJ_KEY,MON):
        DefSum= DefectSummary(Project_Key=PRJ_KEY,Month_of_Metrics=MON,DefectId=P_DefId,Severity=P_Severity,DefectSource=P_DefSrc,RC=P_RC)
        DefSum.save(force_insert=True)
        return 'C'

def addDefectSummary(DefectId, DefectSrc_I,RC_I,DEF_LIST,PRJ_KEY,MON):
        try:
                Flag="S"
                try:
                        DefSumOld= DefectSummary.objects.get(Project_Key=PRJ_KEY,Month_of_Metrics=MON)
                except DefectSummary.DoesNotExist:
                        DefSumOld=None
                if DefSumOld is not None:
                        DefectSummary.objects.filter(Project_Key=PRJ_KEY,Month_of_Metrics=MON).delete()
                for idx in range(len(DEF_LIST)):
                        addOneRowDefSum(DefectId[idx],DefectSrc_I[idx],RC_I[idx],DEF_LIST[idx],PRJ_KEY,MON)
        except:
                Flag="E"
        return Flag

def getRCandDS(withNone):
        DEFECTSOURCE_CHOICES = []
        RC_CHOICES = []
        if(withNone=='Y'):
                DEFECTSOURCE_CHOICES.append('None')
                RC_CHOICES.append('None')
        DEFECTSOURCE_CHOICES_T=DefectSource.objects.values_list('DefectSource')
        for type in DEFECTSOURCE_CHOICES_T:
                for value in type:
                        DEFECTSOURCE_CHOICES.append(value)
        RC_CHOICES_T=RC.objects.values_list('RC')
        for type in RC_CHOICES_T:
                for value in type:
                        RC_CHOICES.append(value)
        return RC_CHOICES,DEFECTSOURCE_CHOICES

def PrjCount():
        try:
                PrjCnt= Project.objects.count()
        except Project.DoesNotExist:
                PrjCnt=0
        print("Project Count:"+str(PrjCnt))
        return PrjCnt

def MetCount():
        try:
                MetCnt= Metrics.objects.count()
        except Metrics.DoesNotExist:
                MetCnt=0
        return MetCnt

def UsrCount():
        try:
                UsrCount= UsrLgn.objects.filter(UsrLgn_Role='P').count()
        except UsrLgn.DoesNotExist:
                UsrCount=0
        return UsrCount

def is_number(n):
    is_number = True
    try:
        num = float(n)
        # check for "nan" floats
        is_number = num == num   # or use `math.isnan(num)`
    except ValueError:
        is_number = False
    return is_number

def isNext(PRJ_KEY,MON):
        flg='N'
        try:
                WDD_L= WeightedDefectDensity.objects.get(Project_Key=PRJ_KEY,Month_of_Metrics=MON)
        except WeightedDefectDensity.DoesNotExist:
                WDD_L=None
        if WDD_L is None:
                flg='S'
        try:
                DefSum_L= DefectSummary.objects.filter(Project_Key=PRJ_KEY,Month_of_Metrics=MON).count()
        except DefectSummary.DoesNotExist:
                DefSum_L=None
        if DefSum_L is None:
                flg='S'
        if(flg=='N'):
                if(DefSum_L != (WDD_L.No_Of_Critical_Defects+WDD_L.No_Of_High_Defects  + WDD_L.No_Of_Medium_Defects+WDD_L.No_Of_Low_Defects)):
                        flg='S'
        return flg

def saveEV(request):
    Remarks=request.POST.get('Remarks', None)
    PlanEff=ActEff=EV_I=0
    
    try:
        ret=GEN_FieldValidation(request,'Planned_Effort','Actual_Effort','F','F')
        print(ret)
        SUCS=['S','E']
        if ret not in SUCS :
            return ret
        MON=request.session['MONTH']
        PRJ_KEY=request.session['PROJECT']
        PlanEff=float(request.POST.get('Planned_Effort', None))
        ActEff=float(request.POST.get('Actual_Effort', None))
        EV_Obj_old=EffortVariance.objects.get(Project_Key=PRJ_KEY,Month_of_Metrics=MON)
        EV_I=(ActEff-PlanEff)/PlanEff
        BnMrk_DP= MetricsBenchMark.objects.get(Metrics='EV',Month=request.session['MONTH'])
        print(EV_I)
        print(BnMrk_DP.BenchMark)
        print(Remarks)
        if((EV_I>BnMrk_DP.BenchMark) and ((Remarks is None) or (len(Remarks.strip())==0))):
                return 'B'
    except EffortVariance.DoesNotExist:
        EV_Obj_old=None
    if EV_Obj_old is None:
        EV_Obj=EffortVariance(Project_Key=PRJ_KEY,Month_of_Metrics=MON,Planned_Effort=PlanEff,Actual_Effort=ActEff,Remarks=Remarks)
        EV_Obj.EV=EV_I
        EV_Obj.save(force_insert=True)
        return 'C'
    else:
        EV_Obj_old.Planned_Effort=PlanEff
        EV_Obj_old.Actual_Effort=ActEff
        EV_Obj_old.EV=EV_I
        EV_Obj_old.Remarks=Remarks
        EV_Obj_old.save()
        return 'U'

def saveQRE(request):
        DRE=1
        Remarks=request.POST.get('Remarks', None)
        try:
                ret=GEN_FieldValidation(request,'QA_Defects','After_QA_Defects','N','N')
                print(ret)
                SUCS=['S','Z','E','F']
                if ret not in SUCS :
                        return ret
                MON=request.session['MONTH']
                PRJ_KEY=request.session['PROJECT']
                QA_Def=float(request.POST.get('QA_Defects', None))
                Af_QA_Def=float(request.POST.get('After_QA_Defects', None))
                QRE_Obj_old=QARemovalEfficiency.objects.get(Project_Key=PRJ_KEY,Month_of_Metrics=MON)
                if(ret=='F'):
                    DRE=1
                else:
                    DRE=QA_Def/(Af_QA_Def+QA_Def)
                
                BnMrk_DP= MetricsBenchMark.objects.get(Metrics='QRE',Month=request.session['MONTH'])
                print(DRE)
                print(BnMrk_DP.BenchMark)
                if((DRE<BnMrk_DP.BenchMark) and ((Remarks is None) or (len(Remarks.strip())==0))):
                        return 'B'
        except QARemovalEfficiency.DoesNotExist:
                QRE_Obj_old=None
        if QRE_Obj_old is None:
                QRE_Obj=QARemovalEfficiency(Project_Key=PRJ_KEY,Month_of_Metrics=MON,QA_Defects=QA_Def,After_QA_Defects=Af_QA_Def,Remarks=Remarks)
                QRE_Obj.DRE=DRE
                QRE_Obj.save(force_insert=True)
                return 'C'
        else:
                QRE_Obj_old.QA_Defects=QA_Def
                QRE_Obj_old.After_QA_Defects=Af_QA_Def
                QRE_Obj_old.DRE=DRE
                QRE_Obj_old.Remarks=Remarks
                QRE_Obj_old.save()
                return 'U'

def saveOTD(request):
        OTD=1
        Remarks=request.POST.get('Remarks', None)
        try:
                ret=GEN_FieldValidation(request,'Total_Delivery','Total_Delivery_OnTime','N','N')
                SUCS=['S','F']
                if ret not in SUCS :
                        return ret
                MON=request.session['MONTH']
                PRJ_KEY=request.session['PROJECT']
                TOT_Del=int(request.POST.get('Total_Delivery', None))
                TOT_Del_OnTime=int(request.POST.get('Total_Delivery_OnTime', None))
                OTD_Obj_old=OnTimeDelivery.objects.get(Project_Key=PRJ_KEY,Month_of_Metrics=MON)
                if(ret=='F'):
                        OTD=1
                else:
                        OTD=TOT_Del_OnTime/TOT_Del
                Remarks=request.POST.get('Remarks', None)
                BnMrk_DP= MetricsBenchMark.objects.get(Metrics='OTD',Month=request.session['MONTH'])
                
                if((OTD<BnMrk_DP.BenchMark) and ((Remarks is None) or (len(Remarks.strip())==0))):
                        return 'B'
        except OnTimeDelivery.DoesNotExist:
                print('Not Exist')
                OTD_Obj_old=None
        if OTD_Obj_old is None:
                print('Create OTD')
                OTD_Obj=OnTimeDelivery(Project_Key=PRJ_KEY,Month_of_Metrics=MON,Total_Delivery=TOT_Del,Total_Delivery_OnTime=TOT_Del_OnTime,Remarks=Remarks)
                OTD_Obj.OTD=OTD
                OTD_Obj.save(force_insert=True)
                return 'C'
        else:
                print('Update OTD')
                OTD_Obj_old.Total_Delivery=TOT_Del
                OTD_Obj_old.Total_Delivery_OnTime=TOT_Del_OnTime
                OTD_Obj_old.OTD=OTD
                OTD_Obj_old.Remarks=Remarks
                OTD_Obj_old.save()
                print(OTD_Obj_old)
                return 'U'

def GEN_FieldValidation(request,FIELD1_P,FIELD2_P,FIELD1_TYP,FIELD2_TYP):
        FIELD1=request.POST.get(FIELD1_P, '')
        FIELD2=request.POST.get(FIELD2_P, '')
        if((FIELD1 =='') or (FIELD2 =='')):
                return 'N' #Field are Mandatory
        if FIELD1_TYP=='N' and (not FIELD1.isnumeric()):
                return 'V' # VALIDATION FAILED
        if FIELD2_TYP=='N' and (not FIELD2.isnumeric()):
                return 'V' # VALIDATION FAILED

        if FIELD1_TYP=='F' and (not is_number(FIELD1)):
                return 'V' # VALIDATION FAILED
        if FIELD1_TYP=='F' and (not is_number(FIELD2)):
                return 'V' # VALIDATION FAILED
        if(FIELD1_TYP=='N'):
                FIELD1=int(request.POST.get(FIELD1_P, None))
        else:
                FIELD1=float(request.POST.get(FIELD1_P, None))
        if(FIELD2_TYP=='N'):
                FIELD2=int(request.POST.get(FIELD2_P, None))
        else:
                FIELD2=float(request.POST.get(FIELD2_P, None))
        if((FIELD1<0) or(FIELD2<0)):
                return "-"
                
        if(FIELD1==0):
                if(FIELD2==0):
                        return 'F' # FULL VALUE
                else:
                        return 'Z' #Can't Zero
        if(FIELD2>FIELD1):
                return 'E' # Can't Exceed
        return 'S' # Successful

def saveAUTE(request,PRJ_KEY):
        Remarks=request.POST.get('Remarks', None)
        try:
                ret=GEN_FieldValidation(request,'Unit_Testing_Coverage','Percentage_Of_Unit_Cases_Passed','F','F')
                SUCS=['S','F','Z','E']
                if ret not in SUCS :
                        return ret
                MON=request.session['MONTH']
        
                UT_Cov=float(request.POST.get('Unit_Testing_Coverage', None))
                UT_Per=float(request.POST.get('Percentage_Of_Unit_Cases_Passed', None))
                if((UT_Per>100) or (UT_Per<0) or (UT_Cov>100) or (UT_Cov<0)):
                        return 'O' #Outside of limit
                
                if(UT_Cov>1):
                        UT_Cov=UT_Cov/100
                if(UT_Per>1):
                        UT_Per=UT_Per/100

                AUTE=5*UT_Cov*UT_Per
                AUTE_Obj_Old=AutomatedUnitTestingEffectiveness.objects.get(Project_Key=PRJ_KEY,Month_of_Metrics=MON)
                BnMrk_DP= MetricsBenchMark.objects.get(Metrics='AUTE',Month=request.session['MONTH'])
                print(BnMrk_DP.BenchMark)
                print("----------aute-------"+str(AUTE))
                if((AUTE<BnMrk_DP.BenchMark) and ((Remarks is None) or (len(Remarks.strip())==0))):
                        return 'B'
        except AutomatedUnitTestingEffectiveness.DoesNotExist:
                AUTE_Obj_Old=None
        if AUTE_Obj_Old is None:
                print("----------AUTE Before insert------------:"+PRJ_KEY+":"+MON+":"+str(UT_Cov)+":"+str(UT_Per))
                AUTE_Obj=AutomatedUnitTestingEffectiveness(Project_Key=PRJ_KEY,Month_of_Metrics=MON,Unit_Testing_Coverage=UT_Cov,Percentage_Of_Unit_Cases_Passed=UT_Per,Remarks=Remarks)
                AUTE_Obj.AUTE=AUTE
                AUTE_Obj.save(force_insert=True)
                return 'C'
        else:
                AUTE_Obj_Old.Unit_Testing_Coverage=UT_Cov
                AUTE_Obj_Old.Percentage_Of_Unit_Cases_Passed=UT_Per
                AUTE_Obj_Old.AUTE=AUTE
                AUTE_Obj_Old.Remarks=Remarks
                
                AUTE_Obj_Old.save()
                return 'U'

def GEN_MSG(upd,request,MET,FIELD1,FIELD2):
        if(upd=='C'):
                messages.success(request, MET + " ADDED FOR PROJECT"+request.session['PROJECT']+ "Month:"+request.session['MONTH'])
        elif(upd=='V'):
                messages.error(request, "Both Fields Only Accept Numeric Value")
        elif(upd=='N'):
                messages.error(request, "Fields Should Not Be Null")
        elif(upd=='Z'):
                messages.error(request, FIELD1 + " are  Zero While " + FIELD2 +  "More Than 0")
        elif(upd=='F'):
                messages.error(request, FIELD1 + " and " + FIELD2 +  " both can't not be 0")
        elif(upd=='E'):
                messages.error(request, FIELD1 + " Can't Be More Than " + FIELD2)
        elif(upd=='B'):
                messages.error(request, "Data point is outlier(beyond benchmarck), Put Remarks!!")
        elif(upd=='-'):
                messages.error(request, "None of number should be -Ve")
        elif(upd=='O'):
                messages.error(request, "Only 0 to 100 Acceptable")
        else:
                messages.success(request,MET + " UPDATED FOR PROJECT"+request.session['PROJECT']+ "Month:"+request.session['MONTH'])
                
def dispReportMsg(ERR,PPT_Name,request):
        SUCC=['1','2','3']
        if ERR in SUCC:
                messages.success(request, REP_PATH.strip()+ PPT_Name + " has been generated")
        elif (ERR=='E1'):
                messages.error(request, "TO should be greater than FROM")
        elif (ERR=='E2'):
                messages.error(request, "TO is not Selected")
        elif (ERR=='E3'):
                messages.error(request, "From is not Selected")
        elif (ERR=='E4'):
                messages.error(request, "No option Selected")
        else:
                messages.error(request, "UnKnown Error")

def MonthNumToStr(MON):
        print("------MonthNumToStr-------")
        YR=int(MON/12)
        MN=MON % 12
        print(YR)
        print(MN)
        return str(YR)+"-"+str(MN)
                                     
def ifMonthInOptedPriod(MNTH,Flg,Opt1,Opt2,FIRST):
        if(Flg=="1"):
                print("inseide ifMonthInOptedPriod")
                print(FIRST)
                FIRST_Num=MonthStrToNum(FIRST)
                MNTH_Num=MonthStrToNum(MNTH)
                No_Of_Month=int(Opt1)
                print("MNTH_Num:"+str(MNTH_Num)+" FIRST_Num:"+str(FIRST_Num)+ " No_Of_Month:"+str(No_Of_Month))
                if((MNTH_Num<=FIRST_Num) and (MNTH_Num>FIRST_Num-No_Of_Month)):
                        return True
                else:
                        return False
        if(Flg=="2"):
                YR_MON=Opt1.split("-")
                OPT_YR=YR_MON[0]
                YR_MON=MNTH.split("-")
                MNTH_YR=YR_MON[0]
                if(OPT_YR==MNTH_YR):
                        return True
                else:
                        return False
        if(Flg=="3"):
                if((MNTH>=Opt1) and (MNTH<=Opt2)):
                        return True
                else:
                        return False
        return False

def saveAppMetrics(MAT_P,PRJ_KEY):
        print('PRJ_KEY:'+PRJ_KEY)
        print(MAT_P)
        AppMet=AppMetrics()
        AppMet.Project_Key=PRJ_KEY
        for obj in AppMetrics.objects.filter(Project_Key=PRJ_KEY):
                print(obj.Metrics)
                if obj.Metrics not in MAT_P:
                        print("Remove"+obj.Metrics)
                        obj.delete()
        for MAT_I in MAT_P:
                print("MAT_I:"+MAT_I)
                NoAdd=1
                for obj in  AppMetrics.objects.filter(Project_Key=PRJ_KEY,Metrics=MAT_I):
                        NoAdd=0
                if(NoAdd==1):
                        print("Add"+MAT_I)
                        AppMet=AppMetrics(Project_Key=PRJ_KEY,Metrics=MAT_I)
                        AppMet.save(force_insert=True)
        
def resetDropDownKeepSelected(CLIENT_CHOICES,Client_I,MASTER_PRJ_CHOICES,MASTER_PRJ_I,PRJ_CHOICES,PRJ_I):
        if(Client_I!='None'):
                print(Client_I)
                for cl in CLIENT_CHOICES:
                        if(cl!=Client_I):
                                CLIENT_CHOICES.remove(cl)
        if(MASTER_PRJ_I!='None'):
                print(MASTER_PRJ_I)
                for mprj in MASTER_PRJ_CHOICES:
                        if(mprj!=MASTER_PRJ_I):
                                MASTER_PRJ_CHOICES.remove(mprj)
        if(PRJ_I!='None'):
                print(PRJ_I)
                for prj in PRJ_CHOICES:
                        if(prj!=PRJ_I):
                                PRJ_CHOICES.remove(prj)
        return CLIENT_CHOICES,MASTER_PRJ_CHOICES,PRJ_CHOICES

def saveProjectOwner(PRJ_KEY,USER_P):
        PrjOwn=ProjectOwner()
        PrjOwn.Project_Key=PRJ_KEY
        for obj in ProjectOwner.objects.filter(Project_Key=PRJ_KEY):
                if obj.Project_PM_EmpId != USER_P:
                        print("Remove"+str(obj.Project_PM_EmpId))
                        obj.delete()
        
        NoAdd=1
        for obj in  ProjectOwner.objects.filter(Project_Key=PRJ_KEY,Project_PM_EmpId=USER_P):
                NoAdd=0
        if(NoAdd==1):
                print("Add"+str(USER_P))
                PrjOwn=ProjectOwner(Project_Key=PRJ_KEY,Project_PM_EmpId=USER_P)
                PrjOwn.save(force_insert=True)
                return 1
        else:
                return 0

def getOpenMonth():
        ActMon=None
        try:
                MetMonthOld=MetricsMonth.objects.filter(Status='A').values_list('Month')
                for type in MetMonthOld:
                        for value in type:
                                ActMon=value
        except MetricsMonth.DoesNotExist:
                MetMonthOld=None
        if MetMonthOld is None:
                return None
        else:
                return ActMon

def saveMonth(MONTH):
        for obj in  MetricsMonth.objects.filter(Month=MONTH):
                return obj.Status, " "
        ActMon=getOpenMonth()
        if (ActMon):
                if(ActMon!=MONTH):
                        print("MetMonthOld.Month:"+ActMon+" Month:"+MONTH)
                        return 'S',ActMon #Already one project is active

        print("Added")
        MetMonth=MetricsMonth(Month=MONTH,Status='A')
        MetMonth.save(force_insert=True)
        return 'C', " "

def saveBenchMark(MONTH,MET,BNCHMARK):
        try:
                MetBnhMrkOld=MetricsBenchMark.objects.get(Metrics=MET,Month=MONTH)
        except MetricsBenchMark.DoesNotExist:
                MetBnhMrkOld=None
        if MetBnhMrkOld==None:
                MetBnhMrk=MetricsBenchMark(Month=MONTH,Metrics=MET,BenchMark=BNCHMARK)
                MetBnhMrk.save(force_insert=True)
                return 'C'
        else:
                MetBnhMrkOld.BenchMark=BNCHMARK
                MetBnhMrkOld.save()
                return 'U'
            
def encrypt(mypwd):
    return mypwd

def decrypt(encMessage):
    return encMessage

def MonthStrToNum(MON):
        YR_MON=MON.split("-")
        return int(YR_MON[0])*12+int(YR_MON[1])

def getPRJ(Met,PRJ_KEY,Month):
        MetObj=OBJ[Met]
        try:
                MetIns=MetObj.objects.get(Project_Key=PRJ_KEY,Month_of_Metrics=Month)
        except MetObj.DoesNotExist:
                MetIns=None
        if (MetIns):
                return MetIns.Project_Key
        else:
                return None

def genListProjDidntAddedMetricsData():
        
        try:
                MetMonth=MetricsMonth.objects.filter(Status='A').values_list('Month')
                for type in MetMonth:
                        for value in type:
                                ActMon=value
        except MetricsMonth.DoesNotExist:
                MetMonth=None
        LstPrj=""
        if(MetMonth):
                Month=ActMon
                print("--------------genListProjDidntAddedMetricsData--------Month:"+Month)
                MISSED_PRJ=[]
                AppMetricsList=AppMetrics.objects.all().order_by('Project_Key')
                for AppObj in AppMetricsList:
                        PRJ_KEY=AppObj.Project_Key
                        PRJ=getPRJ(AppObj.Metrics,PRJ_KEY,Month)
                        print("Applicable Project:"+PRJ_KEY+": Metrics:"+AppObj.Metrics)
                        print(PRJ)
                        if PRJ is None:
                                if PRJ_KEY not in MISSED_PRJ:
                                        print("Added in MISSED")
                                        PrjOwn=ProjectOwner.objects.get(Project_Key=PRJ_KEY)
                                        Lgn=UsrLgn.objects.get(UsrLgn_EmpId=PrjOwn.Project_PM_EmpId)
                                        MISSED_PRJ.append(PRJ_KEY+":"+str(PrjOwn.Project_PM_EmpId)+":"+AppObj.Metrics+":"+Lgn.UsrLgn_Email)
                for PRJ_IDX in MISSED_PRJ:
                        LstPrj=LstPrj+"\n            "+PRJ_IDX
                        
                                        
        else:
                LstPrj=LstPrj+" No Month in Active"
        return LstPrj

