# Move-Templates.ps1
# Script para criar as pastas de templates e mover os arquivos.

$TemplateDir = "app_LyfeSync"
$BasePath = "templates/$TemplateDir"

# --- 1. Criação das Pastas ---
Write-Host "Criando a estrutura de pastas em $BasePath..."

# Criar a pasta 'layouts' (sua base)
New-Item -Path "$BasePath/layouts" -ItemType Directory -Force | Out-Null

# Criar as demais pastas de templates
$Folders = @("public", "dashboard", "habitos", "autocuidado", "humor", "gratidao", "afirmacao", "relatorios", "conta")
foreach ($Folder in $Folders) {
    New-Item -Path "$BasePath/$Folder" -ItemType Directory -Force | Out-Null
}

Write-Host "Pastas criadas com sucesso."

# --- 2. Mapeamento e Movimentação dos Arquivos ---
Write-Host "Movendo arquivos para as novas pastas..."

# Mapeamento: 'Nome do Arquivo' = 'Nome da Pasta Destino'
$MoveMap = @{
    # layouts (Se base.html estiver no root)
    "base.html"           = "layouts"
    "sidebar.html"        = "layouts"
    "navbar.html"         = "layouts"

    # public
    "home.html"           = "public"
    "sobre_nos.html"      = "public"
    "contatos.html"       = "public"
    "login.html"          = "public"
    "cadastro.html"       = "public"

    # dashboard
    "home_lyfesync.html"  = "dashboard"

    # habitos
    "habito.html"         = "habitos"
    "registrar_habito.html" = "habitos"
    "alterar_habito.html" = "habitos"

    # autocuidado
    "autocuidado.html"    = "autocuidado"
    
    # humor
    "humor.html"          = "humor"
    "registrar_humor.html"= "humor"
    "alterar_humor.html"  = "humor"
    "load_humor_api.html" = "humor" # Exemplo de API/Snippet

    # gratidao
    "gratidao.html"       = "gratidao"
    "registrar_gratidao.html" = "gratidao"
    "alterar_gratidao.html" = "gratidao"

    # afirmacao
    "afirmacao.html"      = "afirmacao"
    "registrar_afirmacao.html" = "afirmacao"
    "alterar_afirmacao.html" = "afirmacao"

    # relatorios
    "relatorios.html"     = "relatorios"
    "relatorio_habito.html" = "relatorios"
    "relatorio_humor.html"  = "relatorios"
    
    # conta
    "conta.html"          = "conta"
    "configuracoes_conta.html" = "conta"
    "registrar_dica.html" = "conta"
}

foreach ($File in $MoveMap.Keys) {
    $SourcePath = "$BasePath/$File"
    $DestinationPath = "$BasePath/$($MoveMap[$File])/$File"
    
    if (Test-Path $SourcePath) {
        Move-Item -Path $SourcePath -Destination $DestinationPath -Force
        Write-Host "Movido $File para $($MoveMap[$File])/" -ForegroundColor Green
    } else {
        # Esta é uma mensagem informativa. O arquivo pode ter um nome ligeiramente diferente.
        Write-Host "AVISO: Arquivo $File não encontrado em $BasePath. Pulando." -ForegroundColor Yellow
    }
}

Write-Host "--- Movimentação de Templates CONCLUÍDA ---"