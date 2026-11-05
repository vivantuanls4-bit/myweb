# 🌍 Website Giới Thiệu Du Lịch Địa Phương
## 🎯 1. Mục tiêu
Dự án nhằm xây dựng một hệ thống website giới thiệu du lịch địa phương sử dụng Python (Django), với các mục tiêu:
- Xây dựng ứng dụng web hoàn chỉnh (database, giao diện, xử lý nghiệp vụ)
- Áp dụng kiến thức lập trình web, CSDL, phân quyền
- Mô phỏng quy trình: đăng ký, đăng nhập, đặt tour, bình luận
- Hệ thống chạy ổn định và có thể mở rộng

## 🏗️ 2. Kiến trúc hệ thống
### Client – Server
- Client: Trình duyệt web
- Server: Django xử lý logic

### Mô hình MVT
- Model: Dữ liệu
- View: Xử lý logic
- Template: Giao diện

## 🧩 3. Công nghệ sử dụng
- Python
- Django
- HTML, CSS, Bootstrap, JavaScript
- SQLite / PostgreSQL
- Pillow, Chart.js

## ⚙️ 4. Hướng dẫn cài đặt 

### Cài đặt python, Django và thư viện
pip install -r requirements.txt

### Tạo projiect Django
django-admin startproject webDuLich

sau đó ta vào terminal gõ câu lệnh cd webDuLich để vào vị trí tệp webDuLich

### Tạo APP
python manage.py startapp app

### Tạo và cập nhật cơ sở dữ liệu
python manage.py makemigrations (Chỉ chạy câu lệnh này khi bạn thay đổi các Model (cấu trúc bảng database) trong Django)

python manage.py migrate

### Tạo tài khoản admin
python manage.py createsuperuser

### Chạy server
python manage.py runserver

## 🔐 5. Tài khoản mẫu
- Admin: admin / 123456
- User: thanh@gmail.com / 123456
## 6. URL tham khảo
- Trang chủ: http://127.0.0.1:8000 
- Admin: http://127.0.0.1:8000/admin/ 
- Dịch vụ: http://127.0.0.1:8000/service/
- Thống kế và báo cáo: http://127.0.0.1:8000/report/

## 7. Triển khai lên Render
1. Đẩy `render.yaml` ở thư mục gốc lên nhánh `main` trên GitHub.
2. Trên Render, chọn **New +** → **Blueprint** và kết nối repository này.
3. Render sẽ tạo web service và PostgreSQL từ Blueprint. `SECRET_KEY` được Render tự tạo; không đưa secret vào Git.
4. Chờ build/deploy hoàn tất rồi mở URL của web service.

Blueprint chạy migration khi service khởi động và dùng WhiteNoise để phục vụ static files. Database của gói miễn phí có thời hạn theo chính sách Render; các ảnh tải lên cần dịch vụ lưu trữ bền vững riêng vì filesystem của web service không bền vững.
