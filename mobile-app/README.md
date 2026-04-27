# LyfeSync Mobile (Capacitor)

Este app mobile usa o site responsivo do projeto Django dentro de um container nativo.

## Estrutura

- `android/`: projeto Android Studio
- `ios/`: projeto Xcode
- `capacitor.config.json`: configuracao do app
- `www/index.html`: fallback da camada web

## Configuracao atual

O app esta apontando para:

- `http://10.0.2.2:8000`

Esse endereco funciona no emulador Android para acessar o servidor Django rodando no host.

## Como executar

1. Inicie o Django no projeto raiz:

```bash
py manage.py runserver 0.0.0.0:8000
```

2. Na pasta `mobile-app`, sincronize:

```bash
npm run sync
```

3. Abra no Android Studio:

```bash
npm run open:android
```

4. Rode no emulador/dispositivo pelo Android Studio.

## APK de teste assinado (Android)

Ja deixamos o projeto com assinatura release configurada:

- `android/keystore/lyfesync-upload-key.jks`
- `android/keystore.properties`
- `android/app/build.gradle` com `signingConfigs.release`

Se o build reclamar de SDK ausente, crie `android/local.properties` com:

```properties
sdk.dir=C:\\Users\\SEU_USUARIO\\AppData\\Local\\Android\\Sdk
```

Depois gere o APK:

```bash
cd android
gradlew.bat assembleRelease
```

Saida esperada:

- `android/app/build/outputs/apk/release/app-release.apk`

## iOS

- O projeto iOS foi criado e sincronizado.
- A build final iOS exige macOS + Xcode + CocoaPods.
- Para simulador iOS, normalmente a URL precisa ser ajustada para `http://localhost:8000` no `capacitor.config.json`.
