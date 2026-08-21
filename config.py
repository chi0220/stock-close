# ==============================================================================
# config.py - 全域參數設定
# ==============================================================================

# 路徑與檔案設定
CACHE_DIR             = 'cache'
CACHE_CLOSE_PATH      = 'cache/cache_close.pkl'
FINAL_OUTPUT_FILENAME = 'stock_close_report.txt'
REPORTS_DIR           = 'reports'  # 版本化報告存放資料夾（每次執行存一份）

# 網址設定（沿用 Stock2v2.0 的資料來源：HiStock 全市場排行頁）
HISTOCK_RANK_URL = 'https://histock.tw/stock/rank.aspx?m=13&d=1&p=all'
