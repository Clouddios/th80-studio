"""Generate the app icon (.icns/.png) and the sidebar logo from assets/epomaker-logo.svg.

Usage: .venv/bin/python tools/make_icon.py
"""
import re, subprocess, tempfile, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops, ImageFilter, ImageFont

ROOT=Path(__file__).resolve().parent.parent
ASSETS=ROOT/'assets'
FONT='/System/Library/Fonts/Supplemental/DIN Alternate Bold.ttf'
BLUE=(96,202,255);ACTION=(53,126,242)

def svg_subpaths(svg):
    """Flatten the absolute M/L/H/V/C/Z paths of the logo into point lists."""
    paths=[]
    for d in re.findall(r'\sd="([^"]+)"',svg):
        tokens=re.findall(r'[MLHVCZ]|-?\d*\.?\d+(?:e[-+]?\d+)?',d)
        i=0;x=y=0;current=[];command=None
        def num():
            nonlocal i;i+=1;return float(tokens[i-1])
        while i<len(tokens):
            if tokens[i] in 'MLHVCZ': command=tokens[i];i+=1
            if command=='M':
                if current: paths.append(current)
                x,y=num(),num();current=[(x,y)];command='L'
            elif command=='L': x,y=num(),num();current.append((x,y))
            elif command=='H': x=num();current.append((x,y))
            elif command=='V': y=num();current.append((x,y))
            elif command=='C':
                x1,y1,x2,y2,x3,y3=(num() for _ in range(6))
                for step in range(1,9):
                    t=step/8;u=1-t
                    current.append((u**3*x+3*u*u*t*x1+3*u*t*t*x2+t**3*x3,u**3*y+3*u*u*t*y1+3*u*t*t*y2+t**3*y3))
                x,y=x3,y3
            elif command=='Z':
                if current: paths.append(current)
                current=[];command=None
        if current: paths.append(current)
    return paths

def logo_mask(width):
    """Even-odd rasterization of the logo, supersampled for smooth edges."""
    svg=(ASSETS/'epomaker-logo.svg').read_text()
    vw,vh=map(float,re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"',svg).groups())
    scale=width*4/vw;size=(width*4,round(vh*scale))
    mask=Image.new('L',size,0)
    for points in svg_subpaths(svg):
        layer=Image.new('L',size,0)
        ImageDraw.Draw(layer).polygon([(px*scale,py*scale) for px,py in points],fill=255)
        mask=ImageChops.logical_xor(mask.convert('1'),layer.convert('1')).convert('L')
    return mask.resize((width,round(vh*width/vw)),Image.LANCZOS)

def gradient(size,top,bottom):
    column=Image.new('RGB',(1,256))
    for row in range(256):
        t=row/255;column.putpixel((0,row),tuple(round(a+(b-a)*t) for a,b in zip(top,bottom)))
    return column.resize(size,Image.BICUBIC)

def app_icon():
    """1024px macOS icon: graphite squircle, blue glow, EPOMAKER mark and TH80."""
    S=1024;inset=100;box=(inset,inset,S-inset,S-inset);radius=185
    icon=Image.new('RGBA',(S,S),(0,0,0,0))
    shape=Image.new('L',(S,S),0);ImageDraw.Draw(shape).rounded_rectangle(box,radius,fill=255)
    body=gradient((S,S),(46,61,84),(18,26,38)).convert('RGBA')
    glow=Image.new('RGBA',(S,S),(0,0,0,0))
    ImageDraw.Draw(glow).ellipse((180,700,844,1060),fill=ACTION+(150,))
    body=Image.alpha_composite(body,glow.filter(ImageFilter.GaussianBlur(90)))
    draw=ImageDraw.Draw(body)
    draw.rounded_rectangle((box[0]+3,box[1]+3,box[2]-3,box[3]-3),radius-3,outline=(255,255,255,40),width=4)
    mark=logo_mask(560);x=(S-mark.width)//2
    body.paste((255,255,255,255),(x,270),mark)
    font=ImageFont.truetype(FONT,190);text='TH80'
    left,top,right,bottom=draw.textbbox((0,0),text,font=font)
    draw.text(((S-(right-left))//2-left,560-top),text,font=font,fill=BLUE)
    draw.rounded_rectangle((S//2-110,800,S//2+110,812),6,fill=BLUE+(200,))
    icon.paste(body,(0,0),shape)
    shadow=Image.new('RGBA',(S,S),(0,0,0,0))
    shadow.paste((0,0,0,110),(0,12),shape)
    return Image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(14)),icon)

def write_icns(icon,target):
    with tempfile.TemporaryDirectory() as folder:
        iconset=Path(folder)/'icon.iconset';iconset.mkdir()
        for size in (16,32,128,256,512):
            icon.resize((size,size),Image.LANCZOS).save(iconset/f'icon_{size}x{size}.png')
            icon.resize((size*2,size*2),Image.LANCZOS).save(iconset/f'icon_{size}x{size}@2x.png')
        subprocess.run(['iconutil','-c','icns',str(iconset),'-o',str(target)],check=True)

if __name__=='__main__':
    icon=app_icon();icon.save(ASSETS/'icon.png')
    icon.resize((256,256),Image.LANCZOS).save(ASSETS/'icon-256.png')
    if sys.platform=='darwin': write_icns(icon,ASSETS/'icon.icns')
    mark=logo_mask(124);sidebar=Image.new('RGBA',mark.size,(255,255,255,0))
    sidebar.paste((236,242,248,255),(0,0),mark);sidebar.save(ASSETS/'sidebar-logo.png')
    print('Ícones gerados em',ASSETS)
