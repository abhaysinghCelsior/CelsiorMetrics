import datetime
from django.db import models
from django.utils import timezone
USER="SW-METRICS"

class TmpPswd(models.Model):
    Pswd = models.CharField(max_length=128,default='Celsior')

class UsrLgn(models.Model):
    UsrLgn_EmpId = models.IntegerField(default=0)
    UsrLgnName = models.CharField(max_length=20, primary_key=True,default='Celsior')
    UsrLgnPswd = models.CharField(max_length=128,default='Celsior')
    UsrLgn_Lst_Pswd =  models.CharField(max_length=128,default='Celsior')
    UsrLgn_Email = models.EmailField(max_length=32,default='Celsior.com')
    UsrLgn_Role = models.CharField(max_length=1,default='B')
    Created_by= models.CharField(max_length=24,default=USER)
    Created_Date= models.DateField(default=datetime.date.today)

class Role(models.Model):
    Role = models.CharField(max_length=1,default='B', primary_key=True)
    Role_Details = models.CharField(max_length=10) #B - Basic P- PM O-PMO D-DeliveryHead
    Created_by= models.CharField(max_length=24,default=USER,null=True)
    Created_Date= models.DateField(default=datetime.date.today,null=True)

class ProjectOwner(models.Model):
    Project_Key = models.CharField(max_length=72, primary_key=True)
    Project_PM_EmpId = models.IntegerField(default=0)
    Created_by= models.CharField(max_length=24,default=USER,null=True)
    Created_Date= models.DateField(default=datetime.date.today,null=True)


class Client(models.Model):
    Client = models.CharField(max_length=24, primary_key=True)
    Client_Details = models.CharField(max_length=64)
    Created_by= models.CharField(max_length=24,default=USER,null=True)
    Created_Date =models.DateField(default=datetime.date.today,null=True)
    def __str__(self):
        return self.Client


class MasterProject(models.Model):
    Client = models.CharField(max_length=24)
    MasterProject = models.CharField(max_length=24, primary_key=True)
    MasterProject_Details = models.CharField(max_length=64)
    Created_by= models.CharField(max_length=24,default=USER,null=True)
    Created_Date= models.DateField(default=datetime.date.today,null=True)


class Project(models.Model):
    class Meta:
        unique_together = (('Project_Client', 'Project_MasterProject','Project','Project_Key'),)
    Project_Client = models.CharField(max_length=24)
    Project_MasterProject = models.CharField(max_length=24)
    Project = models.CharField(max_length=24)
    Project_Key = models.CharField(max_length=72)
    Project_Details = models.CharField(max_length=72)
    Created_by= models.CharField(max_length=24,default=USER,null=True)
    Created_Date= models.DateField(default=datetime.date.today,null=True)


class Subordinates(models.Model):
    PM_EmpId = models.IntegerField(default=0, primary_key=True)
    Sub_EmpId = models.IntegerField(default=0)
    Created_by= models.CharField(max_length=24)
    Created_Date= models.DateField()

class AppMetrics(models.Model):
    class Meta:
        unique_together = (('Project_Key', 'Metrics'),)
    Project_Key = models.CharField(max_length=72)
    Metrics =  models.CharField(max_length=4)
    Created_by= models.CharField(max_length=24,default=USER,null=True)
    Created_Date= models.DateField(default=datetime.date.today,null=True)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key in kwargs:
            setattr(self, key, kwargs[key])


class Metrics(models.Model):
    Metrics = models.CharField(max_length=4, primary_key=True)
    Metrics_Details = models.CharField(max_length=64) 
    Created_by= models.CharField(max_length=24,default=USER,null=True)
    Created_Date =models.DateField(default=datetime.date.today,null=True)


class MetricsMonth(models.Model):
    Month = models.CharField(max_length=24, primary_key=True)
    Status = models.CharField(max_length=1) 
    Created_by= models.CharField(max_length=24,default=USER,null=True)
    Created_Date= models.DateField(default=datetime.date.today,null=True)


class MetricsMonthStatus(models.Model):
    Status = models.CharField(max_length=1, primary_key=True)
    Details = models.CharField(max_length=16) # I-INACTIVE A-ACTIVE G-METRICS GENERATED
    Created_by= models.CharField(max_length=24,default=USER,null=True)
    Created_Date= models.DateField(default=datetime.date.today,null=True)


class MetricsBenchMark(models.Model):
    class Meta:
        unique_together = (('Metrics', 'Month'),)
    Metrics = models.CharField(max_length=24)
    Month = models.CharField(max_length=24)
    BenchMark = models.FloatField()
    Created_by= models.CharField(max_length=24,default=USER,null=True)
    Created_Date =models.DateField(default=datetime.date.today,null=True)

    
