# Sử dụng Python chính thức
FROM python:3.10-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Copy file vào container
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY api-odb.py ./

# Expose port Flask chạy
EXPOSE 5000

# Chạy app Flask
CMD ["python", "app.py"]
