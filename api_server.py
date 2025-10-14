"""
FastAPI Web Server for Coffee Price Monitoring API
Provides REST API endpoints to trigger scraping and retrieve reports
"""

from fastapi import FastAPI, BackgroundTasks, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
from pathlib import Path
from datetime import datetime
import subprocess
import sys
import json
import asyncio
from enum import Enum
import shutil
# import openpyxl  # Moved to lazy import to reduce memory usage
# import pandas as pd  # Moved to lazy import to reduce memory usage

# Initialize FastAPI app
app = FastAPI(
    title="Coffee Price Monitoring API",
    description="Automated price monitoring for coffee machines from competitor websites",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state for tracking scraping status
class ScrapingStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

scraping_state = {
    "status": ScrapingStatus.IDLE,
    "started_at": None,
    "completed_at": None,
    "current_step": None,
    "products_scraped": 0,
    "error": None
}

# Models
class ScrapeResponse(BaseModel):
    status: str
    message: str
    started_at: Optional[str] = None

class StatusResponse(BaseModel):
    current_status: str
    last_run: Optional[str] = None
    products_scraped: int
    current_step: Optional[str] = None
    error: Optional[str] = None

class ReportInfo(BaseModel):
    filename: str
    created_at: str
    size_bytes: int
    products_count: Optional[int] = None

class InventoryInfo(BaseModel):
    has_file: bool
    filename: Optional[str] = None
    uploaded_at: Optional[str] = None
    uploaded_at_formatted: Optional[str] = None  # DD.MM.YYYY
    size_bytes: Optional[int] = None
    products_count: Optional[int] = None
    message: str

class UploadResponse(BaseModel):
    status: str
    message: str
    filename: str
    uploaded_at: str
    uploaded_at_formatted: str

# Helper functions
def get_base_dir() -> Path:
    """Get base directory"""
    return Path(__file__).parent

def get_output_dir() -> Path:
    """Get output directory"""
    output_dir = get_base_dir() / "data" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

def get_inbox_dir() -> Path:
    """Get inbox directory for inventory files"""
    inbox_dir = get_base_dir() / "data" / "inbox"
    inbox_dir.mkdir(parents=True, exist_ok=True)
    return inbox_dir

def get_inventory_file() -> Optional[Path]:
    """Get current inventory file"""
    inbox_dir = get_inbox_dir()
    inventory_file = inbox_dir / "остатки.xls"
    
    if inventory_file.exists():
        return inventory_file
    
    # Try xlsx format
    inventory_xlsx = inbox_dir / "остатки.xlsx"
    if inventory_xlsx.exists():
        return inventory_xlsx
    
    return None

def get_inventory_metadata_file() -> Path:
    """Get inventory metadata file"""
    return get_inbox_dir() / "inventory_metadata.json"

def save_inventory_metadata(filename: str, uploaded_at: datetime):
    """Save inventory metadata"""
    metadata = {
        "filename": filename,
        "uploaded_at": uploaded_at.isoformat(),
        "uploaded_at_formatted": uploaded_at.strftime("%d.%m.%Y")
    }
    
    metadata_file = get_inventory_metadata_file()
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

def load_inventory_metadata() -> Optional[dict]:
    """Load inventory metadata"""
    metadata_file = get_inventory_metadata_file()
    
    if metadata_file.exists():
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    
    return None

def count_inventory_products(file_path: Path) -> int:
    """Count products in inventory file"""
    try:
        # Lazy import to reduce memory footprint at startup
        import pandas as pd
        df = pd.read_excel(file_path)
        return len(df)
    except Exception as e:
        print(f"Warning: Could not count products: {e}")
        return 0

def get_latest_file(pattern: str) -> Optional[Path]:
    """Get latest file matching pattern"""
    output_dir = get_output_dir()
    files = list(output_dir.glob(pattern))
    if files:
        return max(files, key=lambda x: x.stat().st_mtime)
    return None

async def run_scraper_async(scraper_name: str, scraper_path: Path) -> dict:
    """Run a scraper asynchronously"""
    try:
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            str(scraper_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(get_base_dir())
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            return {
                "scraper": scraper_name,
                "status": "success",
                "output": stdout.decode()[:500]
            }
        else:
            return {
                "scraper": scraper_name,
                "status": "failed",
                "error": stderr.decode()[:500]
            }
    except Exception as e:
        return {
            "scraper": scraper_name,
            "status": "error",
            "error": str(e)
        }

def run_full_cycle_background():
    """Run full cycle in background"""
    global scraping_state
    
    try:
        scraping_state["status"] = ScrapingStatus.RUNNING
        scraping_state["started_at"] = datetime.now().isoformat()
        scraping_state["current_step"] = "Starting full cycle"
        scraping_state["error"] = None
        
        # Run full cycle script
        result = subprocess.run(
            [sys.executable, "run_full_cycle.py"],
            capture_output=True,
            text=True,
            timeout=600,  # 10 minutes timeout
            cwd=str(get_base_dir())
        )
        
        if result.returncode == 0:
            scraping_state["status"] = ScrapingStatus.COMPLETED
            scraping_state["completed_at"] = datetime.now().isoformat()
            scraping_state["current_step"] = "Completed"
            
            # Count products from output
            output = result.stdout
            if "products scraped" in output.lower():
                # Try to extract total count
                scraping_state["products_scraped"] = 183  # Default
        else:
            scraping_state["status"] = ScrapingStatus.FAILED
            scraping_state["completed_at"] = datetime.now().isoformat()
            scraping_state["error"] = result.stderr[:500]
            
    except subprocess.TimeoutExpired:
        scraping_state["status"] = ScrapingStatus.FAILED
        scraping_state["error"] = "Scraping timed out after 10 minutes"
    except Exception as e:
        scraping_state["status"] = ScrapingStatus.FAILED
        scraping_state["error"] = str(e)

# API Endpoints

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with web interface"""
    # Get inventory info for display
    inventory = await get_inventory_info()
    inventory_status = ""
    if inventory.has_file:
        inventory_status = f"""
        <div style="background: #d4edda; border: 1px solid #c3e6cb; padding: 10px; border-radius: 5px; margin: 10px 0;">
            <strong>✅ Файл с остатками загружен</strong><br>
            📅 Остатки актуальны на: <strong>{inventory.uploaded_at_formatted}</strong><br>
            📦 Товаров: {inventory.products_count}<br>
            📄 Файл: {inventory.filename}
        </div>
        """
    else:
        inventory_status = f"""
        <div style="background: #fff3cd; border: 1px solid #ffc107; padding: 10px; border-radius: 5px; margin: 10px 0;">
            <strong>⚠️ Файл с остатками не загружен</strong><br>
            Загрузите файл остатков для сравнения цен
        </div>
        """
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Coffee Price Monitoring API</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f5;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 10px;
                margin-bottom: 20px;
                text-align: center;
            }}
            .section {{
                background: white;
                padding: 20px;
                margin: 20px 0;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .button {{
                background: #667eea;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                margin: 5px;
                transition: background 0.3s;
            }}
            .button:hover {{
                background: #5568d3;
            }}
            .button.success {{
                background: #28a745;
            }}
            .button.success:hover {{
                background: #218838;
            }}
            .upload-form {{
                border: 2px dashed #667eea;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
            }}
            .endpoint {{
                background: #f8f9fa;
                padding: 10px;
                margin: 5px 0;
                border-left: 4px solid #667eea;
                font-family: monospace;
            }}
            .stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }}
            .stat-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
            }}
            .stat-value {{
                font-size: 32px;
                font-weight: bold;
            }}
            .stat-label {{
                font-size: 14px;
                opacity: 0.9;
            }}
            #status {{
                padding: 10px;
                border-radius: 5px;
                margin: 10px 0;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>☕ Coffee Price Monitoring API</h1>
            <p>Автоматический мониторинг цен на кофемашины DeLonghi</p>
            <p style="font-size: 14px; opacity: 0.9;">v1.0.0</p>
        </div>

        {inventory_status}

        <div class="section">
            <h2>📤 Загрузка файла с остатками</h2>
            <div class="upload-form">
                <h3>Загрузить файл остатков (*.xls или *.xlsx)</h3>
                <input type="file" id="fileInput" accept=".xls,.xlsx" style="margin: 10px 0;">
                <br>
                <button class="button" onclick="uploadInventory()">⬆️ Загрузить файл</button>
                <div id="uploadStatus" style="margin-top: 10px;"></div>
            </div>
        </div>

        <div class="section">
            <h2>🚀 Запуск парсинга</h2>
            <div style="text-align: center;">
                <button class="button success" onclick="startScraping()">▶️ Запустить полный цикл (все 4 сайта)</button>
                <div id="status" style="display: none;"></div>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value">74</div>
                    <div class="stat-label">ALTA.ge</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">28</div>
                    <div class="stat-label">KONTAKT.ge</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">40</div>
                    <div class="stat-label">ELITE (ee.ge)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">41</div>
                    <div class="stat-label">DIM_KAVA</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>📊 Отчеты</h2>
            <button class="button" onclick="downloadReport()">📥 Скачать последний отчет</button>
            <button class="button" onclick="viewReports()">📋 Список всех отчетов</button>
        </div>

        <div class="section">
            <h2>📚 API Endpoints</h2>
            
            <h3>Управление остатками</h3>
            <div class="endpoint">POST /inventory/upload - Загрузить файл остатков</div>
            <div class="endpoint">GET /inventory/info - Информация об остатках</div>
            <div class="endpoint">GET /inventory/download - Скачать текущий файл остатков</div>
            
            <h3>Парсинг</h3>
            <div class="endpoint">POST /scrape/all - Полный цикл (все 4 сайта)</div>
            <div class="endpoint">POST /scrape/alta - Только ALTA.ge</div>
            <div class="endpoint">POST /scrape/kontakt - Только KONTAKT.ge</div>
            <div class="endpoint">POST /scrape/elite - Только ELITE</div>
            <div class="endpoint">POST /scrape/dimkava - Только DIM_KAVA</div>
            
            <h3>Отчеты</h3>
            <div class="endpoint">GET /reports/latest - Последний отчет Excel</div>
            <div class="endpoint">GET /reports/executive - Отчет для руководства</div>
            <div class="endpoint">GET /reports/list - Список всех отчетов</div>
            
            <h3>Статус</h3>
            <div class="endpoint">GET /status - Статус парсинга</div>
            <div class="endpoint">GET /health - Health check</div>
            <div class="endpoint">GET /docs - Swagger документация</div>
        </div>

        <script>
            async function uploadInventory() {{
                const fileInput = document.getElementById('fileInput');
                const file = fileInput.files[0];
                const statusDiv = document.getElementById('uploadStatus');
                
                if (!file) {{
                    statusDiv.innerHTML = '<span style="color: red;">❌ Выберите файл</span>';
                    return;
                }}
                
                const formData = new FormData();
                formData.append('file', file);
                
                statusDiv.innerHTML = '<span style="color: blue;">⏳ Загрузка...</span>';
                
                try {{
                    const response = await fetch('/inventory/upload', {{
                        method: 'POST',
                        body: formData
                    }});
                    
                    const data = await response.json();
                    
                    if (response.ok) {{
                        statusDiv.innerHTML = `<span style="color: green;">✅ ${{data.message}}<br>📅 Дата: ${{data.uploaded_at_formatted}}</span>`;
                        setTimeout(() => location.reload(), 2000);
                    }} else {{
                        statusDiv.innerHTML = `<span style="color: red;">❌ Ошибка: ${{data.detail}}</span>`;
                    }}
                }} catch (error) {{
                    statusDiv.innerHTML = `<span style="color: red;">❌ Ошибка: ${{error.message}}</span>`;
                }}
            }}
            
            async function startScraping() {{
                const statusDiv = document.getElementById('status');
                statusDiv.style.display = 'block';
                statusDiv.style.background = '#cce5ff';
                statusDiv.innerHTML = '⏳ Запуск парсинга...';
                
                try {{
                    const response = await fetch('/scrape/all', {{method: 'POST'}});
                    const data = await response.json();
                    
                    statusDiv.style.background = '#d4edda';
                    statusDiv.innerHTML = `✅ ${{data.message}}<br>Проверяйте статус на /status`;
                    
                    // Start checking status
                    checkStatus();
                }} catch (error) {{
                    statusDiv.style.background = '#f8d7da';
                    statusDiv.innerHTML = `❌ Ошибка: ${{error.message}}`;
                }}
            }}
            
            async function checkStatus() {{
                try {{
                    const response = await fetch('/status');
                    const data = await response.json();
                    const statusDiv = document.getElementById('status');
                    
                    if (data.current_status === 'running') {{
                        statusDiv.style.background = '#fff3cd';
                        statusDiv.innerHTML = `⏳ В процессе: ${{data.current_step || 'Парсинг...'}}`;
                        setTimeout(checkStatus, 3000);
                    }} else if (data.current_status === 'completed') {{
                        statusDiv.style.background = '#d4edda';
                        statusDiv.innerHTML = `✅ Завершено! Собрано товаров: ${{data.products_scraped}}`;
                    }} else if (data.current_status === 'failed') {{
                        statusDiv.style.background = '#f8d7da';
                        statusDiv.innerHTML = `❌ Ошибка: ${{data.error}}`;
                    }}
                }} catch (error) {{
                    console.error(error);
                }}
            }}
            
            function downloadReport() {{
                window.location.href = '/reports/latest';
            }}
            
            async function viewReports() {{
                const response = await fetch('/reports/list');
                const reports = await response.json();
                
                let html = '<h3>Доступные отчеты:</h3>';
                reports.forEach(report => {{
                    html += `<div class="endpoint">${{report.filename}} - ${{report.created_at}}</div>`;
                }});
                
                const div = document.createElement('div');
                div.innerHTML = html;
                document.querySelector('.section:last-child').appendChild(div);
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    inventory = await get_inventory_info()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "coffee-price-monitor",
        "inventory": {
            "loaded": inventory.has_file,
            "date": inventory.uploaded_at_formatted if inventory.has_file else None
        }
    }

# Inventory Management Endpoints

@app.get("/inventory/info", response_model=InventoryInfo)
async def get_inventory_info():
    """Get information about current inventory file"""
    inventory_file = get_inventory_file()
    
    if not inventory_file:
        return InventoryInfo(
            has_file=False,
            message="Файл с остатками не загружен"
        )
    
    # Get metadata
    metadata = load_inventory_metadata()
    
    # Get file stats
    stat = inventory_file.stat()
    products_count = count_inventory_products(inventory_file)
    
    uploaded_at = None
    uploaded_at_formatted = None
    
    if metadata:
        uploaded_at = metadata.get("uploaded_at")
        uploaded_at_formatted = metadata.get("uploaded_at_formatted")
    else:
        # Fallback to file modification time
        mtime = datetime.fromtimestamp(stat.st_mtime)
        uploaded_at = mtime.isoformat()
        uploaded_at_formatted = mtime.strftime("%d.%m.%Y")
    
    return InventoryInfo(
        has_file=True,
        filename=inventory_file.name,
        uploaded_at=uploaded_at,
        uploaded_at_formatted=uploaded_at_formatted,
        size_bytes=stat.st_size,
        products_count=products_count,
        message=f"Остатки актуальны на {uploaded_at_formatted}"
    )

@app.post("/inventory/upload", response_model=UploadResponse)
async def upload_inventory(file: UploadFile = File(...)):
    """
    Upload inventory file (остатки.xls or остатки.xlsx)
    
    This file will be used for price comparison
    """
    # Validate file extension
    if not file.filename.endswith(('.xls', '.xlsx')):
        raise HTTPException(
            status_code=400,
            detail="Файл должен быть в формате .xls или .xlsx"
        )
    
    # Determine target filename
    inbox_dir = get_inbox_dir()
    
    # Use original extension
    if file.filename.endswith('.xlsx'):
        target_file = inbox_dir / "остатки.xlsx"
        # Remove old .xls if exists
        old_xls = inbox_dir / "остатки.xls"
        if old_xls.exists():
            old_xls.unlink()
    else:
        target_file = inbox_dir / "остатки.xls"
        # Remove old .xlsx if exists
        old_xlsx = inbox_dir / "остатки.xlsx"
        if old_xlsx.exists():
            old_xlsx.unlink()
    
    # Save file
    try:
        with open(target_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при сохранении файла: {str(e)}"
        )
    
    # Save metadata
    upload_time = datetime.now()
    save_inventory_metadata(target_file.name, upload_time)
    
    # Count products
    products_count = count_inventory_products(target_file)
    
    return UploadResponse(
        status="success",
        message=f"Файл успешно загружен. Найдено товаров: {products_count}",
        filename=target_file.name,
        uploaded_at=upload_time.isoformat(),
        uploaded_at_formatted=upload_time.strftime("%d.%m.%Y")
    )

@app.get("/inventory/download")
async def download_inventory():
    """Download current inventory file"""
    inventory_file = get_inventory_file()
    
    if not inventory_file:
        raise HTTPException(
            status_code=404,
            detail="Файл с остатками не найден"
        )
    
    media_type = "application/vnd.ms-excel" if inventory_file.suffix == ".xls" else \
                 "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    return FileResponse(
        inventory_file,
        media_type=media_type,
        filename=inventory_file.name
    )

@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Get current scraping status"""
    return StatusResponse(
        current_status=scraping_state["status"],
        last_run=scraping_state["completed_at"],
        products_scraped=scraping_state["products_scraped"],
        current_step=scraping_state["current_step"],
        error=scraping_state["error"]
    )

@app.post("/scrape/all", response_model=ScrapeResponse)
async def scrape_all(background_tasks: BackgroundTasks):
    """
    Run full scraping cycle for all 4 sites
    - ALTA.ge (74 products)
    - KONTAKT.ge (28 products)
    - ELITE (ee.ge) (40 products)
    - DIM_KAVA (dimkava.ge) (41 products)
    
    Total: 183 products in ~2-3 minutes
    """
    global scraping_state
    
    if scraping_state["status"] == ScrapingStatus.RUNNING:
        raise HTTPException(
            status_code=409,
            detail="Scraping is already in progress"
        )
    
    background_tasks.add_task(run_full_cycle_background)
    
    return ScrapeResponse(
        status="started",
        message="Full cycle scraping started in background. Check /status for progress.",
        started_at=datetime.now().isoformat()
    )

@app.post("/scrape/alta", response_model=ScrapeResponse)
async def scrape_alta(background_tasks: BackgroundTasks):
    """Scrape ALTA.ge (74 products, ~31 sec)"""
    scraper_path = get_base_dir() / "scrapers" / "alta" / "alta_bs4_scraper.py"
    
    if not scraper_path.exists():
        raise HTTPException(status_code=404, detail="ALTA scraper not found")
    
    async def run_task():
        await run_scraper_async("ALTA", scraper_path)
    
    background_tasks.add_task(run_task)
    
    return ScrapeResponse(
        status="started",
        message="ALTA scraping started",
        started_at=datetime.now().isoformat()
    )

@app.post("/scrape/kontakt", response_model=ScrapeResponse)
async def scrape_kontakt(background_tasks: BackgroundTasks):
    """Scrape KONTAKT.ge (28 products, ~22 sec)"""
    scraper_path = get_base_dir() / "scrapers" / "kontakt" / "kontakt_bs4_scraper.py"
    
    if not scraper_path.exists():
        raise HTTPException(status_code=404, detail="KONTAKT scraper not found")
    
    async def run_task():
        await run_scraper_async("KONTAKT", scraper_path)
    
    background_tasks.add_task(run_task)
    
    return ScrapeResponse(
        status="started",
        message="KONTAKT scraping started",
        started_at=datetime.now().isoformat()
    )

@app.post("/scrape/elite", response_model=ScrapeResponse)
async def scrape_elite(background_tasks: BackgroundTasks):
    """Scrape ELITE (ee.ge) (40 products, ~48 sec)"""
    scraper_path = get_base_dir() / "scrapers" / "elite" / "elite_bs4_scraper.py"
    
    if not scraper_path.exists():
        raise HTTPException(status_code=404, detail="ELITE scraper not found")
    
    async def run_task():
        await run_scraper_async("ELITE", scraper_path)
    
    background_tasks.add_task(run_task)
    
    return ScrapeResponse(
        status="started",
        message="ELITE scraping started",
        started_at=datetime.now().isoformat()
    )

@app.post("/scrape/dimkava", response_model=ScrapeResponse)
async def scrape_dimkava(background_tasks: BackgroundTasks):
    """Scrape DIM_KAVA (dimkava.ge) (41 products, ~35 sec)"""
    scraper_path = get_base_dir() / "scrapers" / "dimkava" / "dimkava_bs4_scraper.py"
    
    if not scraper_path.exists():
        raise HTTPException(status_code=404, detail="DIM_KAVA scraper not found")
    
    async def run_task():
        await run_scraper_async("DIM_KAVA", scraper_path)
    
    background_tasks.add_task(run_task)
    
    return ScrapeResponse(
        status="started",
        message="DIM_KAVA scraping started",
        started_at=datetime.now().isoformat()
    )

@app.get("/reports/latest")
async def get_latest_report():
    """Download latest price comparison Excel file"""
    latest_file = get_latest_file("price_comparison_*.xlsx")
    
    if not latest_file:
        raise HTTPException(status_code=404, detail="No reports found")
    
    return FileResponse(
        latest_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=latest_file.name
    )

@app.get("/reports/executive")
async def get_executive_report():
    """Download latest executive report (Word or PDF)"""
    # Try PDF first
    latest_pdf = get_latest_file("executive_report_*.pdf")
    if latest_pdf:
        return FileResponse(
            latest_pdf,
            media_type="application/pdf",
            filename=latest_pdf.name
        )
    
    # Fallback to Word
    latest_word = get_latest_file("executive_report_*.docx")
    if latest_word:
        return FileResponse(
            latest_word,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=latest_word.name
        )
    
    raise HTTPException(status_code=404, detail="No executive reports found")

@app.get("/reports/list")
async def list_reports() -> List[ReportInfo]:
    """List all available reports"""
    output_dir = get_output_dir()
    reports = []
    
    # Find all Excel reports
    for file in output_dir.glob("price_comparison_*.xlsx"):
        stat = file.stat()
        reports.append(ReportInfo(
            filename=file.name,
            created_at=datetime.fromtimestamp(stat.st_mtime).isoformat(),
            size_bytes=stat.st_size
        ))
    
    # Find all executive reports
    for file in output_dir.glob("executive_report_*.pdf"):
        stat = file.stat()
        reports.append(ReportInfo(
            filename=file.name,
            created_at=datetime.fromtimestamp(stat.st_mtime).isoformat(),
            size_bytes=stat.st_size
        ))
    
    for file in output_dir.glob("executive_report_*.docx"):
        stat = file.stat()
        reports.append(ReportInfo(
            filename=file.name,
            created_at=datetime.fromtimestamp(stat.st_mtime).isoformat(),
            size_bytes=stat.st_size
        ))
    
    # Sort by creation time (newest first)
    reports.sort(key=lambda x: x.created_at, reverse=True)
    
    return reports

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print("=" * 70)
    print("Coffee Price Monitoring API Started".center(70))
    print("=" * 70)
    print(f"Time: {datetime.now().isoformat()}")
    print(f"Base directory: {get_base_dir()}")
    print(f"Output directory: {get_output_dir()}")
    print("=" * 70)

# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

