import streamlit as st
import pandas as pd
import asyncio
import random
import time

# ==========================================
# 1. KHỞI TẠO LUỒNG TÍNH TOÁN NGẦM (BACKGROUND)
# ==========================================
# Sử dụng bộ nhớ tạm (Session State) của Streamlit làm kho lưu trữ dữ liệu
if "market_data" not in st.session_state:
    st.session_state.market_data = {
        "vn30_price": 1250.0,
        "vn30_signal": "Đi ngang",
        "equities": [
            {"Mã": "HPG", "Giá": 28500, "RSI": 45, "Điểm Hội Tụ": 8},
            {"Mã": "SSI", "Giá": 35200, "RSI": 62, "Điểm Hội Tụ": 9},
            {"Mã": "FPT", "Giá": 115000, "RSI": 55, "Điểm Hội Tụ": 6},
            {"Mã": "VND", "Giá": 15100, "RSI": 32, "Điểm Hội Tụ": 7}
        ]
    }

def update_market_simulation():
    """Hàm này đóng vai trò giống file main.py cũ: 
    Tự động tính toán cập nhật giá thị trường mỗi khi Dashboard làm mới"""
    data = st.session_state.market_data
    
    # Giả lập giá VN30F1M nhảy liên tục
    data["vn30_price"] += round(random.choice([-0.5, 0.0, 0.5]), 1)
    data["vn30_signal"] = random.choice(["Tăng", "Giảm", "Đi ngang"])
    
    # Giả lập biến động điểm số của nhóm cổ phiếu cơ sở
    for stock in data["equities"]:
        stock["Giá"] += random.choice([-100, 0, 100])
        stock["RSI"] = max(10, min(90, stock["RSI"] + random.choice([-1, 0, 1])))
        stock["Điểm Hội Tụ"] = random.choice([6, 7, 8, 9, 10])
        
    st.session_state.market_data = data

# ==========================================
# 2. THIẾT KẾ GIAO DIỆN HIỂN THỊ (STREAMLIT)
# ==========================================
st.set_page_config(layout="wide", page_title="AI Trading Dashboard")
st.title("📊 Bảng Điều Khiển Chứng Khoán Đa Luồng AI")

# Chạy hàm cập nhật dữ liệu trước khi vẽ giao diện
update_market_simulation()
current_data = st.session_state.market_data

# Chia màn hình làm 2 cột độc lập
col1, col2 = st.columns(2)

with col1:
    st.header("⚡ VN30F1M (Phái sinh realtime)")
    st.metric(
        label="Giá khớp hiện tại", 
        value=f"{current_data['vn30_price']:.1f} điểm", 
        delta=current_data['vn30_signal']
    )
    st.caption("Mẹo: Nhấn nút 'R' trên bàn phím hoặc bấm Re-run để ép cập nhật lệnh tức thì.")

with col2:
    st.header("🏢 Tín hiệu Cơ sở (Điểm hội tụ >= 8)")
    df = pd.DataFrame(current_data["equities"])
    # Bộ lọc chiến lược: Chỉ hiện mã có tỷ lệ thắng/điểm hội tụ cao
    high_score_df = df[df["Điểm Hội Tụ"] >= 8]
    st.dataframe(high_score_df, use_container_width=True, hide_index=True)

# Tự động kích hoạt làm mới giao diện sau mỗi 2 giây
time.sleep(2)
st.rerun()
