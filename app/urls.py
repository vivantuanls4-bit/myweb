from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
urlpatterns = [
    path('', views.home,name='home'),
    path('cart/', views.cart, name='gioHang'),
    path('booking/', views.booking, name='thanhToan'),
    path('introduce/', views.introduce, name='gioiThieu'),
    path('policy/', views.policy, name='chinhSach'),
    path('contact/', views.contact, name='lienHe'),
    path('service/', views.service, name='datDichVu'),
    path('detail/<int:id>/', views.detail, name='chiTietDiem'),
    path('search/', views.search, name='timKiem'),
    path('trangCaNhan/', views.trangCaNhan, name='trangCaNhan'),
    path('report/', views.report, name='baoCao'),
    path('request_report_permission/', views.request_report_permission, name='request_report_permission'),

    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

    path('create_dia_diem/', views.create_dia_diem, name='create_dia_diem'),
    path('edit_dia_diem/<int:id>/', views.edit_dia_diem, name='edit_dia_diem'),
    path('manage_requests/', views.manage_requests, name='manage_requests'),
    path('approve_request/<int:id>/', views.approve_request, name='approve_request'),
    path('approve_report_permission_request/<int:id>/', views.approve_report_permission_request, name='approve_report_permission_request'),
    path('revoke_report_permission/<int:id>/', views.revoke_report_permission, name='revoke_report_permission'),
]
