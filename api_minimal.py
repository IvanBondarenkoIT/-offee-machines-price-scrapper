"""
Minimal FastAPI app for Railway testing
Just displays "Hello World" to verify deployment works
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def root():
    """Simple HTML page to verify Railway deployment"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Railway Test</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            .container {
                text-align: center;
                background: white;
                padding: 50px;
                border-radius: 20px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            }
            h1 {
                color: #667eea;
                font-size: 48px;
                margin: 0;
            }
            p {
                color: #666;
                font-size: 20px;
            }
            .status {
                color: #28a745;
                font-weight: bold;
                font-size: 24px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✅ Railway Works!</h1>
            <p class="status">Deployment Successful</p>
            <p>Coffee Price Monitor API</p>
            <p style="font-size: 14px; color: #999;">
                FastAPI на Railway.com<br>
                Всё работает нормально! 🎉
            </p>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy", "message": "Railway deployment works!"}

@app.get("/test")
async def test():
    """Test endpoint"""
    return {
        "status": "ok",
        "service": "coffee-price-monitor-minimal",
        "message": "Минимальное приложение работает!"
    }

# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

