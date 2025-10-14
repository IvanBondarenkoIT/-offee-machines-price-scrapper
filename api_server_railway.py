"""
FastAPI Web Server for Railway - Results Viewer Only
Displays and serves pre-generated reports (uploaded from local PC)
NO scraping, NO inventory upload - just static content serving
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from pathlib import Path
from datetime import datetime
import json
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Coffee Price Reports Viewer",
    description="View and download price monitoring reports",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
OUTPUT_DIR = Path("data/output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Models
class ReportInfo(BaseModel):
    filename: str
    date: str
    size_kb: int
    type: str  # "excel", "word", "pdf"

class SystemStatus(BaseModel):
    status: str
    total_reports: int
    latest_report: Optional[str]
    last_update: Optional[str]

# Helper functions
def get_latest_report(extension: str = "xlsx") -> Optional[Path]:
    """Get the most recent report file"""
    try:
        files = list(OUTPUT_DIR.glob(f"*.{extension}"))
        if not files:
            return None
        return max(files, key=lambda f: f.stat().st_mtime)
    except Exception as e:
        logger.error(f"Error finding latest report: {e}")
        return None

def list_all_reports() -> List[ReportInfo]:
    """List all available reports"""
    reports = []
    try:
        for ext, file_type in [("xlsx", "excel"), ("docx", "word"), ("pdf", "pdf")]:
            for file_path in OUTPUT_DIR.glob(f"*.{ext}"):
                reports.append(ReportInfo(
                    filename=file_path.name,
                    date=datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                    size_kb=file_path.stat().st_size // 1024,
                    type=file_type
                ))
        
        # Sort by date, newest first
        reports.sort(key=lambda r: r.date, reverse=True)
    except Exception as e:
        logger.error(f"Error listing reports: {e}")
    
    return reports

# API Endpoints

@app.get("/", response_class=HTMLResponse)
async def root():
    """Web interface - report viewer"""
    
    reports = list_all_reports()
    latest_excel = get_latest_report("xlsx")
    latest_word = get_latest_report("docx")
    latest_pdf = get_latest_report("pdf")
    
    reports_html = ""
    if reports:
        for report in reports[:10]:  # Show last 10 reports
            icon = "📊" if report.type == "excel" else "📄" if report.type == "word" else "📕"
            reports_html += f"""
            <div class="report-item">
                <span class="report-icon">{icon}</span>
                <div class="report-info">
                    <div class="report-name">{report.filename}</div>
                    <div class="report-meta">{report.date} • {report.size_kb} KB</div>
                </div>
                <a href="/reports/download/{report.filename}" class="download-btn">⬇ Скачать</a>
            </div>
            """
    else:
        reports_html = '<p style="text-align: center; color: #666;">Отчеты пока не загружены</p>'
    
    return f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Отчеты по ценам на кофемашины</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            
            .container {{
                max-width: 900px;
                margin: 0 auto;
            }}
            
            .header {{
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                margin-bottom: 30px;
                text-align: center;
            }}
            
            h1 {{
                color: #333;
                font-size: 2em;
                margin-bottom: 10px;
            }}
            
            .subtitle {{
                color: #666;
                font-size: 1.1em;
            }}
            
            .stats {{
                display: flex;
                gap: 15px;
                margin-bottom: 30px;
                flex-wrap: wrap;
            }}
            
            .stat-card {{
                flex: 1;
                min-width: 200px;
                background: white;
                padding: 20px;
                border-radius: 12px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }}
            
            .stat-label {{
                color: #666;
                font-size: 0.9em;
                margin-bottom: 8px;
            }}
            
            .stat-value {{
                color: #333;
                font-size: 1.8em;
                font-weight: bold;
            }}
            
            .reports-section {{
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }}
            
            .section-title {{
                color: #333;
                font-size: 1.5em;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 2px solid #eee;
            }}
            
            .report-item {{
                display: flex;
                align-items: center;
                padding: 15px;
                border: 1px solid #eee;
                border-radius: 8px;
                margin-bottom: 10px;
                transition: all 0.2s;
            }}
            
            .report-item:hover {{
                background: #f8f9fa;
                border-color: #667eea;
                transform: translateY(-2px);
                box-shadow: 0 3px 10px rgba(102, 126, 234, 0.2);
            }}
            
            .report-icon {{
                font-size: 2em;
                margin-right: 15px;
            }}
            
            .report-info {{
                flex: 1;
            }}
            
            .report-name {{
                color: #333;
                font-weight: 500;
                margin-bottom: 5px;
            }}
            
            .report-meta {{
                color: #999;
                font-size: 0.85em;
            }}
            
            .download-btn {{
                background: #667eea;
                color: white;
                padding: 8px 20px;
                border-radius: 6px;
                text-decoration: none;
                font-weight: 500;
                transition: all 0.2s;
            }}
            
            .download-btn:hover {{
                background: #764ba2;
                transform: scale(1.05);
            }}
            
            .quick-links {{
                margin-top: 20px;
                padding-top: 20px;
                border-top: 1px solid #eee;
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
            }}
            
            .quick-link {{
                background: #f8f9fa;
                color: #667eea;
                padding: 10px 20px;
                border-radius: 6px;
                text-decoration: none;
                font-weight: 500;
                transition: all 0.2s;
            }}
            
            .quick-link:hover {{
                background: #667eea;
                color: white;
            }}
            
            @media (max-width: 600px) {{
                .stats {{
                    flex-direction: column;
                }}
                
                .report-item {{
                    flex-direction: column;
                    text-align: center;
                }}
                
                .report-icon {{
                    margin: 0 0 10px 0;
                }}
                
                .download-btn {{
                    margin-top: 10px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 Отчеты по ценам</h1>
                <p class="subtitle">Мониторинг цен на кофемашины</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-label">Всего отчетов</div>
                    <div class="stat-value">{len(reports)}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Последний отчет</div>
                    <div class="stat-value">{reports[0].date.split()[0] if reports else "—"}</div>
                </div>
            </div>
            
            <div class="reports-section">
                <h2 class="section-title">Доступные отчеты</h2>
                {reports_html}
                
                <div class="quick-links">
                    <a href="/reports/latest/excel" class="quick-link">📊 Скачать последний Excel</a>
                    <a href="/reports/latest/word" class="quick-link">📄 Скачать последний Word</a>
                    <a href="/reports/latest/pdf" class="quick-link">📕 Скачать последний PDF</a>
                    <a href="/reports/list" class="quick-link">📋 API: Список отчетов</a>
                    <a href="/status" class="quick-link">🔄 API: Статус</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/status")
async def get_status():
    """Get system status"""
    reports = list_all_reports()
    latest = reports[0] if reports else None
    
    return SystemStatus(
        status="online",
        total_reports=len(reports),
        latest_report=latest.filename if latest else None,
        last_update=latest.date if latest else None
    )

@app.get("/reports/list")
async def list_reports():
    """List all available reports"""
    return {"reports": list_all_reports()}

@app.get("/reports/latest/{report_type}")
async def get_latest_report_endpoint(report_type: str):
    """Download the latest report of specified type"""
    
    extensions = {
        "excel": "xlsx",
        "word": "docx",
        "pdf": "pdf"
    }
    
    if report_type not in extensions:
        raise HTTPException(status_code=400, detail="Invalid report type. Use: excel, word, or pdf")
    
    logger.info(f"Getting latest {report_type} report...")
    latest_file = get_latest_report(extensions[report_type])
    logger.info(f"Found file: {latest_file}")
    
    if not latest_file or not latest_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"No {report_type} reports available yet. Reports are uploaded from local PC."
        )
    
    return FileResponse(
        str(latest_file),  # Convert Path to string for FileResponse
        media_type="application/octet-stream",
        filename=latest_file.name
    )

@app.get("/reports/download/{filename}")
async def download_report(filename: str):
    """Download a specific report by filename"""
    
    # Security: prevent directory traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    file_path = OUTPUT_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Report not found")
    
    return FileResponse(
        str(file_path),  # Convert Path to string for FileResponse
        media_type="application/octet-stream",
        filename=filename
    )

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    return {"status": "healthy", "service": "reports-viewer"}

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("=" * 60)
    logger.info("Railway Reports Viewer started!")
    logger.info("=" * 60)
    logger.info(f"Output directory: {OUTPUT_DIR.absolute()}")
    logger.info(f"Available reports: {len(list_all_reports())}")
    logger.info("=" * 60)

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

