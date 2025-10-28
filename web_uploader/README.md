# Web Uploader - Local Data Upload Script

This script uploads your locally generated price comparison Excel files to the Railway web application.

## Setup

1. **Copy config example:**
   ```bash
   copy web_uploader\config.example.ini web_uploader\config.ini
   ```

2. **Edit config.ini:**
   ```ini
   [API]
   url = https://your-app.railway.app/api/upload
   key = your-api-key-from-railway
   
   [LOCAL]
   data_directory = data/output/excel
   ```

3. **Get API key from Railway:**
   - Go to your Railway project
   - Open "Variables" tab
   - Copy the `API_KEY` value
   - Paste it into `config.ini`

## Usage

### Basic Upload

```bash
python web_uploader/uploader.py
```

The script will:
1. Find the latest `price_comparison_*.xlsx` file
2. Show file information
3. Ask for confirmation
4. Upload to Railway
5. Display statistics

### Example Output

```
============================================================
 Coffee Price Monitor - Data Uploader
============================================================

[INFO] Looking for files in: data/output/excel
[INFO] Found file: price_comparison_20251028_143000.xlsx

[INFO] Uploading file: price_comparison_20251028_143000.xlsx
[INFO] File size: 156.23 KB
[INFO] Modified: 2025-10-28 14:30:15
[INFO] Sending request to: https://your-app.railway.app/api/upload
[INFO] Please wait...

[SUCCESS] File uploaded successfully!
[INFO] Upload ID: 42
[INFO] Upload Date: 2025-10-28

=== Statistics ===
Total Products: 127
Total Value: 245678.50 GEL
Products Cheaper: 45
Products Expensive: 32
No Competitors: 50

[INFO] Data is now available on the web application
[INFO] Visit: https://your-app.railway.app
```

## Workflow

1. **Run full cycle locally:**
   ```bash
   python run_full_cycle.py
   ```
   This generates the Excel file in `data/output/excel/`

2. **Upload to Railway:**
   ```bash
   python web_uploader/uploader.py
   ```

3. **View on web:**
   - Open Railway app URL in browser
   - Login
   - View latest data on dashboard

## Troubleshooting

### "Config file not found"
- Run the script once - it will create a template
- Edit `web_uploader/config.ini` with your settings

### "Authentication failed"
- Check API key in `config.ini`
- Get correct API key from Railway Variables tab

### "Connection failed"
- Check internet connection
- Verify Railway app URL is correct
- Ensure Railway app is deployed and running

### "No price comparison files found"
- Run `python run_full_cycle.py` first
- Check `data/output/excel/` directory exists
- Verify file pattern: `price_comparison_*.xlsx`

## Advanced

### Specify custom config file:
```python
from web_uploader.uploader import PriceDataUploader

uploader = PriceDataUploader('path/to/custom/config.ini')
uploader.run()
```

### Upload specific file:
```python
from pathlib import Path
from web_uploader.uploader import PriceDataUploader

uploader = PriceDataUploader()
file_path = Path('data/output/excel/price_comparison_20251028.xlsx')
success = uploader.upload_file(file_path)
```

## Requirements

- Python 3.8+
- `requests` library (install: `pip install requests`)

## Security

- **Never commit `config.ini` to git** (it contains API key)
- Keep your API key secure
- Only share with trusted team members
- Rotate API key if compromised

## Notes

- Only one upload per date is stored
- Uploading on the same date will replace existing data
- All statistics are recalculated on upload
- Upload typically takes 5-15 seconds depending on file size

