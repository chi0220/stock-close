import os
import pickle
from datetime import datetime
from config import CACHE_DIR, CACHE_CLOSE_PATH, FINAL_OUTPUT_FILENAME, REPORTS_DIR
from scraper_close import scrape_close_prices


# ── 快取：失敗時退回上次成功資料（比照 Stock2v2.0 的模式）───────────────────

def _load_cache_fallback(cache_path: str):
    if not os.path.exists(cache_path):
        return None
    try:
        with open(cache_path, 'rb') as f:
            return pickle.load(f)
    except Exception:
        return None


def _save_cache(data, cache_path: str) -> None:
    try:
        with open(cache_path, 'wb') as f:
            pickle.dump(data, f)
    except Exception as e:
        print(f"  [警告] 快取寫入失敗: {e}")


def run_task(label: str, cache_path: str, scrape_fn):
    print(f"\n[{label}] 開始執行...")
    try:
        data = scrape_fn()
    except Exception as e:
        print(f"  [錯誤] {label} 執行時發生例外: {e}")
        data = None

    if data is not None and not data.empty:
        _save_cache(data, cache_path)
        return data, False

    print(f"  [警告] {label} 本次無資料，嘗試退回上次快取...")
    fallback = _load_cache_fallback(cache_path)
    if fallback is not None and not fallback.empty:
        print(f"  [資訊] {label} 使用上次快取資料（可能非最新）。")
        return fallback, True

    print(f"  [錯誤] {label} 無資料可用（本次失敗且無可用快取）。")
    return None, False


def format_close_section(df) -> str:
    if df is None:
        return "## [CLOSE]\n```csv\nError: No Data\n```\n\n"
    csv_text = df.to_csv(index=False)
    return f"## [CLOSE]\n```csv\n{csv_text}```\n\n"


if __name__ == '__main__':
    print("程式開始執行（收盤價爬取，失敗時退回上次快取）\n")
    os.makedirs(CACHE_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)

    df_close, is_stale = run_task("收盤價", CACHE_CLOSE_PATH, scrape_close_prices)

    try:
        now = datetime.now()
        parts = []

        parts.append("# 收盤價 MD\n")
        parts.append(f"# T:{now.strftime('%Y-%m-%d %H:%M')}\n\n")

        if is_stale:
            parts.append("> ⚠️ 本次即時爬取失敗，內容為上次成功快取的退回資料，可能非最新。\n\n")

        parts.append(format_close_section(df_close))

        report_content = "".join(parts)

        with open(FINAL_OUTPUT_FILENAME, 'w', encoding='utf_8_sig') as f:
            f.write(report_content)
        print(f"\n[成功] 最新報告已儲存至：{FINAL_OUTPUT_FILENAME}")

        date_dir = os.path.join(REPORTS_DIR, now.strftime('%Y-%m-%d'))
        os.makedirs(date_dir, exist_ok=True)
        versioned_path = os.path.join(date_dir, f"{now.strftime('%H%M')}.txt")
        with open(versioned_path, 'w', encoding='utf_8_sig') as f:
            f.write(report_content)
        print(f"[成功] 版本化備份已儲存至：{versioned_path}")

    except Exception as e:
        print(f"\n[嚴重錯誤] 寫入報告時發生問題: {e}")
        import traceback
        traceback.print_exc()

    print("\n程式執行結束。")
