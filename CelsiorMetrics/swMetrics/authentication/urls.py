# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path
from .views import login_view, register_view, index,logout,AssignRole,AssignMetricsOwner,AssignMetrics
from .views import InitiateMonth,FreezeMonth,GenerateReport,AUTE,EV,OTD,WDD,QRE,WCRE,DefectSummaryData,home,ContactUs
from django.contrib.auth.views import LogoutView
app_name = 'swMetrics'

urlpatterns = [
    path('', index, name="index"),
    path('login/', login_view, name="login"),
    path('home/', home, name="home"),
    path('ContactUs/', ContactUs, name="ContactUs"),
    path('register/', register_view, name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("AssignRole/", AssignRole, name="AssignRole"),
    path("AssignMetricsOwner/", AssignMetricsOwner, name="AssignMetricsOwner"),
    path("AssignMetrics/",AssignMetrics, name="AssignMetrics"),
    path("InitiateMonth/",InitiateMonth, name="InitiateMonth"),
    path("FreezeMonth/",FreezeMonth, name="FreezeMonth"),
    path("GenerateReport/",GenerateReport, name="GenerateReport"),
    path('AUTE/<str:PRJ_KEY>',AUTE, name="AUTE"),
    path('EV/<str:PRJ_KEY>',EV, name="EV"),
    path('OTD/<str:PRJ_KEY>',OTD, name="OTD"),
    path('QRE/<str:PRJ_KEY>',QRE, name="QRE"),
    path('WCRE/<str:PRJ_KEY>',WCRE, name="WCRE"),
    path('WDD/<str:PRJ_KEY>',WDD, name="WDD"),
    path('DefectSummaryData/<str:PRJ_KEY>',DefectSummaryData, name="DefectSummaryData"),
]
