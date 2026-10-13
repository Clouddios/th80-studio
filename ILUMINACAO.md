# Iluminação do TH80 Pro V2

O controle usa o bloco nativo de 48 bytes. Neste teclado, as consultas de iluminação VIA apenas repetiram o pedido. Os projetos de GMK87 fornecem uma referência útil para o protocolo nativo, mas os recursos e nomes de efeitos desse modelo não comprovam suporte no TH80.

| Byte, contado a partir de zero | Uso | Evidência no TH80 |
| --- | --- | --- |
| 1 | ID do efeito | IDs 1, 3, 13 e 16 capturados; alterações confirmadas |
| 2 | Brilho de 0 a 9 | Capturas, escrita e confirmação visual |
| 3 | Velocidade | Níveis 2 e 4 capturados; alterações confirmadas |
| 5 | Modo de cor | 0 para RGB; 255 em um estado arco-íris capturado |
| 6, 7, 8 | Vermelho, verde, azul, cada um de 0 a 255 | Mudança #68FF00 → #35FF00 confirmada visualmente |
| 9 | Campo auxiliar de cor | Muda junto dos atalhos; significado ainda não decodificado |

## Cor personalizada

HEX é uma representação dos três canais RGB: #0066FF significa R=0, G=102, B=255. A roda usa HSV para a seleção visual e converte o resultado para RGB. Seu controle de luminosidade modifica a cor, enquanto o brilho da aba principal controla a iluminação do teclado.

Escolher uma cor na roda não envia dados. Clique em Usar cor e depois em Aplicar iluminação. O app lê a configuração atual, salva uma cópia, muda o byte 5 para zero e os bytes 6–8 para a cor escolhida. Preserva o byte 9 e os demais ajustes, e exige leitura final correspondente. O funcionamento visual de RGB arbitrário ainda precisa de teste físico neste TH80; alguns efeitos podem ignorar a cor escolhida.

## Catálogo aprendido

As capturas anteriores são importadas para catalogo-iluminacao.json ao abrir o app. Adicionar estado atual lê o teclado, sem gravar nele, e registra o efeito, velocidade e bloco de cor observado. Para ampliar a lista, mude somente o efeito ou a velocidade com os atalhos físicos e adicione o estado. Uma captura comprova que o estado foi observado; reproduzi-lo ainda requer confirmação visual.

As cores capturadas reproduzem os cinco bytes 5–9 originais. Uma cor personalizada preserva o campo auxiliar 9. O catálogo atual reúne quatro efeitos, dois níveis de velocidade e dez estados de cor; três estados de cor já foram confirmados visualmente pelo usuário.

## Referências e limites

- [gmk87-node, código do protocolo](https://github.com/codedgar/gmk87-node/blob/main/src/lib/device.js): interpreta os mesmos offsets e modifica uma cópia da configuração atual. O construtor RGB preserva o byte 9.
- [Documentação de iluminação](https://codedgar.github.io/gmk87-node/how-to/configure-lighting/): documenta RGB, brilho 0–9, velocidade 0–9 e 19 efeitos para GMK87. A ordem de velocidade nesse modelo é 0 mais rápido e 9 mais lento; não foi confirmada em toda a faixa do TH80.
- [Lista de efeitos GMK87](https://codedgar.github.io/gmk87-node/how-to/lighting-presets/): IDs 0–18, incluindo cor fixa, respiração, ondas e efeitos reativos. Os nomes não são usados como nomes confirmados no TH80.
- [GMK87-Tool](https://github.com/pihomeserver/GMK87-Tool): outra implementação do controle RGB e dos efeitos pelo HID.
- [gmk87-usb-reverse](https://github.com/ikkentim/gmk87-usb-reverse): referência de engenharia reversa do protocolo.

Não existe evidência de que isso seja um padrão universal de teclados. É uma família de protocolo HID proprietário com semelhanças entre esses dispositivos. LEDs auxiliares, direção de efeito e todos os IDs do GMK87 não estão habilitados neste app sem validação no TH80.
