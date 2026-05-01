from multiprocessing import context

from django.shortcuts import render, redirect, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models.functions import TruncMonth
from django.contrib import messages
from django.http import HttpResponse
from django.db import models
from django.db.models import Avg, Sum, F, Count, Q
from .models import *
from .forms import *
import json, time
# PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import os
import base64
from io import BytesIO
# Create your views here.

User = get_user_model()

# Đăng ký font Unicode cho tiếng Việt
def get_pdf_font_name():
    font_paths = [
        os.path.join(os.path.dirname(__file__), 'fonts', 'DejaVuSans.ttf'),
        os.path.join('C:\\Windows\\Fonts', 'arial.ttf'),
        os.path.join('C:\\Windows\\Fonts', 'times.ttf'),
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
        '/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf',
    ]

    for path in font_paths:
        if path and os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont('PDFUnicode', path))
                return 'PDFUnicode'
            except Exception:
                continue

    return 'Helvetica'

#trang chủ
def home(request):
    diaDiem = DiaDiem.objects.all()
    context={ 'diaDiem': diaDiem}
    return render(request,'app/home.html',context)

#giỏ hàng
@login_required
def cart(request):
    datCho_list = DatCho.objects.filter(ma_nguoi_dung=request.user).order_by('-ngay_dat')
    return render(request,'app/cart.html', {'datCho_list': datCho_list})

#thanh toán
@login_required
def booking(request):
    initial = {}
    dia_diem_id = request.GET.get('dia_diem_id')
    tour_id = request.GET.get('tour_id')

    if tour_id and tour_id.isdigit():
        tour = TourDuLich.objects.filter(ma_tour=tour_id).first()
        if tour:
            initial['ma_tour'] = tour
    elif dia_diem_id and dia_diem_id.isdigit():
        tour = TourDuLich.objects.filter(ma_dia_diem__ma_dia_diem=dia_diem_id).first()
        if tour:
            initial['ma_tour'] = tour

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            datCho = form.save(commit=False)
            datCho.ma_nguoi_dung = request.user
            tour = datCho.ma_tour

            if tour.so_luong_con_trong <= 0:
                form.add_error(None, 'Xin lỗi, tour này đã hết chỗ. Vui lòng chọn tour khác.')
            else:
                datCho.trang_thai = 'confirmed'
                datCho.save()
                messages.success(request, f'Đặt chỗ thành công. Mã đặt chỗ của bạn là {datCho.ma_dat_cho}.')
                return redirect('gioHang')
    else:
        form = BookingForm(initial=initial)

    return render(request, 'app/booking.html', {'form': form})


#giới thiệu
def introduce(request):
    return render(request, 'app/introduce.html')

#chính sách web
def policy(request):
    return render(request, 'app/policy.html')

#liên hệ
def contact(request):
    return render(request, 'app/contact.html')

#đặt dịch vụ
def service(request):
    danhMuc = DanhMuc.objects.all()
    diaDiem = DiaDiem.objects.all()
    # lọc theo danh mục
    danh_muc_id = request.GET.get('danhMuc')
    if danh_muc_id:
        diaDiem = diaDiem.filter(ma_danh_muc_id=danh_muc_id)
    # tìm kiếm
    q = request.GET.get('q')
    if q:
        diaDiem = diaDiem.filter(ten_dia_diem__icontains=q)
    # sắp xếp
    sap_xep = request.GET.get('sapXep')
    if sap_xep == 'moi':
        diaDiem = diaDiem.order_by('-ngay_tao')
    elif sap_xep == 'cu':
        diaDiem = diaDiem.order_by('ngay_tao')

    return render(request, 'app/service.html', {
        'danhMuc': danhMuc,
        'diaDiem': diaDiem
    })

#chi tiết điểm
def detail(request, id):
    diem = get_object_or_404(DiaDiem, pk=id)
    danhGiaList = diem.danh_gia.all()

    form = DanhGiaForm()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')

        form = DanhGiaForm(request.POST)
        if form.is_valid():
            # Chặn đánh giá trùng
            daDanhGia = DanhGia.objects.filter(
                ma_nguoi_dung=request.user,
                ma_dia_diem=diem
            ).exists()

            if not daDanhGia:
                danhGia = form.save(commit=False)
                danhGia.ma_nguoi_dung = request.user
                danhGia.ma_dia_diem = diem
                danhGia.save()

            return redirect('chiTietDiem', id=id)

    return render(request, 'app/detail.html', {
        'diem': diem,
        'danhGiaList': danhGiaList,
        'form': form
    })

