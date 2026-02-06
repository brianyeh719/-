# THSR 高鐵自動訂票機器人 🚄

一個基於 Python 和 Playwright 的台灣高鐵網路訂票自動化工具。

## ✨ 功能特色

- 🔄 **自動填寫表單** - 自動填入起訖站、日期、時間等資訊
- 🔍 **驗證碼辨識** - 使用 ddddocr 自動辨識驗證碼
- ⏰ **優先時段選擇** - 設定偏好時段，自動選擇最適合的班次
- 🔁 **智慧重試機制** - 找不到符合時段時自動重新搜尋
- 🧪 **測試模式** - 可在不實際送出訂位的情況下測試流程

## 📋 系統需求

- Python 3.9 或以上
- 作業系統：Windows / macOS / Linux

## 🚀 安裝方式（兩種方案）

### 方案一：一鍵安裝（Windows 推薦）

這個方案不需要理解虛擬環境，雙擊即可。

1. 安裝 Python 3.9+（只需一次）
2. 雙擊 `run.bat`
3. 第一次會自動呼叫 `setup.ps1` 進行安裝

如果 PowerShell 被限制執行腳本，請用以下指令手動跑一次：

```powershell
powershell -ExecutionPolicy Bypass -File setup.ps1
```

之後只要雙擊 `run.bat` 就能直接啟動。

### 方案二：原始碼手動安裝（跨平台）

```bash
# 1. 複製專案
git clone https://github.com/THSR-TicketRobot/THSR-TicketRobot.git
cd THSR-Ticket

# 2. (可選) 建立虛擬環境
python -m venv .venv

# 3. 啟用虛擬環境 (Windows)
.\.venv\Scripts\activate

# 3. 啟用虛擬環境 (macOS / Linux)
# source .venv/bin/activate

# 4. 安裝依賴
pip install -r requirements.txt

# 5. 安裝 Playwright 瀏覽器
playwright install chromium

# 6. 執行程式
python main.py
```

> macOS / Linux 目前請使用此手動方案。


## 🛠️ 開發者指南

### 專案結構

```
THSR-Ticket/
├── main.py           # 主程式 (GUI 入口)
├── bot.py            # 訂票邏輯核心
├── requirements.txt  # 依賴清單
├── README.md         # 說明文件
├── setup.ps1         # 一鍵安裝腳本 (Windows)
├── run.bat           # 一鍵啟動腳本 (Windows)

```

### 檔案操作流程（快速理解）

1. 使用者雙擊 `run.bat`
2. `run.bat` 檢查 `.venv` 是否存在
3. 若沒有 `.venv`，則自動執行 `setup.ps1`
4. `setup.ps1` 建立 `.venv`、安裝依賴、安裝 Playwright Chromium
5. `run.bat` 啟動 `main.py`
6. `main.py` 透過 `bot.py` 執行訂票流程
## ⚠️ 注意事項

- 本工具僅供學習和個人使用
- 請遵守台灣高鐵網站的使用條款
- 驗證碼辨識不保證 100% 正確，
## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

## 免責聲明

本專案僅供教育和學習目的。使用者應自行承擔使用本工具的風險和責任。開發者不對任何因使用本工具而導致的損失負責。
