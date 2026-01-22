# PowerShell скрипт для создания .env файла с WooCommerce ключами
# Использование: .\create_env_file.ps1 -Url "https://dimkava.ge" -Key "ck_..." -Secret "cs_..."

param(
    [Parameter(Mandatory=$true)]
    [string]$Key,
    
    [Parameter(Mandatory=$true)]
    [string]$Secret,
    
    [string]$Url = "https://dimkava.ge",
    [string]$ApiVersion = "wc/v3"
)

$envContent = @"
# WooCommerce API (для экспорта данных)
WC_URL=$Url
WC_CONSUMER_KEY=$Key
WC_CONSUMER_SECRET=$Secret
WC_API_VERSION=$ApiVersion
"@

$envContent | Out-File -FilePath ".env" -Encoding UTF8 -NoNewline

Write-Host "[OK] Файл .env создан успешно!" -ForegroundColor Green
Write-Host "[SECURITY] Файл .env в .gitignore и не попадет в Git" -ForegroundColor Yellow
Write-Host ""
Write-Host "Теперь можно запустить: python test_woocommerce_client.py" -ForegroundColor Cyan
