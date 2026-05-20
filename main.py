import asyncio
import pandas as pd

# Giả lập biến toàn cục (Shared State) để lưu dữ liệu tạm thời
# Trong thực tế, bạn nên dùng Redis để Dashboard và Core Bot giao tiếp độc lập
SHARED_STATE = {
    "vn30f1m": {},
    "equities_signals": pd.DataFrame()
}

async def stream_vn30f1m():
    """Luồng 1: Chạy liên tục 24/7, nhận từng tick giá của Phái sinh"""
    print("Khởi động luồng Websocket VN30F1M...")
    # Giả lập kết nối Websocket tới VPS/SSI
    while True:
        # Nhận tick data mới nhất
        new_price = await fetch_websocket_tick() 
        
        # Cập nhật và tính toán RSI, MACD cực nhanh bằng NumPy/deque
        signal = calculate_vn30_confluence(new_price)
        
        # Lưu vào cache để Dashboard lấy lên hiển thị
        SHARED_STATE["vn30f1m"] = signal
        
        # Nghỉ 0.1s tránh quá tải CPU (tuỳ tốc độ Websocket)
        await asyncio.sleep(0.1) 

async def poll_equities():
    """Luồng 2: Quét toàn bộ thị trường cơ sở mỗi 15 phút hoặc cuối ngày"""
    print("Khởi động luồng Quét Cơ sở (T+2.5)...")
    tickers = ["SSI", "HPG", "FPT", "VND", "TCB"] # Danh sách theo dõi
    
    while True:
        print("Đang tải dữ liệu OHLC cho thị trường cơ sở...")
        # Gọi REST API lấy dữ liệu 1 loạt mã chứng khoán (Batch processing)
        df_equities = await fetch_rest_api_batch(tickers)
        
        # Tính toán vector hóa bằng Pandas cho tất cả mã cùng lúc (rất nhanh)
        df_signals = calculate_equity_confluence(df_equities)
        
        # Lọc ra các mã đạt điểm hội tụ > 8/10
        buy_candidates = df_signals[df_signals['Confluence_Score'] >= 8]
        
        # Cập nhật vào cache
        SHARED_STATE["equities_signals"] = buy_candidates
        
        # Nghỉ 15 phút (900 giây) mới quét lại, vì cơ sở không cần nhảy theo tick
        await asyncio.sleep(900)

async def main():
    """Chạy song song cả 2 luồng"""
    task1 = asyncio.create_task(stream_vn30f1m())
    task2 = asyncio.create_task(poll_equities())
    
    # Đợi cả 2 task chạy (vòng lặp vô hạn)
    await asyncio.gather(task1, task2)

if __name__ == "__main__":
    asyncio.run(main())