class WeightedDefectDensity(models.Model):
    class Meta:
        unique_together = (('Project_Key', 'Month_of_Metrics'),)
    Project_Key = models.CharField(max_length=72)
    Month_of_Metrics = models.CharField(max_length=20)
    Dev_Hours = models.FloatField()
    No_Of_Critical_Defects = models.IntegerField(default=0)
    No_Of_High_Defects  = models.IntegerField(default=0)
    No_Of_Medium_Defects  = models.IntegerField(default=0)
    No_Of_Low_Defects  = models.IntegerField(default=0)
    WDD = models.FloatField()
    Remarks = models.CharField(max_length=128)
    Created_by= models.CharField(max_length=24,default=USER,null=True)
    Created_Date= models.DateField(default=datetime.date.today,null=True)

class DefectSummary(models.Model):
    class Meta:
        unique_together = (('Project_Key', 'Month_of_Metrics','DefectId'),)
    Project_Key = models.CharField(max_length=72)
    Month_of_Metrics = models.CharField(max_length=20)
    DefectId = models.CharField(max_length=32)
    Severity = models.CharField(max_length=32)
    DefectSource = models.CharField(max_length=32)
    RC = models.CharField(max_length=32)
    Created_by= models.CharField(max_length=24,default=USER,null=True)
    Created_Date= models.DateField(default=datetime.date.today,null=True)


class QARemovalEfficiency(models.Model):
    class Meta:
        unique_together = (('Project_Key', 'Month_of_Metrics'),)
    Project_Key = models.CharField(max_length=72)
    Month_of_Metrics = models.CharField(max_length=20)
    QA_Defects = models.IntegerField(default=0)
    After_QA_Defects  = models.IntegerField(default=0)
    DRE = models.FloatField()
    Remarks = models.CharField(max_length=128)
    Created_by= models.CharField(max_length=24,default=USER,null=True)
    Created_Date =models.DateField(default=datetime.date.today,null=True)



class OnTimeDelivery(models.Model):
    class Meta:
        unique_together = (('Project_Key', 'Month_of_Metrics'),)
    Project_Key = models.CharField(max_length=72)
    Month_of_Metrics = models.CharField(max_length=20)
    Total_Delivery = models.IntegerField(default=0)
    Total_Delivery_OnTime  = models.IntegerField(default=0)
    OTD = models.FloatField()
    Remarks = models.CharField(max_length=128)
    Created_by= models.CharField(max_length=24,default=USER,null=True)
    Created_Date =models.DateField(default=datetime.date.today,null=True)

class WeightedCodeReviewEffectiveness(models.Model):
    class Meta:
        unique_together = (('Project_Key', 'Month_of_Metrics'),)
    Project_Key = models.CharField(max_length=72)
    Month_of_Metrics = models.CharField(max_length=20)
    Static_CR = models.CharField(max_length=1)
    Peer_CR = models.CharField(max_length=1)
    Arch_CR = models.CharField(max_length=1)
    No_Of_Object = models.IntegerField(default=0)
    No_Of_Object_StaticReview  = models.IntegerField(default=0)
    No_Of_Object_PeerReviewed  = models.IntegerField(default=0)
    No_Of_Object_ArchReviewed  = models.IntegerField(default=0)
    No_Of_ReviewComments  = models.IntegerField(default=0)
    No_Of_ReviewComments_Incorporated  = models.IntegerField(default=0)
    WCRE = models.FloatField()
    Remarks = models.CharField(max_length=128)
    Created_by= models.CharField(max_length=24,default=USER,null=True)
    Created_Date= models.DateField(default=datetime.date.today,null=True)



class AutomatedUnitTestingEffectiveness(models.Model):
    class Meta:
        unique_together = (('Project_Key', 'Month_of_Metrics'),)
    Project_Key = models.CharField(max_length=72)
    Month_of_Metrics = models.CharField(max_length=20)
    Unit_Testing_Coverage = models.FloatField()
    Percentage_Of_Unit_Cases_Passed = models.FloatField()
    AUTE = models.FloatField()
    Remarks = models.CharField(max_length=128)
    Created_by= models.CharField(max_length=24,default=USER,null=True)
    Created_Date =models.DateField(default=datetime.date.today,null=True)


class EffortVariance(models.Model):
    class Meta:
        unique_together = (('Project_Key', 'Month_of_Metrics'),)
    Project_Key = models.CharField(max_length=72)
    Month_of_Metrics = models.CharField(max_length=20)
    Planned_Effort = models.FloatField()
    Actual_Effort = models.FloatField()
    EV = models.FloatField()
    Remarks = models.CharField(max_length=128)
    Created_by= models.CharField(max_length=24,default=USER,null=True)
    Created_Date =models.DateField(default=datetime.date.today,null=True)

class DefectSource(models.Model):
    DefectSource = models.CharField(max_length=72)

class RC(models.Model):
    RC = models.CharField(max_length=72)



    
