# THSR 高鐵自動訂票機器人 🚄

一個基於 Python 和 Playwright 的台灣高鐵網路訂票自動化工具。

## ✨ 功能特色

- 🔄 **自動填寫表單** - 自動填入起訖站、日期、時間等資訊
- 🔍 **驗證碼辨識** - 使用 ddddocr 自動辨識驗證碼
- ⏰ **優先時段選擇** - 設定偏好時段，自動選擇最適合的班次
- 🔁 **智慧重試機制** - 找不到符合時段時自動重新搜尋
- 🧪 **測試模式** - 可在不實際送出訂位的情況下測試流程
- 📧 **Email 通知** - 支援訂位確認信

## 📋 系統需求

- Python 3.9 或以上
- 作業系統：Windows / macOS / Linux

## 🚀 安裝方式

### 方法一：從原始碼執行 (推薦)

```bash
# 1. 複製專案
git clone https://github.com/YOUR_USERNAME/THSR-Ticket.git
cd THSR-Ticket

# 2. 建立虛擬環境
python -m venv venv

# 3. 啟動虛擬環境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. 安裝依賴
pip install -r requirements.txt

# 5. 安裝 Playwright 瀏覽器
playwright install chromium

# 6. 執行程式
python main.py
```

### 方法二：下載可執行檔

前往 [Releases](https://github.com/YOUR_USERNAME/THSR-Ticket/releases) 頁面下載對應系統的執行檔：

- Windows: `THSR-Ticket-Windows.exe`
- macOS: `THSR-Ticket-macOS.app`
- Linux: `THSR-Ticket-Linux`

## 📖 使用說明

1. **啟動程式** - 執行 `python main.py` 或開啟下載的執行檔
2. **填寫資訊**：
   - 起站 / 迄站
   - 乘車日期 (格式: YYYY/MM/DD)
   - 出發時間
   - 車票張數
   - 身分證字號
   - 手機號碼
   - 電子郵件 (選填)
3. **設定優先時段** (選填)
   - 格式：`HH:MM-HH:MM`
   - 可設定多個時段，用逗號分隔：`12:00-14:00, 18:00-20:00`
4. **選擇模式**：
   - ✅ 測試模式：填寫完資料但不送出訂位
   - ❌ 正式模式：實際完成訂位
5. **點擊「開始訂票」**

## ⚠️ 注意事項

- 本工具僅供學習和個人使用
- 請遵守台灣高鐵網站的使用條款
- 驗證碼辨識不保證 100% 正確，可能需要手動輸入
- 高鐵系統對操作速度敏感，請確保網路穩定

## 🛠️ 開發者指南

### 專案結構

```
THSR-Ticket/
├── main.py           # 主程式 (GUI 入口)
├── bot.py            # 訂票邏輯核心
├── requirements.txt  # 依賴清單
├── README.md         # 說明文件
├── build.py          # 打包腳本
└── .github/
    └── workflows/
        └── build.yml # CI/CD 自動打包
```

### 本地打包

```bash
# 安裝打包工具
pip install pyinstaller

# 執行打包腳本
python build.py
```

## 📄 授權條款

MIT License

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

## 免責聲明

本專案僅供教育和學習目的。使用者應自行承擔使用本工具的風險和責任。開發者不對任何因使用本工具而導致的損失負責。