# Tìm kiếm
def search(request):
    query = request.GET.get('q', '')
    diaDiem_results = []
    tourDuLich_results = []

    if query:
        # Tìm kiếm trong DiaDiem
        diaDiem_results = DiaDiem.objects.filter(
            models.Q(ten_dia_diem__icontains=query)
        )

        # Tìm kiếm trong TourDuLich
        tourDuLich_results = TourDuLich.objects.filter(
            models.Q(ten_tour__icontains=query)
        )

    context = {
        'query': query,
        'diaDiem_results': diaDiem_results,
        'tourDuLich_results': tourDuLich_results,
    }
    return render(request, 'app/search.html', context)


#trang cá nhân
@login_required
def trangCaNhan(request):
    user = request.user
    dat_cho_list = DatCho.objects.filter(ma_nguoi_dung=user).order_by('-ngay_dat')
    danhGia_list = DanhGia.objects.filter(ma_nguoi_dung=user).order_by('-ngay_danh_gia')
    
    report_permission_requests = RequestReportPermission.objects.filter(
        ma_nguoi_dung=user
    ).order_by('-ngay_tao')
    has_pending_report_permission_request = report_permission_requests.filter(trang_thai='pending').exists()
    has_report_permission = request.user.has_perm('app.view_report')

    pending_request_count = None
    if user.is_staff:
        pending_request_count = (
            RequestDiaDiem.objects.filter(trang_thai='pending').count() +
            RequestReportPermission.objects.filter(trang_thai='pending').count()
        )

    context = {
        'user': user,
        'dat_cho_list': dat_cho_list,
        'danhGia_list': danhGia_list,
        'user_report_permission_requests': report_permission_requests,
        'has_pending_report_permission_request': has_pending_report_permission_request,
        'has_report_permission': has_report_permission,
        'can_request_report_permission': not user.is_staff and not has_report_permission and not has_pending_report_permission_request,
        'pending_request_count': pending_request_count,
    }

    if user.is_staff:
        # Admin sees all permission requests in addition to user requests
        context['report_permission_requests'] = RequestReportPermission.objects.all().order_by('-ngay_tao')

    return render(request, 'app/trangCaNhan.html', context)


# ======================
# AUTH
# ======================
#đăng nhập
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        # Kiểm tra email không được trống
        if not email:
            return render(request, 'app/login.html', {
                'mode': 'login',
                'error': 'Vui lòng nhập email'
            })

        # Kiểm tra mật khẩu không được trống
        if not password:
            return render(request, 'app/login.html', {
                'mode': 'login',
                'error': 'Vui lòng nhập mật khẩu'
            })

        user = authenticate(
            request,
            username=email,
            password=password
        )

        if user:
            auth_login(request, user)
            return redirect('home')
        else:
            return render(request, 'app/login.html', {
                'mode': 'login',
                'error': 'Email hoặc mật khẩu không chính xác'
            })

    return render(request, 'app/login.html', {
        'mode': 'login'
    })

