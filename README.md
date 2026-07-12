# Label_HetroD

交通場景互動標註與前處理工具。這個 repo 主要分成兩部分：

- 標註工具：`label_tool/` 與 `refine_tool/`
- 資料前處理：根目錄下的計算、轉換與分析腳本
- GitHub 範例資料：`sample_data/` 裡放的是可公開的最小 sample data

如果你是第一次打開這個專案，建議先看下面的「快速開始」，再決定要跑標註工具還是後處理腳本。

## 專案結構

```text
Label_HetroD/
├── label_tool/          # 主要標註工具
├── refine_tool/         # 另一份標註工具版本
├── scenario_video_export/ # 已標註 scenario 匯出成影片的後處理腳本
├── sample_data/         # 最小可公開 sample data
├── data/                # 本機實際資料與前處理輸出
├── preprocess_label.py  # 產生 trackid_class.json
├── calculate_distance.py # 計算最短距離
├── calculate_pet.py      # 計算 PET
├── draw_bbox.py         # bbox 繪製與資料檢查
├── label_area_type.py   # 區域類型分析
└── change_dict_to_parquet.py
```

`label_tool/` 與 `refine_tool/` 目前結構幾乎相同，保留兩份是為了支援不同工作流程或作為備份版本。若你之後只想維護一個主版本，可以再進一步把共用邏輯抽出去。

另外，`scenario_video_export/generate_labeled_videos.py` 是一支後處理腳本，會把已標註的 scenario 轉成影片，方便複核與展示。

`sample_data/` 則是給 GitHub 預覽和快速示範用的最小資料集。你可以先跑 `python prepare_sample_data.py`，把這份 sample 複製到本機的 `data/`，再啟動標註工具。

## label_tool 與 refine_tool 的差異

- `label_tool/` 是主要標註工具，流程比較完整，適合從頭開始標註新 pair。
- `refine_tool/` 是整理或複核用版本，偏向處理已經有標註結果的 pair，讓你快速檢查與修正。
- 兩者的啟動方式目前相同，差別主要在 controller 與 video controller 的流程邏輯，而不是入口檔。
- 如果你只想維護一套主流程，通常會保留 `label_tool/` 當主版本，`refine_tool/` 當輔助版本。

## 安裝

建議使用 `uv` 建立獨立環境：

```bash
uv sync --no-install-project
```

如果你只想建立虛擬環境並沿用 `requirements.txt`：

```bash
uv venv .venv
uv pip install -r requirements.txt -p .venv/bin/python
```

如果你已經完成前面的安裝，後續只要在專案根目錄執行 `uv sync --no-install-project` 即可恢復環境。

## 快速開始

1. 安裝依賴。
2. 執行 `python prepare_sample_data.py`，把 sample data 複製到本機 `data/`。
3. 進入 `label_tool/` 執行 `python start.py` 開啟標註介面。
4. 如果要產出已標註 scenario 的影片，執行 `python scenario_video_export/generate_labeled_videos.py`。

## 執行標註工具

在專案根目錄執行：

```bash
cd label_tool
python start.py
```

切換 iPad 介面：

```bash
cd label_tool
python start.py --ui ipad
```

## 資料需求

標註工具會使用本機 `data/` 內的中繼資料，常見必要檔案包含：

- `data/00_background.png`
- `data/track_frame_dict.json`
- `data/trackid_objects.json`
- `data/trackid_class.json`
- `data/pet_distance_dict.json`

如果只有原始 CSV，可以先執行前處理腳本建立中繼檔：

```bash
python preprocess_label.py
python calculate_distance.py
python calculate_pet.py
```

## 發佈到 GitHub 的建議

下列檔案通常是由前處理腳本生成，不建議直接提交：

- `track_frame_dict.json`
- `trackid_objects.json`
- `data/tmp_distance_jsons/`
- `data/min_distance_result.json`
- `data/pet_result.json`

這些檔案建議保留在本機資料夾，讓別人下載 repo 後再自行生成。

如果你只想先看範例，GitHub 上的 `sample_data/` 就是一份只有一到兩筆資料的最小版本。

## 常見輸出

- 標註結果會寫回 `data/labeled_scenarios.json`。
- 距離與 PET 的中繼結果會由前處理腳本產生。
- `scenario_video_export/` 會把已標註 pair 轉成 mp4，方便複核與展示。

## 依賴

主要依賴已整理在 `requirements.txt`，可直接搭配 `uv` 安裝。
