from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models

# BẢNG NGƯỜI_DÙNG
class NguoiDung(AbstractUser):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username
# BẢNG DANH MỤC
class DanhMuc(models.Model):
    ma_danh_muc = models.AutoField(primary_key=True)
    ten_danh_muc = models.CharField(max_length=100, unique=True)
    mo_ta = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Danh mục"
        verbose_name_plural = "Danh mục"

    def __str__(self):
        return self.ten_danh_muc


# BẢNG ĐỊA ĐIỂM
class DiaDiem(models.Model):
    ma_dia_diem = models.AutoField(primary_key=True)
    ten_dia_diem = models.CharField(max_length=200)
    mo_ta = models.TextField()
    dia_chi = models.CharField(max_length=255)
    ma_danh_muc = models.ForeignKey(DanhMuc, on_delete=models.SET_NULL, related_name='dia_diem_list', null=True, blank=True)
    anh_dai_dien = models.ImageField(upload_to='dia_diem/', null=True, blank=True)
    ma_nguoi_dung = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='dia_diem_created')
    ngay_tao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Địa điểm"
        verbose_name_plural = "Địa điểm"
        permissions = [
            ('view_report', 'Can access report page'),
        ]

    def __str__(self):
        return self.ten_dia_diem

    @property
    def anh_dai_dien_url(self):
        if self.anh_dai_dien and hasattr(self.anh_dai_dien, 'url'):
            return self.anh_dai_dien.url
        return ''


#BẢNG TOUR DU LỊCH
class TourDuLich(models.Model):
    ma_tour = models.AutoField(primary_key=True)
    ten_tour = models.CharField(max_length=200)
    thoi_gian = models.IntegerField(help_text="Số ngày")
    gia = models.DecimalField(max_digits=10, decimal_places=2)
    so_luong_cho = models.PositiveIntegerField(default=10, help_text="Số lượng chỗ tối đa")
    ma_dia_diem = models.ManyToManyField(DiaDiem, related_name='tour_list') # lỗi

    class Meta:
        verbose_name = "Tour du lịch"
        verbose_name_plural = "Tour du lịch"

    def __str__(self):
        return self.ten_tour

    @property
    def so_luong_da_dat(self):
        return self.dat_cho_list.exclude(trang_thai='cancelled').count()

    @property
    def so_luong_con_trong(self):
        return max(0, self.so_luong_cho - self.so_luong_da_dat)

# BẢNG YÊU CẦU TẠO ĐỊA ĐIỂM
class RequestDiaDiem(models.Model):
    ma_request = models.AutoField(primary_key=True)
    ma_nguoi_dung = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='request_list')
    ten_dia_diem = models.CharField(max_length=200)
    mo_ta = models.TextField()
    dia_chi = models.CharField(max_length=255)
    ma_danh_muc = models.ForeignKey(DanhMuc, on_delete=models.SET_NULL, null=True, blank=True)
    anh_dai_dien = models.ImageField(upload_to='request_dia_diem/', null=True, blank=True)
    ngay_tao = models.DateTimeField(auto_now_add=True)
    trang_thai = models.CharField(max_length=20, choices=[
        ('pending', 'Đang chờ'),
        ('approved', 'Đã chấp nhận'),
        ('rejected', 'Đã từ chối'),
    ], default='pending')
    ly_do_tu_choi = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Yêu cầu tạo địa điểm"
        verbose_name_plural = "Yêu cầu tạo địa điểm"

    def __str__(self):
        return f"Yêu cầu {self.ten_dia_diem} - {self.ma_nguoi_dung.username}"
    
#BẢNG ĐẶT_CHỖ (thiếu)
class DatCho(models.Model):
    ma_dat_cho = models.AutoField(primary_key=True)
    ma_nguoi_dung = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='dat_cho_list')
    ma_tour = models.ForeignKey(TourDuLich, on_delete=models.CASCADE, related_name='dat_cho_list')
    ngay_dat = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField()
    end_date = models.DateField() # xóa
    trang_thai = models.CharField(max_length=20, choices=[
        ('pending', 'Đang chờ'),
        ('confirmed', 'Đã xác nhận'),
        ('cancelled', 'Đã hủy'),
    ], default='pending')
    # ghi chú
    def __str__(self):
        return f"Đặt chỗ {self.ma_dat_cho} - {self.ma_nguoi_dung}"

#BẢNG ĐÁNH_GIÁ
class DanhGia(models.Model):
    sao = [(i, f"{i} sao") for i in range(1, 6)]
    ma_danh_gia = models.AutoField(primary_key=True)
    ma_nguoi_dung = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='danh_gia')
    ma_dia_diem = models.ForeignKey(DiaDiem, on_delete=models.CASCADE, related_name='danh_gia')

    so_sao = models.IntegerField(choices=sao)
    noi_dung_binh_luan = models.TextField()

    ngay_danh_gia = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('ma_nguoi_dung', 'ma_dia_diem')  # Mỗi người dùng chỉ được đánh giá một lần cho mỗi địa điểm
        ordering = ['-ngay_danh_gia']  # Sắp xếp theo ngày đánh giá mới nhất

# BẢNG YÊU CẦU CẤP QUYỀN XEM BÁO CÁO
class RequestReportPermission(models.Model):
    ma_request = models.AutoField(primary_key=True)
    ma_nguoi_dung = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='report_permission_requests')
    ngay_tao = models.DateTimeField(auto_now_add=True)
    trang_thai = models.CharField(max_length=20, choices=[
        ('pending', 'Đang chờ'),
        ('approved', 'Đã chấp nhận'),
        ('rejected', 'Đã từ chối'),
    ], default='pending')
    ly_do_tu_choi = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Yêu cầu cấp quyền báo cáo"
        verbose_name_plural = "Yêu cầu cấp quyền báo cáo"

    def __str__(self):
        return f"Yêu cầu cấp quyền báo cáo - {self.ma_nguoi_dung.username}"
    