from datetime import date
from django import forms
from .models import DanhGia, DatCho, DiaDiem, TourDuLich, DanhMuc, RequestDiaDiem

class DanhGiaForm(forms.ModelForm):
    class Meta:
        model = DanhGia
        fields = ['so_sao', 'noi_dung_binh_luan']
        widgets = {
            'so_sao': forms.RadioSelect,
            'noi_dung_binh_luan': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Chia sẻ cảm nhận của bạn...'
            })
        }

class BookingForm(forms.ModelForm):
    class Meta:
        model = DatCho
        fields = ['ma_tour', 'start_date', 'end_date']
        widgets = {
            'ma_tour': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if end_date < start_date:
                raise forms.ValidationError('Ngày về phải lớn hơn hoặc bằng ngày đi.')
            if start_date < date.today():
                raise forms.ValidationError('Ngày khởi hành phải là ngày hôm nay hoặc tương lai.')

        return cleaned_data

class DiaDiemForm(forms.ModelForm):
    class Meta:
        model = DiaDiem
        fields = ['ten_dia_diem', 'mo_ta', 'dia_chi', 'ma_danh_muc', 'anh_dai_dien']
        widgets = {
            'ten_dia_diem': forms.TextInput(attrs={'class': 'form-control'}),
            'mo_ta': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'dia_chi': forms.TextInput(attrs={'class': 'form-control'}),
            'ma_danh_muc': forms.Select(attrs={'class': 'form-control'}),
            'anh_dai_dien': forms.FileInput(attrs={'class': 'form-control'}),
        }

class RequestDiaDiemForm(forms.ModelForm):
    class Meta:
        model = RequestDiaDiem
        fields = ['ten_dia_diem', 'mo_ta', 'dia_chi', 'ma_danh_muc', 'anh_dai_dien']
        widgets = {
            'ten_dia_diem': forms.TextInput(attrs={'class': 'form-control'}),
            'mo_ta': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'dia_chi': forms.TextInput(attrs={'class': 'form-control'}),
            'ma_danh_muc': forms.Select(attrs={'class': 'form-control'}),
            'anh_dai_dien': forms.FileInput(attrs={'class': 'form-control'}),
        }

class TourDuLichForm(forms.ModelForm):
    class Meta:
        model = TourDuLich
        fields = ['ten_tour', 'thoi_gian', 'gia', 'ma_dia_diem']
        widgets = {
            'ten_tour': forms.TextInput(attrs={'class': 'form-control'}),
            'thoi_gian': forms.NumberInput(attrs={'class': 'form-control'}),
            'gia': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'ma_dia_diem': forms.Select(attrs={'class': 'form-control'}),
        }

class DanhMucForm(forms.ModelForm):
    class Meta:
        model = DanhMuc
        fields = ['ten_danh_muc', 'mo_ta']
        widgets = {
            'ten_danh_muc': forms.TextInput(attrs={'class': 'form-control'}),
            'mo_ta': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }