# TH80 Studio 🎹

**Seu teclado, sua foto, suas teclas, suas cores.**

Configurador desktop de código aberto para o **EPOMAKER TH80 Pro V2**, com conexão USB e interface em português, grafite e azul. Envie imagens e GIFs, acerte o relógio, remapeie teclas e controle a iluminação sem depender do Image Custom Tool.

![Exemplo de GIF para a tela do teclado](assets/clawd-typing.gif)

> Projeto independente, sem vínculo com a EPOMAKER. Validado em um TH80 Pro V2 no Windows. macOS e Linux ainda não foram validados no hardware.

## O que dá para fazer

| Aba | Recursos |
| --- | --- |
| Tela e GIF | Prévia, ajuste para 240 × 135 e envio de imagens ou animações |
| Relógio | Sincronizar data e hora do computador; voltar à imagem salva |
| Teclas | Ler quatro camadas, editar uma das 79 teclas e desfazer a última alteração |
| Iluminação | Brilho 0–9, efeitos e velocidades observados, estados de cor, roda de cores e HEX |
| Manual | Guia em português, atalhos físicos e acesso ao manual oficial |

## Instalação no Windows

Você precisa de **Python 3.12 com Tcl/Tk**, instalado pelo [site oficial do Python](https://www.python.org/downloads/windows/), e do teclado conectado por USB.

1. Baixe o projeto em **Code → Download ZIP** ou clone:

   ```powershell
   git clone https://github.com/Clouddios/th80-studio.git
   cd th80-studio
   ```

2. Dê dois cliques em **Instalar.cmd**. Ele cria um ambiente `.venv` e instala Pillow e hidapi.
3. Abra **Abrir.cmd**.
4. Deixe o seletor do teclado no meio, conecte o cabo USB e feche outros configuradores, incluindo VIA.
5. Clique em **Conectar teclado**.

Também é possível instalar manualmente, sem ativar o ambiente no PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

O projeto não usa caminhos particulares nem exige Codex instalado. Esta versão é executada pelo Python; ainda não há instalador `.exe` assinado.

## Foto e GIF

Abra **Tela e GIF**, escolha o arquivo, confira a prévia e envie. O exemplo [clawd-typing.gif](assets/clawd-typing.gif) já está no formato da tela.

- Resolução: **240 × 135 pixels**.
- Imagens recebem recorte central; transparência é composta sobre preto.
- GIFs são adaptados para **até 18 quadros por posição**, com duração uniforme de pelo menos 60 ms. É um limite conservador do app, não a capacidade máxima comprovada do dispositivo.
- O envio substitui **as duas posições de imagem**. O app salva a configuração anterior, mas **não copia as imagens antigas**.
- Mantenha o cabo conectado até terminar.

## Relógio e teclas

Em **Relógio**, envie a hora local do computador. A prévia do app mostra o relógio do computador; não faz leitura contínua do horário do teclado.

Em **Teclas**, leia a camada antes de editar. Clique na tecla, escolha a função e aplique. O app confere o valor atual, salva o anterior e verifica a gravação por leitura. **Desfazer última alteração** restaura apenas a última tecla, se ela ainda tiver o valor aplicado pelo app.

Letras, números, F1–F12, navegação e modificadores estão disponíveis. Macros e atalhos compostos ainda não têm editor.

## Iluminação e cores HEX

1. Clique em **Verificar iluminação**.
2. Ajuste o brilho e escolha efeito, velocidade ou cor. **Manter atual** preserva aquele ajuste.
3. Para RGB livre, abra **Roda de cores / HEX**, escolha na roda ou digite um código como `#0066FF`.
4. Clique em **Usar cor** e depois em **Aplicar iluminação**. Selecionar na roda não envia dados automaticamente.

A cor pode depender do efeito ativo. Brilho, alterações de efeito e velocidade, e três estados de cor foram confirmados no teclado físico. RGB arbitrário tem testes automatizados e verificação de leitura; sua aparência ainda precisa de confirmação física.

O catálogo começa com os estados conhecidos. Para ampliá-lo, mude o efeito ou a velocidade pelos atalhos físicos e clique em **Adicionar estado atual**. Esse botão **só lê** o teclado. As capturas locais são importadas ao abrir o app.

Leia [ILUMINACAO.md](ILUMINACAO.md) para os offsets do protocolo e a diferença entre o que foi observado no TH80 e o que é referência de outros teclados.

## Atalhos do teclado

| Atalho | Ação padrão no manual do TH80 Pro V2 |
| --- | --- |
| Fn + Backspace | Ligar/desligar iluminação |
| Fn + `\` | Alternar efeitos RGB |
| Fn + ↑ / ↓ | Ajustar brilho |
| Fn + → / ← | Ajustar matiz |
| Fn + = / - | Ajustar velocidade |
| Fn + [ / ] | Ajustar saturação |
| Fn + Enter | Alternar conteúdo da tela |
| Fn + X | Ligar/desligar tela |
| Fn + A / S | Modo Windows / Mac |

Fonte: [manual oficial da EPOMAKER](https://epomaker.com/blogs/manuals/th80-pro-v2-manual). Remapeamentos podem alterar o comportamento dos atalhos.

## Compatibilidade e diagnóstico

O app seleciona o produto **EPOMAKER TH80 Pro V2**, VID `320F`, PID `5055`, com interfaces HID específicas. IDs parecidos em outro modelo não garantem compatibilidade. Conecte apenas um teclado desse modelo por vez.

Se o teclado não aparecer, confira cabo, posição do seletor e feche outros configuradores. Bluetooth e receptor 2,4 GHz não são suportados nesta versão. O código evita comandos de reset, bootloader e firmware; não exige desativar proteções do Windows nem remover drivers.

Resultados e cópias de configuração são gravados localmente em `resultado-*.json`, `*-antes-*.json` e nas pastas `registros-*`. Eles são ignorados pelo Git. Não são enviados a um serviço de telemetria pelo app. Ao abrir uma issue, revise os registros antes de anexá-los.

## Desenvolvimento

```powershell
.\.venv\Scripts\python.exe -m unittest discover -p "test_*.py"
.\.venv\Scripts\python.exe app.py --check-ui
```

Os testes exercitam pacotes USB, transferências, animações, relógio, keymap VIA, preservação de configurações, catálogo e conversão de cores, substituindo a fronteira USB por dispositivos simulados. Eles não substituem a confirmação no teclado físico.

| Arquivo | Responsabilidade |
| --- | --- |
| `app.py`, `ui.py` | Operações e interface Tkinter |
| `protocol.py`, `transfer.py` | Pacotes nativos, confirmação e transferências |
| `via.py`, `keyboard_layout.py` | VIA e layout das teclas |
| `media.py` | Preparação de imagens e GIFs |
| `color_wheel.py`, `lighting_catalog.py` | Seleção RGB e catálogo observado |
| `manual.py` | Guia integrado |

Contribuições são bem-vindas: testes em mais unidades, mapeamento de efeitos, empacotamento para Windows e suporte validado a macOS/Linux. Informe modelo exato, sistema, passos e resultado esperado ao abrir uma issue.

## Créditos e licença

Código do projeto sob [licença MIT](LICENSE). Consulte [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) para as referências do protocolo e dependências.

Obrigado aos projetos [gmk87-node](https://github.com/codedgar/gmk87-node), [gmk87-usb-reverse](https://github.com/ikkentim/gmk87-usb-reverse), [GMK87-Tool](https://github.com/pihomeserver/GMK87-Tool) e [QMK](https://github.com/qmk/qmk_firmware). Recursos de outros modelos são referências, não suporte confirmado no TH80.