#đăng ký
def register_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        confirm = request.POST.get('confirmPassword', '')

        # Kiểm tra tên không được trống
        if not name:
            return render(request, 'app/login.html', {
                'mode': 'register',
                'error': 'Vui lòng nhập họ và tên'
            })

        # Kiểm tra email không được trống
        if not email:
            return render(request, 'app/login.html', {
                'mode': 'register',
                'error': 'Vui lòng nhập email'
            })

        # Kiểm tra mật khẩu không được trống
        if not password:
            return render(request, 'app/login.html', {
                'mode': 'register',
                'error': 'Vui lòng nhập mật khẩu'
            })

        # Kiểm tra mật khẩu khớp
        if password != confirm:
            return render(request, 'app/login.html', {
                'mode': 'register',
                'error': 'Mật khẩu không khớp'
            })

        # Kiểm tra độ dài mật khẩu
        if len(password) < 6:
            return render(request, 'app/login.html', {
                'mode': 'register',
                'error': 'Mật khẩu phải có ít nhất 6 ký tự'
            })

        # Kiểm tra email đã tồn tại
        if User.objects.filter(email=email).exists():
            return render(request, 'app/login.html', {
                'mode': 'register',
                'error': 'Email này đã được đăng ký'
            })

        if User.objects.filter(username=email).exists():
            return render(request, 'app/login.html', {
                'mode': 'register',
                'error': 'Email này đã tồn tại trong hệ thống'
            })

        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name
            )
            auth_login(request, user)
            return redirect('home')
        except Exception as e:
            return render(request, 'app/login.html', {
                'mode': 'register',
                'error': 'Đã xảy ra lỗi khi đăng ký. Vui lòng thử lại.'
            })

    return render(request, 'app/login.html', {
        'mode': 'register'
    })

