"""Bounded, acknowledged transfers. No retries after a write failure."""
import time
from protocol import packet, config_query, matches_response, select_device, photo_config, animation_config

class Device:
    def __enter__(self):
        import hid
        info=select_device(hid.enumerate(0x320f,0x5055))
        self.handle=hid.device()
        try:
            self.handle.open_path(info['path'])
            for _ in range(10):
                if not self.handle.read(64,20): break
        except Exception:
            self.handle.close()
            raise
        return self

    def __exit__(self,*args): self.handle.close()

    def transact(self,request,timeout=3):
        if self.handle.write(request)!=len(request): raise OSError('Envio USB incompleto.')
        deadline=time.monotonic()+timeout
        while time.monotonic()<deadline:
            response=bytes(self.handle.read(64,100))
            if matches_response(request,response):
                if request[3]!=5 and response[7] in (0xfe,0xff):
                    raise OSError(f'Teclado recusou o comando {request[3]:02x}: {response.hex()}')
                return response
        raise TimeoutError(f'Sem confirmação USB para o comando {request[3]:02x}. Transferência interrompida.')

    def read_config(self):
        return b''.join(self.transact(config_query(offset))[4:8] for offset in range(0,48,4))

    def exchange(self,command,data=b'',position=0):
        if command==2: time.sleep(0.1)
        return self.transact(packet(command,data,position),30 if command==0x23 else 3)[4:]

def upload(exchange,original,frame,progress):
    config=photo_config(original)
    if len(frame)!=65536: raise ValueError('Quadro de imagem inválido.')
    _upload(exchange,config,frame+frame,progress)

def write_config(exchange,config):
    if len(config)!=48: raise ValueError('Configuração inválida.')
    exchange(1);exchange(6,config);exchange(2)

def upload_animation(exchange,original,frames,delay_ms,progress):
    config=animation_config(original,len(frames),delay_ms)
    if any(len(frame)!=65536 for frame in frames): raise ValueError('Quadro de imagem inválido.')
    data=b''.join(frames)
    _upload(exchange,config,data+data,progress)

def _upload(exchange,config,data,progress):
    write_config(exchange,config)
    exchange(0x23); exchange(1)
    for offset in range(0,len(data),56):
        exchange(0x21,data[offset:offset+56],offset)
        if offset% (56*24)==0: progress(min(99,(offset+56)*100/len(data)))
    exchange(2)
    progress(100)
