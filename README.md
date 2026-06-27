# Ultima IV 繁體中文網頁版 (u4Web) 雲端編譯與部署專案

本專案是《Ultima IV: Quest of the Avatar 繁體中文版》的網頁移植版專案。本專案採用 **方案 A (GitHub Actions)**：您**不需要在自己的電腦上安裝任何編譯工具**，只需將此目錄上傳至 GitHub，雲端系統便會自動完成 WebAssembly (Wasm) 的編譯、原版遊戲下載與中文化打包，並自動發布到您的 **Hugging Face Space** 靜態網頁上。

---

## 🚀 部署指南 (Hugging Face Spaces)

請依照以下 4 個步驟，設定您的雲端自動化編譯與部署鏈：

### 1. 建立 Hugging Face Space
1. 登入/註冊 [Hugging Face](https://huggingface.co/)。
2. 點擊右上角個人頭像，選擇 **New Space**。
3. 輸入 Space 名稱（例如：`u4Web`）。
4. **關鍵設定**：在 **SDK** 處選擇 **`Static`** (靜態網頁託管)。
5. 點擊 **Create Space**。

### 2. 取得 Hugging Face 存取 Token
1. 前往 Hugging Face 的 [Settings -> Access Tokens](https://huggingface.co/settings/tokens)。
2. 點選 **New token**。
3. Token 名稱設定為 `u4Web-deploy`，**Role (權限)** 必須選擇 **`Write`** (寫入權限)。
4. 複製產生的 Token 內容。

### 3. 設定 GitHub Secrets
1. 在 GitHub 上建立一個新的儲存庫 (Repository)，名稱為 `u4Web`。
2. 進入該 GitHub 儲存庫的 **Settings** -> **Secrets and variables** -> **Actions**。
3. 點選 **New repository secret**，新增以下兩個 Secret：
   * **`HF_TOKEN`**：貼上您在步驟 2 複製的 Hugging Face Write Token。
   * **`HF_SPACE_URL`**：填入您的 Space Git 連結。
     * 格式為：`https://huggingface.co/spaces/您的帳號/您的Space名稱`
     * 例如：`https://huggingface.co/spaces/ark945/u4Web`

### 4. 推送程式碼 (Deploy!)
將本目錄的所有檔案（包含 `.github/`、`web/`、`patches/`、`assets/`、`tools/` 等）Push 至您的 GitHub 儲存庫。
* 當您 Push 到 `main` 或 `master` 分支後，GitHub Actions 會立刻啟動。
* 您可以前往 GitHub 儲存庫的 **Actions** 分頁查看進度，編譯大約需要 2~3 分鐘。
* 編譯完成後，Action 會自動把打包好的靜態網頁（含遊戲 Wasm 與資料包）推播至您的 Hugging Face Space，此時即可在瀏覽器上網頁即開即玩！

---

## 🎮 網頁功能說明

* **守護密碼**：為了防止版權爭議，網頁預設有毛玻璃密碼鎖定。
  * 預設密碼為：**`arku4`**
* **自動存檔**：在遊戲內進行正常存檔後，系統會自動在背景將存檔同步至您瀏覽器的 **IndexedDB** 本機資料庫。重新整理頁面或重開機存檔皆不會遺失。
* **下載存檔備份**：點擊網頁下方的下載按鈕，會自動將您的遊戲存檔（PARTY.SAV 等）打包成 `u4_saves_backup.zip` 下載至本機，方便做實體備份。
* **上傳存檔還原**：點擊上傳按鈕並選擇您備份的 ZIP，即可在一秒內將您的存檔導回瀏覽器中繼續遊玩（亦適用於將存檔轉移至手機或其他電腦遊玩）。