# BÁO CÁO THỐNG KÊ
@login_required
def report(request):
    try:
        # ===== 1. CHECK QUYỀN =====
        user_is_admin = request.user.is_staff
        user_can_view_report = request.user.has_perm('app.view_report')
        user_is_creator = DiaDiem.objects.filter(ma_nguoi_dung=request.user).exists()

        if not user_is_admin and not user_can_view_report and not user_is_creator:
            # Kiểm tra nếu đã có yêu cầu pending
            has_pending_request = RequestReportPermission.objects.filter(
                ma_nguoi_dung=request.user,
                trang_thai='pending'
            ).exists()
            return render(request, 'app/report.html', {
                'error': 'Bạn không có quyền truy cập',
                'can_request_permission': True,
                'has_pending_request': has_pending_request
            })

        # ===== 2. FILTER =====
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        diem_id = request.GET.get('diem')
        so_sao = request.GET.get('so_sao')

        # 🔥 FIX QUAN TRỌNG
        export = request.GET.get('export') or request.POST.get('export')

        if user_is_admin or user_can_view_report:
            dia_diem_qs = DiaDiem.objects.all()
            tour_qs = TourDuLich.objects.all()
            dat_cho_qs = DatCho.objects.all()
            danh_gia_qs = DanhGia.objects.all()
        else:
            dia_diem_qs = DiaDiem.objects.filter(ma_nguoi_dung=request.user)
            tour_qs = TourDuLich.objects.filter(ma_dia_diem__in=dia_diem_qs).distinct()
            dat_cho_qs = DatCho.objects.filter(
                ma_tour__ma_dia_diem__ma_nguoi_dung=request.user
            )
            danh_gia_qs = DanhGia.objects.filter(
                ma_dia_diem__ma_nguoi_dung=request.user
            )

        # Áp dụng bộ lọc theo thứ tự
        filtered_dia_diem_ids = set()

        if start_date and end_date:
            temp_dat_cho_qs = dat_cho_qs.filter(
                ngay_dat__date__range=[start_date, end_date]
            )
            filtered_dia_diem_ids.update(temp_dat_cho_qs.values_list('ma_tour__ma_dia_diem', flat=True).distinct())
            dat_cho_qs = temp_dat_cho_qs

        if diem_id:
            filtered_dia_diem_ids.add(int(diem_id))
            dat_cho_qs = dat_cho_qs.filter(
                ma_tour__ma_dia_diem__ma_dia_diem=diem_id
            )
            danh_gia_qs = danh_gia_qs.filter(
                ma_dia_diem__ma_dia_diem=diem_id
            )

        if so_sao:
            temp_danh_gia_qs = danh_gia_qs.filter(so_sao=so_sao)
            rating_dia_diem_ids = set(temp_danh_gia_qs.values_list('ma_dia_diem', flat=True).distinct())
            if filtered_dia_diem_ids:
                filtered_dia_diem_ids = filtered_dia_diem_ids.intersection(rating_dia_diem_ids)
            else:
                filtered_dia_diem_ids = rating_dia_diem_ids
            danh_gia_qs = temp_danh_gia_qs

        # Áp dụng bộ lọc địa điểm
        if filtered_dia_diem_ids:
            dia_diem_qs = dia_diem_qs.filter(ma_dia_diem__in=filtered_dia_diem_ids)
            dat_cho_qs = dat_cho_qs.filter(
                ma_tour__ma_dia_diem__in=dia_diem_qs
            )
            danh_gia_qs = danh_gia_qs.filter(
                ma_dia_diem__in=dia_diem_qs
            )


        # ===== 3. THỐNG KÊ =====
        total_diem = dia_diem_qs.count()
        total_tour = TourDuLich.objects.filter(ma_dia_diem__in=dia_diem_qs).distinct().count()
        total_dat_cho = dat_cho_qs.count()
        total_danh_gia = danh_gia_qs.count()

        dat_cho_by_month = dat_cho_qs.annotate(
            month=TruncMonth('ngay_dat')
        ).values('month').annotate(
            count=Count('ma_dat_cho')
        ).order_by('month')

        dat_cho_by_diem = dat_cho_qs.values(
            'ma_tour__ten_tour',
            'ma_tour__ma_dia_diem__ten_dia_diem'
        ).annotate(
            count=Count('ma_dat_cho')
        ).order_by('-count')

        top_diem_dat = dat_cho_qs.values(
            'ma_tour__ma_dia_diem__ten_dia_diem'
        ).annotate(
            count=Count('ma_dat_cho')
        ).order_by('-count')[:10]

        revenue_by_diem = dat_cho_qs.values(
            'ma_tour__ma_dia_diem__ten_dia_diem'
        ).annotate(
            revenue=Sum('ma_tour__gia')
        ).order_by('-revenue')

        danh_gia_by_rating = danh_gia_qs.values('so_sao').annotate(
            count=Count('so_sao')
        ).order_by('-so_sao')

        comments = danh_gia_qs.select_related('ma_nguoi_dung', 'ma_dia_diem').order_by('-ngay_danh_gia')[:50]

        # ===== 4. EXPORT PDF =====
        if export == 'pdf':

            chart_month = request.POST.get('chart_month')
            chart_revenue = request.POST.get('chart_revenue')

            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="report.pdf"'

            doc = SimpleDocTemplate(response, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()
            font_name = get_pdf_font_name()

            for style_name in ['Title', 'Heading1', 'Heading2', 'Heading3', 'Normal']:
                if style_name in styles:
                    styles[style_name].fontName = font_name

            # TITLE
            elements.append(Paragraph("BÁO CÁO THỐNG KÊ DU LỊCH", styles['Title']))
            elements.append(Spacer(1, 20))

            # ===== BẢNG =====
            summary_data = [
                ['Chỉ số', 'Giá trị'],
                ['Tổng địa điểm', total_diem],
                ['Tổng tour', total_tour],
                ['Tổng đặt', total_dat_cho],
                ['Tổng đánh giá', total_danh_gia],
            ]

            table = Table(summary_data)
            table.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('FONTNAME', (0,0), (-1,-1), font_name),
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ]))

            elements.append(Paragraph("1. Tổng quan", styles['Heading2']))
            elements.append(table)
            elements.append(Spacer(1, 20))

            # ===== BẢNG THEO ĐỊA ĐIỂM =====
            elements.append(Paragraph("2. Thống kê theo địa điểm & tour", styles['Heading2']))
            table_data = [['Địa điểm', 'Tour', 'Số lượt đặt']]
            for item in dat_cho_by_diem:
                table_data.append([
                    item['ma_tour__ma_dia_diem__ten_dia_diem'],
                    item['ma_tour__ten_tour'],
                    item['count']
                ])
            table2 = Table(table_data)
            table2.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('FONTNAME', (0,0), (-1,-1), font_name),
            ]))
            elements.append(table2)
            elements.append(Spacer(1, 20))

            # ===== TOP 10 =====
            elements.append(Paragraph("3. Top 10 địa điểm được đặt nhiều", styles['Heading2']))
            top_data = [['Địa điểm', 'Lượt đặt']]
            for item in top_diem_dat:
                top_data.append([
                    item['ma_tour__ma_dia_diem__ten_dia_diem'],
                    item['count']
                ])
            table3 = Table(top_data)
            table3.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('FONTNAME', (0,0), (-1,-1), font_name),
            ]))
            elements.append(table3)
            elements.append(Spacer(1, 20))

            # ===== DOANH THU =====
            elements.append(Paragraph("4. Doanh thu theo địa điểm", styles['Heading2']))
            revenue_data = [['Địa điểm', 'Doanh thu']]
            for item in revenue_by_diem:
                revenue_data.append([
                    item['ma_tour__ma_dia_diem__ten_dia_diem'],
                    f"{item['revenue'] or 0:,} VND"
                ])
            table4 = Table(revenue_data)
            table4.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('FONTNAME', (0,0), (-1,-1), font_name),
            ]))
            elements.append(table4)
            elements.append(Spacer(1, 20))

            # ===== BIỂU ĐỒ THÁNG =====
            if chart_month:
                img_data = base64.b64decode(chart_month.split(',')[1])
                elements.append(Paragraph("5. Biểu đồ đặt chỗ theo tháng", styles['Heading2']))
                elements.append(Image(BytesIO(img_data), width=400, height=200))
                elements.append(Spacer(1, 20))

            # ===== BIỂU ĐỒ DOANH THU =====
            if chart_revenue:
                img_data = base64.b64decode(chart_revenue.split(',')[1])
                elements.append(Paragraph("6. Biểu đồ doanh thu", styles['Heading2']))
                elements.append(Image(BytesIO(img_data), width=400, height=200))
                elements.append(Spacer(1, 20))

            doc.build(elements)
            return response

        # ===== 5. HTML =====
        context = {
            'total_diem': total_diem,
            'total_tour': total_tour,
            'total_dat_cho': total_dat_cho,
            'total_danh_gia': total_danh_gia,

            'dat_cho_by_month': json.dumps(list(dat_cho_by_month), default=str),
            'dat_cho_by_diem': dat_cho_by_diem,
            'top_diem_dat': top_diem_dat,
            'revenue_by_diem': revenue_by_diem,
            'danh_gia_by_rating': danh_gia_by_rating,
            'comments': comments,

            'revenue_chart': json.dumps(list(revenue_by_diem), default=str),
            'rating_chart': json.dumps(list(danh_gia_by_rating), default=str),

            'ds_diem': dia_diem_qs,
        }

        return render(request, 'app/report.html', context)

    except Exception as e:
        return render(request, 'app/report.html', {
            'error': str(e)
        })

