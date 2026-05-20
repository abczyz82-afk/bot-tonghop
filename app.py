import streamlit as st
import time
# Khởi tạo kết nối tới Redis (đã lưu dữ liệu từ main.py)

st.title("Hệ Thống Giao Dịch Đa Luồng")

col1, col2 = st.columns(2)

with col1:
    st.header("⚡ VN30F1M (Real-time)")
    # Widget placeholder cho biểu đồ Phái sinh cập nhật mỗi giây
    vn30_placeholder = st.empty()

with col2:
    st.header("🏢 Cơ Sở (T+2.5)")
    # Bảng hiển thị các mã cơ sở đạt điểm hội tụ cao
    equity_placeholder = st.empty()

# Vòng lặp cập nhật UI
while True:
    # Lấy dữ liệu từ Cache (Redis/DB) đã được main.py tính toán sẵn
    vn30_data = get_from_redis("vn30f1m") 
    equity_data = get_from_redis("equities_signals")
    
    # Cập nhật giao diện
    vn30_placeholder.metric(label="Giá Phái Sinh", value=vn30_data['price'], delta=vn30_data['signal'])
    equity_placeholder.dataframe(equity_data)
    
    time.sleep(1) # Refresh Dashboard mỗi giây
