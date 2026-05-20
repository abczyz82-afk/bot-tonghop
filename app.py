import streamlit as st
from vnstock3 import Vnstock
import google.generativeai as genai
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(layout="wide", page_title="AI Trading Pro")

# --- 1. CẤU HÌNH API GEMINI (AI) ---
st.sidebar.header("⚙️ Cấu hình Hệ thống")
api_key = st.sidebar.text_input("Nhập Gemini API Key của bạn:", type="password")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.sidebar.warning("⚠️ Vui lòng nhập API Key để bật tính năng AI.")

# --- 2. GIAO DIỆN CHÍNH & TÌM KIẾM MÃ ---
st.title("📈 Bảng Điều Khiển & Trợ Lý Phân Tích AI")
ticker = st.text_input("🔍 Nhập mã chứng khoán bạn muốn xem (VD: SSI, HPG, FPT, VN30F1M):", "SSI").upper()

# Hàm lấy dữ liệu thật từ Vnstock
@st.cache_data(ttl=60) # Lưu cache 60 giây để không bị khóa API sàn
def fetch_real_data(symbol):
    try:
        stock = Vnstock().stock(symbol=symbol, source='TCBS')
        # Lấy dữ liệu 30 ngày gần nhất
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=45)).strftime('%Y-%m-%d')
        df = stock.quote.history(start=start_date, end=end_date, interval='1D')
        return df
    except Exception as e:
        return None

if st.button("Lấy Dữ Liệu & Phân Tích"):
    with st.spinner(f"Đang kéo dữ liệu thật của {ticker} từ thị trường..."):
        df = fetch_real_data(ticker)
        
        if df is not None and not df.empty:
            # Lấy thông tin phiên gần nhất
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            price_change = latest['close'] - prev['close']
            
            # Hiển thị số liệu
            st.subheader(f"Dữ liệu hiện tại: {ticker}")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Giá đóng cửa", f"{latest['close']:,.0f} đ", f"{price_change:,.0f} đ")
            col2.metric("Khối lượng (Vol)", f"{latest['volume']:,.0f}")
            col3.metric("Giá Cao nhất", f"{latest['high']:,.0f} đ")
            col4.metric("Giá Thấp nhất", f"{latest['low']:,.0f} đ")
            
            st.write("Lịch sử giá 5 phiên gần nhất:")
            st.dataframe(df.tail(5)[['time', 'open', 'high', 'low', 'close', 'volume']], hide_index=True)
            
            # --- 3. TÍCH HỢP GEMINI AI ---
            if api_key:
                st.markdown("---")
                st.subheader(f"🤖 AI Nhận định về {ticker}")
                
                # Nén dữ liệu thô thành text để gửi cho AI
                data_context = df.tail(10)[['time', 'close', 'volume']].to_string()
                
                prompt = f"""
                Bạn là chuyên gia chứng khoán. Dưới đây là dữ liệu giá và khối lượng 10 phiên gần nhất của mã {ticker}:
                {data_context}
                
                Dựa vào dữ liệu thật này, hãy phân tích ngắn gọn:
                1. Xu hướng ngắn hạn đang là gì?
                2. Khối lượng giao dịch có ủng hộ xu hướng giá không?
                3. Đề xuất một kịch bản giao dịch (Mua/Bán/Quan sát) và mức giá mục tiêu.
                Lưu ý: Trả lời đi thẳng vào vấn đề, không dài dòng.
                """
                
                with st.spinner("AI đang suy nghĩ..."):
                    try:
                        response = model.generate_content(prompt)
                        st.info(response.text)
                    except Exception as e:
                        st.error(f"Lỗi khi gọi AI: {e}")
            else:
                st.warning("Nhập API Key ở cột bên trái để AI phân tích dữ liệu trên.")
        else:
            st.error(f"Không tìm thấy dữ liệu cho mã {ticker}. Vui lòng kiểm tra lại tên mã.")