# YÊU CẦU CẤP QUYỀN XEM BÁO CÁO
@login_required
def request_report_permission(request):
    if request.method == 'POST':
        # Kiểm tra nếu đã có yêu cầu pending
        existing_request = RequestReportPermission.objects.filter(
            ma_nguoi_dung=request.user,
            trang_thai='pending'
        ).exists()

        if existing_request:
            messages.warning(request, 'Bạn đã có yêu cầu cấp quyền đang chờ xử lý.')
        else:
            RequestReportPermission.objects.create(ma_nguoi_dung=request.user)
            messages.success(request, 'Yêu cầu cấp quyền đã được gửi tới admin.')

    return redirect('baoCao')

# Tạo địa điểm mới với upload ảnh (admin tạo trực tiếp, user tạo request)
@login_required
def create_dia_diem(request):
    if request.user.is_staff:
        # Admin tạo trực tiếp
        if request.method == 'POST':
            form = DiaDiemForm(request.POST, request.FILES)
            if form.is_valid():
                dia_diem = form.save(commit=False)
                dia_diem.ma_nguoi_dung = request.user
                dia_diem.save()
                return redirect('home')
        else:
            form = DiaDiemForm()
    else:
        # User tạo request
        if request.method == 'POST':
            form = RequestDiaDiemForm(request.POST, request.FILES)
            if form.is_valid():
                request_dia_diem = form.save(commit=False)
                request_dia_diem.ma_nguoi_dung = request.user
                request_dia_diem.save()
                return redirect('trangCaNhan')
        else:
            form = RequestDiaDiemForm()
    return render(request, 'app/create_dia_diem.html', {'form': form})
    
