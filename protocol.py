"""Display protocol with TH80-confirmed configuration reads.

References: codedgar/gmk87-node and jeisinger/zuoya_gmk87.py.
The installed Image Custom Tool independently confirms report 4,
64-byte packets, the sum of bytes 3..63 and 24-bit offsets.
"""

def config_query(offset):
    if offset not in range(0,48,4):
        raise ValueError('Offset de configuração inválido.')
    packet=bytearray(64)
    packet[0]=4
    packet[3]=5  # Query only; no preparation, commit or configuration write.
    packet[4]=4
    packet[5:8]=offset.to_bytes(3,'little')
    packet[1:3]=sum(packet[3:]).to_bytes(2,'little')
    return bytes(packet)

def matches_response(query,response):
    return len(response)>=8 and response[:3]==query[:3] and response[3]==query[3]

def select_device(devices):
    matches=[d for d in devices if
        d.get('vendor_id')==0x320f and d.get('product_id')==0x5055
        and d.get('product_string')=='EPOMAKER TH80 Pro V2'
        and d.get('usage_page')==0xff1c and d.get('usage')==0x92]
    if len(matches)!=1:
        raise ValueError('Nenhuma interface da tela encontrada.' if not matches
                         else 'Mais de um TH80 encontrado. Conecte somente um para este teste.')
    return matches[0]

def packet(command, data=b'', position=0):
    if not 1 <= command <= 255 or len(data)>56 or not 0 <= position <= 0xffffff:
        raise ValueError('Comando, tamanho ou posição inválidos.')
    result=bytearray(64)
    result[0]=4; result[3]=command; result[4]=len(data)
    result[5:8]=position.to_bytes(3,'little')
    result[8:8+len(data)]=data
    result[1:3]=sum(result[3:]).to_bytes(2,'little')
    return bytes(result)

def photo_config(original):
    if len(original)!=48: raise ValueError('Configuração deve ter 48 bytes.')
    result=bytearray(original)
    result[33]=1; result[34]=1; result[46]=1
    return bytes(result)

def animation_config(original,count,delay_ms):
    if not 1<=count<=18 or not 60<=delay_ms<=65535:
        raise ValueError('Use até 18 quadros e intervalo de 60 a 65535 ms.')
    result=bytearray(photo_config(original))
    result[34]=count;result[46]=count
    result[43:45]=delay_ms.to_bytes(2,'little')
    return bytes(result)

def display_config(original,mode):
    if len(original)!=48 or mode not in (0,1,2): raise ValueError('Configuração de tela inválida.')
    result=bytearray(original);result[33]=mode
    return bytes(result)

def clock_config(original,now):
    if not 2000<=now.year<=2099: raise ValueError('O relógio aceita anos entre 2000 e 2099.')
    result=bytearray(display_config(original,0))
    def bcd(value): return ((value//10)<<4)|(value%10)
    result[35:42]=bytes([bcd(now.second),bcd(now.minute),bcd(now.hour),
                          (now.weekday()+1)%7,bcd(now.day),bcd(now.month),bcd(now.year-2000)])
    return bytes(result)

def encode_frame(image):
    if image.size!=(240,135): raise ValueError('A imagem deve medir 240 × 135.')
    result=bytearray()
    for r,g,b in image.convert('RGB').get_flattened_data():
        value=((r>>3)<<11)|((g>>2)<<5)|(b>>3)
        result.extend(value.to_bytes(2,'big'))
    result.extend(bytes(65536-len(result)))
    return bytes(result)
