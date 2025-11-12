# Move-Templates-Final.ps1
# Script para mover os templates restantes (com nomes em CamelCase/mixed)
# Assume que a pasta 'templates/app_LyfeSync' existe.

$TemplateDir = "app_LyfeSync"
$BasePath = "templates/$TemplateDir"

Write-Host "Verificando e Movendo arquivos restantes para as pastas corretas..."

# Cria a pasta 'layouts' caso não tenha sido criada antes
New-Item -Path "$BasePath/layouts" -ItemType Directory -Force | Out-Null

# Mapeamento: 'Nome do Arquivo Restante' = 'Nome da Pasta Destino'
$MoveMap = @{
    # Afirmação
    "alterarAfirmacao.html" = "afirmacao"
    "registrarAfirmacao.html" = "afirmacao"

    # Gratidão
    "alterarGratidao.html" = "gratidao"
    "registrarGratidao.html" = "gratidao"

    # Humor (inclui Dicas)
    "alterarHumor.html" = "humor"
    "registrarHumor.html" = "humor"
    "dicas.html" = "humor" # Conforme solicitado

    # Hábitos
    "alterarHabito.html" = "habitos"
    "registrarHabito.html" = "habitos"

    # Dashboard/Públicas
    "homeLyfesync.html" = "dashboard"
    "logout.html" = "public"
    "sobreNos.html" = "public"

    # Relatórios
    "relatorioAfirmacao.html" = "relatorios"
    "relatorioGratidao.html" = "relatorios"
    "relatorioHumor.html" = "relatorios"
    "relatorioHabito.html" = "relatorios"
}

foreach ($File in $MoveMap.Keys) {
    $SourcePath = "$BasePath/$File"
    $DestinationPath = "$BasePath/$($MoveMap[$File])/$File"
    
    if (Test-Path $SourcePath) {
        # O comando Move-Item no PowerShell
        Move-Item -Path $SourcePath -Destination $DestinationPath -Force
        Write-Host "✅ Movido $File para $($MoveMap[$File])/" -ForegroundColor Green
    } else {
        # Esta é uma mensagem informativa. O arquivo pode ter sido movido antes.
        Write-Host "AVISO: Arquivo $File não encontrado em $BasePath. Pulando." -ForegroundColor Yellow
    }
}

Write-Host "--- Movimentação de Templates COMPLEMENTAR CONCLUÍDA ---"