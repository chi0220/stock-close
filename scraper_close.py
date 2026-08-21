"""
scraper_close.py
──────────────────────────────
抓取 HiStock 全市場排行頁，只取「代號」與「收盤價」兩欄。
資料來源與清理邏輯比照 Stock2v2.0 的 scraper_1_ranking.py。
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup
from config import HISTOCK_RANK_URL


def clean_numeric(val: str) -> str:
    """清理 HiStock 數字：▲▼ 符號、%、逗號"""
    s = str(val).strip()
    is_negative = ('▼' in s) or ('▽' in s)
    for ch in ('▲', '▼', '▽', '+', '%', ',', ' '):
        s = s.replace(ch, '')
    if is_negative and s and not s.startswith('-'):
        s = '-' + s
    return s


def _scrape_all_rows() -> list[dict]:
    """從 HiStock 抓取所有排行列，只保留代號與收盤價"""
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/122.0.0.0 Safari/537.36'
        )
    }
    resp = requests.get(HISTOCK_RANK_URL, headers=headers, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, 'html.parser')
    rows = soup.select('table#CPHB1_gv tr')[1:]

    records = []
    for row in rows:
        cells = row.find_all('td')
        if len(cells) < 13:
            continue
        try:
            records.append({
                '代號':   cells[0].text.strip(),
                '收盤價': clean_numeric(cells[2].text),
            })
        except (IndexError, Exception):
            continue

    return records


def scrape_close_prices() -> 'pd.DataFrame | None':
    """主函式：抓取全市場代號+收盤價，回傳 DataFrame"""
    print("\n[任務] 抓取 HiStock 全市場收盤價...")

    try:
        records = _scrape_all_rows()
    except Exception as e:
        print(f"  [錯誤] HiStock 爬蟲失敗: {e}")
        return None

    if not records:
        print("  [錯誤] 未取得任何資料。")
        return None

    df = pd.DataFrame(records)
    df['收盤價'] = pd.to_numeric(df['收盤價'], errors='coerce').fillna(0.0)
    df = df[df['收盤價'] > 0].reset_index(drop=True)

    print(f"  [成功] 共取得 {len(df)} 檔收盤價。")
    return df
