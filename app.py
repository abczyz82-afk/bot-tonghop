import streamlit as st
import yfinance as yf
import google.generativeai as genai
import pandas as pd

st.set_page_config(layout="wide", page_title="AI Trading Pro (Global Data)")

# --- 1. CẤU HÌNH TRỢ LÝ AI GEMINI ---
st.sidebar.header("⚙️ Cấu hình Hệ thống")
api_key = st.sidebar.text_input("Nhập Gemini API Key của bạn:", type="password")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.sidebar.warning("⚠️ Vui lòng nhập API Key ở đây để bật tính năng AI Phân tích.")

# --- 2. GIAO DIỆN CHÍNH & TÌM KIẾM MÃ TỰ DO ---
st.title("📈 Hệ Thống Tra Cứu & Trợ Lý Phân Tích Chiến Lược AI")
st.markdown("Dữ liệu được kết nối trực tiếp, miễn phí và độc lập qua **Yahoo Finance Global API**, triệt tiêu hoàn toàn lỗi nghẽn hoặc chặn IP từ các công ty chứng khoán nội địa.")

# Ô tìm kiếm tự do cho phép người dùng gõ bất kỳ mã nào họ muốn xem
ticker_input = st.text_input("🔍 Nhập bất kỳ mã cổ phiếu nào bạn muốn kiểm tra (VD: SSI, HPG, FPT, VN30F1M):", "SSI").upper().strip()

def get_clean_ticker(symbol):
    """Tự động xử lý ký hiệu để khớp với định dạng dữ liệu quốc tế"""
    if symbol in ["VNINDEX", "VNI"]:
        return "^VNI"
    if symbol in ["VN30", "VN30F1M"]:
        if symbol == "VN30F1M":
            st.warning("⚠️ Mã phái sinh VN30F1M không hỗ trợ trực tiếp trên nguồn quốc tế. Hệ thống tự động chuyển sang phân tích chứng chỉ rổ chỉ số cơ sở VN30 (E1VFVN30) làm đại diện.")
        return "E1VFVN30.HM"
    
    # Mặc định thêm hậu tố thị trường Việt Nam (.HM cho sàn HOSE)
    return f"{symbol}.HM"

if st.button("Lấy Dữ Liệu & Kích Hoạt AI"):
    yf_ticker = get_clean_ticker(ticker_input)
    
    with st.spinner(f"Đang trích xuất dữ liệu sạch của mã {yf_ticker}..."):
        try:
            stock = yf.Ticker(yf_ticker)
            # Tải dữ liệu lịch sử 1 tháng gần nhất
            df = stock.history(period="1mo")
            
            if df is not None and not df.empty:
                # Trích xuất dữ liệu phiên gần nhất và phiên trước đó để tính biến động
                latest = df.iloc[-1]
                prev = df.iloc[-2]
                price_change = latest['Close'] - prev['Close']
                
                # Hiển thị bảng số liệu trực quan cho người dùng xem
                st.subheader(f"📊 Bảng giá thực tế của {ticker_input} (Nguồn: Yahoo Finance)")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Giá đóng cửa phiên cuối", f"{latest['Close']:,.0f} đ", f"{price_change:,.0f} đ")
                col2.metric("Khối lượng giao dịch (Vol)", f"{latest['Volume']:,.0f}")
                col3.metric("Giá cao nhất phiên", f"{latest['High']:,.0f} đ")
                col4.metric("Giá thấp nhất phiên", f"{latest['Low']:,.0f} đ")
                
                st.write("Dữ liệu lịch sử các phiên giao dịch gần đây:")
                df_display = df.copy().reset_index()
                df_display['Date'] = df_display['Date'].dt.strftime('%Y-%m-%d')
                st.dataframe(df_display.tail(5)[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']], hide_index=True, use_container_width=True)
                
                # --- 3. ĐẨY DỮ LIỆU VÀO AI ĐỂ PHÂN TÍCH MỨC GIÁ HỢP LÝ ---
                if api_key:
                    st.markdown("---")
                    st.subheader(f"🤖 Trợ Lý AI Khuyến Nghị Chiến Lược Giao Dịch")
                    
                    # Đóng gói dữ liệu thô thành chuỗi văn bản gửi vào ngữ cảnh của Gemini
                    data_context = df.tail(10)[['Close', 'Volume']].to_string()
                    
                    prompt = f"""
                    Bạn là một chuyên gia phân tích kỹ thuật chứng khoán chuyên nghiệp. Đây là dữ liệu giá đóng cửa và khối lượng 10 phiên gần nhất của mã {ticker_input}:
                    {data_context}
                    
                    Dựa trên dữ liệu thực tế này, hãy thực hiện phân tích chuyên sâu và đưa ra báo cáo tư vấn:
                    1. Động lượng giá ngắn hạn đang biểu hiện thế nào (Đang tích lũy, tăng trưởng bứt phá, hay có dấu hiệu phân phối suy yếu)?
                    2. Biến động của khối lượng giao dịch (Volume) có xác nhận cho xu hướng giá hay không? Có dòng tiền lớn tham gia không?
                    3. Đưa ra khuyến nghị cụ thể: Mức giá MUA hợp lý (vùng hỗ trợ an toàn) là bao nhiêu? Mức giá BÁN mục tiêu hoặc điểm cắt lỗ kỹ thuật cụ thể dựa trên hành động giá này là bao nhiêu?
                    Yêu cầu: Trả lời ngắn gọn, quyết đoán và bắt buộc phải đưa ra các con số mức giá cụ thể, không nói chung chung.
                    """
                    
                    with st.spinner("AI đang tính toán vùng giá mua bán tối ưu..."):
                        response = model.generate_content(prompt)
                        st.info(response.text)
                else:
                    st.error("💡 Vui lòng nhập Gemini API Key ở thanh menu bên trái để kích hoạt phần phân tích chiến lược tự động từ AI.")
            else:
                st.error(f"Hệ thống không tìm thấy dữ liệu cho mã {ticker_input}. Vui lòng kiểm tra lại ký tự.")
        except Exception as e:
            st.error(f"Lỗi kết nối máy chủ dữ liệu quốc tế: {e}")