# Chỉnh sửa địa điểm với upload ảnh
@login_required
def edit_dia_diem(request, id):
    dia_diem = get_object_or_404(DiaDiem, pk=id)
    if request.method == 'POST':
        form = DiaDiemForm(request.POST, request.FILES, instance=dia_diem)
        if form.is_valid():
            form.save()
            return redirect('chiTietDiem', id=id)
    else:
        form = DiaDiemForm(instance=dia_diem)
    return render(request, 'app/edit_dia_diem.html', {'form': form, 'dia_diem': dia_diem})

# Admin xem danh sách tất cả yêu cầu
@login_required
def manage_requests(request):
    if not request.user.is_staff:
        return redirect('home')

    create_requests = RequestDiaDiem.objects.all().order_by('-ngay_tao')
    permission_requests = RequestReportPermission.objects.all().order_by('-ngay_tao')
    requests = []

    for req in create_requests:
        requests.append({
            'obj': req,
            'type': 'create',
            'label': 'Tạo địa điểm',
        })

    for req in permission_requests:
        requests.append({
            'obj': req,
            'type': 'permission',
            'label': 'Cấp quyền báo cáo',
        })

    requests.sort(key=lambda item: item['obj'].ngay_tao, reverse=True)
    pending_request_count = (
        RequestDiaDiem.objects.filter(trang_thai='pending').count() +
        RequestReportPermission.objects.filter(trang_thai='pending').count()
    )

    return render(request, 'app/manage_requests.html', {
        'requests': requests,
        'pending_request_count': pending_request_count,
    })

# Admin approve hoặc reject request tạo địa điểm
@login_required
def approve_request(request, id):
    if not request.user.is_staff:
        return redirect('home')
    req = get_object_or_404(RequestDiaDiem, pk=id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            dia_diem = DiaDiem.objects.create(
                ten_dia_diem=req.ten_dia_diem,
                mo_ta=req.mo_ta,
                dia_chi=req.dia_chi,
                ma_danh_muc=req.ma_danh_muc,
                anh_dai_dien=req.anh_dai_dien,
                ma_nguoi_dung=req.ma_nguoi_dung
            )
            req.trang_thai = 'approved'
            req.save()
        elif action == 'reject':
            req.trang_thai = 'rejected'
            req.ly_do_tu_choi = request.POST.get('ly_do', '')
            req.save()
        return redirect('manage_requests')
    return render(request, 'app/approve_request.html', {'req': req})

# Admin approve hoặc reject request cấp quyền báo cáo
@login_required
def approve_report_permission_request(request, id):
    if not request.user.is_staff:
        return redirect('home')
    req = get_object_or_404(RequestReportPermission, pk=id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            # Cấp quyền bằng cách thêm permission
            from django.contrib.auth.models import Permission
            perm = Permission.objects.get(codename='view_report')
            req.ma_nguoi_dung.user_permissions.add(perm)
            req.trang_thai = 'approved'
            req.save()
            messages.success(request, f'Đã cấp quyền xem báo cáo cho {req.ma_nguoi_dung.username}.')
        elif action == 'reject':
            req.trang_thai = 'rejected'
            req.ly_do_tu_choi = request.POST.get('ly_do', '')
            req.save()
            messages.info(request, f'Đã từ chối yêu cầu cấp quyền của {req.ma_nguoi_dung.username}.')
        return redirect('trangCaNhan')
    return render(request, 'app/approve_report_permission_request.html', {'req': req})

@login_required
def revoke_report_permission(request, id):
    if not request.user.is_staff:
        return redirect('home')
    req = get_object_or_404(RequestReportPermission, pk=id)
    if req.trang_thai == 'approved':
        from django.contrib.auth.models import Permission
        perm = Permission.objects.get(codename='view_report')
        req.ma_nguoi_dung.user_permissions.remove(perm)
        req.trang_thai = 'revoked'
        req.save()
        messages.success(request, f'Quyền xem báo cáo của {req.ma_nguoi_dung.username} đã được thu hồi.')
    else:
        messages.warning(request, 'Chỉ có thể thu hồi quyền từ yêu cầu đã được cấp.')
    return redirect('manage_requests')


