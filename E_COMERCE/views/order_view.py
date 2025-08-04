from django.views import View
from django.shortcuts import render,redirect
from django.contrib.auth.mixins import LoginRequiredMixin

class OrderListView(View):
    def get(self,request):
        return
    
    def post(self,request):
        return
    
    
class OrderCreateView(LoginRequiredMixin,View):
    login_url = 'log_in'
    def get(self,request):
        return render(request, 'enduser/order.html')
    
    def post(self,request):
        return
    
class OrderUpdateView(View):
    def get(self,request):
        return
    
    def post(self,request):
        return
    
    
class OrderDeleteView(View):
    def get(self,request):
        return
    
    def post(self,request):
        return
    
    
class OrderDetailsView(View):
    def get(self,request):
        return
    
    def post(self,request):
        return