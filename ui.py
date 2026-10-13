"""Native desktop frontend. Graphite shell, blue keycaps and live LCD preview."""
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from via import KEYCODES, key_name

C={'base':'#202b3b','side':'#17212e','panel':'#29374b','edge':'#41526b',
   'text':'#ecf2f8','muted':'#a8b8ce','blue':'#60caff','action':'#357ef2'}

def label(parent,text='',size=11,color=None,bg=None,weight='normal',**kwargs):
    return tk.Label(parent,text=text,fg=color or C['text'],bg=bg or parent.cget('bg'),
                    font=('Bahnschrift' if size>=20 else 'Segoe UI',size,weight),anchor='w',**kwargs)

def rounded(canvas,x1,y1,x2,y2,r=8,**kwargs):
    points=[x1+r,y1,x2-r,y1,x2,y1,x2,y1+r,x2,y2-r,x2,y2,x2-r,y2,
            x1+r,y2,x1,y2,x1,y2-r,x1,y1+r,x1,y1]
    return canvas.create_polygon(points,smooth=True,**kwargs)

class KeyboardCanvas(tk.Canvas):
    def __init__(self,parent,layout,callback=None,height=235):
        super().__init__(parent,bg=parent.cget('bg'),highlightthickness=0,height=height)
        self.layout=layout;self.callback=callback;self.codes={};self.selected=None
        self.bind('<Configure>',lambda event:self.draw())
    def draw(self):
        self.delete('all')
        width=max(self.winfo_width(),300);height=max(self.winfo_height(),180)
        units=max(k.x+k.width for k in self.layout)
        rows=max(k.y+k.height for k in self.layout)
        unit=min((width-36)/units,(height-32)/rows)
        left=(width-unit*units)/2;top=12
        rounded(self,left-10,top-10,left+unit*units+10,top+unit*rows+10,12,fill='#111b29',outline=C['edge'],width=2)
        short={'Backspace':'Bksp','Espaço':'','Windows esquerdo':'Win','Windows direito':'Win',
               'Ctrl esquerdo':'Ctrl','Ctrl direito':'Ctrl','Shift esquerdo':'Shift','Shift direito':'Shift',
               'Alt esquerdo':'Alt','Alt direito':'Alt','Caps Lock':'Caps','Page Up':'PgUp','Page Down':'PgDn',
               'Esquerda':'←','Direita':'→','Cima':'↑','Baixo':'↓','Transparente':'▽','Desativada':'×'}
        for key in self.layout:
            pos=(key.row,key.col);tag=f'key-{key.row}-{key.col}'
            x=left+key.x*unit;y=top+key.y*unit
            selected=pos==self.selected
            fill=C['action'] if selected else ('#7ca4d6' if key.row==0 else '#e0e5ec')
            rounded(self,x+2,y+2,x+key.width*unit-2,y+key.height*unit-2,5,fill=fill,outline=C['blue'] if selected else '#101e31',width=1,tags=(tag,))
            code=self.codes.get(f'{key.row},{key.col}')
            name=key_name(code) if code is not None else ('Esc' if pos==(0,0) else (f'F{key.col}' if key.row==0 else ''))
            name=short.get(name,name)
            if name.startswith('Especial'): name='Fn / esp.'
            self.create_text(x+key.width*unit/2,y+key.height*unit/2,text=name,fill='#ffffff' if selected else '#20304a',font=('Segoe UI',max(7,int(unit/5))),tags=(tag,))
            if self.callback:
                self.tag_bind(tag,'<Button-1>',lambda event,p=pos:self.callback(p))
        if self.callback: self.configure(cursor='hand2')
    def set_codes(self,codes): self.codes=codes;self.draw()

def build_ui(app):
    root=app.root;root.configure(bg=C['base'])
    style=ttk.Style();style.theme_use('clam')
    style.configure('TButton',background=C['panel'],foreground=C['text'],bordercolor=C['edge'],lightcolor=C['edge'],darkcolor=C['edge'],font=('Segoe UI',10),padding=(15,9),focuscolor=C['blue'])
    style.map('TButton',background=[('active','#354965'),('disabled','#263244')],foreground=[('disabled','#6f839c')])
    style.configure('Accent.TButton',background=C['action'],bordercolor=C['action'],font=('Segoe UI',10,'bold'))
    style.map('Accent.TButton',background=[('active','#4b95ff'),('disabled','#263244')])
    style.configure('TCombobox',fieldbackground=C['side'],background=C['panel'],foreground=C['text'],arrowcolor=C['text'],bordercolor=C['edge'],padding=7)
    style.map('TCombobox',fieldbackground=[('readonly',C['side'])],foreground=[('readonly',C['text'])])
    style.configure('TSpinbox',fieldbackground=C['side'],background=C['panel'],foreground=C['text'],arrowcolor=C['text'],bordercolor=C['edge'],padding=5)
    style.configure('Horizontal.TProgressbar',background=C['blue'],troughcolor=C['side'],bordercolor=C['side'],lightcolor=C['blue'],darkcolor=C['blue'])
    root.option_add('*TCombobox*Listbox.background',C['side']);root.option_add('*TCombobox*Listbox.foreground',C['text'])
    sidebar=tk.Frame(root,bg=C['side'],width=176);sidebar.pack(side='left',fill='y');sidebar.pack_propagate(False)
    label(sidebar,'TH80\nStudio',size=29,weight='bold',color=C['blue']).pack(anchor='w',padx=22,pady=(28,4))
    label(sidebar,'Seu teclado. Seu estilo.',size=9,color=C['muted']).pack(anchor='w',padx=22,pady=(0,34))
    app.nav_buttons={};app.pages={}
    for key,name in [('images','Tela e GIF'),('clock','Relógio'),('keys','Teclas'),('lighting','Iluminação'),('manual','Manual')]:
        button=tk.Button(sidebar,text=name,anchor='w',bg=C['side'],fg=C['muted'],activebackground=C['panel'],activeforeground=C['text'],relief='flat',borderwidth=0,padx=18,pady=12,font=('Segoe UI',11),command=lambda p=key:app.show_page(p),takefocus=True)
        button.pack(fill='x',padx=10,pady=3);app.nav_buttons[key]=button
    label(sidebar,'EPOMAKER\nTH80 Pro V2\nConexão USB',size=10,color=C['muted'],justify='left').pack(side='bottom',anchor='w',padx=22,pady=25)
    shell=tk.Frame(root,bg=C['base']);shell.pack(side='left',fill='both',expand=True)
    header=tk.Frame(shell,bg=C['base']);header.pack(fill='x',padx=28,pady=(26,18))
    app.heading=tk.StringVar(value='Tela e GIF')
    label(header,size=25,weight='bold',textvariable=app.heading).pack(side='left')
    app.connection_label=label(header,'●  Aguardando USB',size=10,color=C['muted']);app.connection_label.pack(side='right',padx=(12,0))
    app.button=ttk.Button(header,text='Conectar teclado',command=app.start);app.button.pack(side='right')
    body=tk.Frame(shell,bg=C['base']);body.pack(fill='both',expand=True,padx=28)
    for key in app.nav_buttons:
        app.pages[key]=tk.Frame(body,bg=C['base'])
    images=app.pages['images']
    label(images,'Uma telinha com a sua personalidade.',size=11,color=C['muted']).pack(anchor='w',pady=(0,18))
    hero=tk.Frame(images,bg=C['panel']);hero.pack(fill='x')
    display=tk.Frame(hero,bg=C['panel']);display.pack(side='left',padx=22,pady=22)
    screen=tk.Frame(display,bg='#0b1522',highlightbackground=C['edge'],highlightthickness=2)
    screen.pack()
    app.preview=tk.Label(screen,text='Escolha uma foto ou GIF\npara ver a prévia na tela.',width=40,height=10,bg='#0b1522',fg=C['muted'],font=('Segoe UI',10),compound='center')
    app.preview.pack(padx=10,pady=10)
    label(display,'240 × 135 pixels • prévia do envio',size=9,color=C['muted']).pack(anchor='w',pady=(10,0))
    controls=tk.Frame(hero,bg=C['panel']);controls.pack(side='left',fill='both',expand=True,padx=(0,20),pady=22)
    label(controls,'Foto ou animação',size=18,weight='bold').pack(anchor='w',pady=(0,12))
    app.choose_button=ttk.Button(controls,text='Escolher foto / GIF',command=app.choose);app.choose_button.pack(fill='x',pady=(0,8))
    app.send_button=ttk.Button(controls,text='Enviar para o teclado',style='Accent.TButton',state='disabled',command=app.send);app.send_button.pack(fill='x',pady=(0,14))
    label(controls,'Intervalo da animação (ms)',size=9,color=C['muted']).pack(anchor='w')
    app.delay=tk.StringVar(value='100')
    app.delay_input=ttk.Spinbox(controls,from_=60,to=65535,increment=10,width=9,textvariable=app.delay,state='disabled');app.delay_input.pack(anchor='w',pady=6)
    app.media_info=tk.StringVar(value='GIFs são adaptados para até 18 quadros por posição.')
    label(images,textvariable=app.media_info,size=10,color=C['muted'],wraplength=740).pack(anchor='w',pady=(12,2))
    app.hero_keyboard=KeyboardCanvas(images,app.layout,height=225);app.hero_keyboard.pack(fill='x',pady=(5,0))
    label(images,'O envio substitui as duas imagens salvas. Deixe o cabo conectado até terminar.',size=9,color=C['muted'],wraplength=740).pack(anchor='w')
    clock=app.pages['clock']
    label(clock,'Acompanhe o tempo sem sair do teclado.',color=C['muted']).pack(anchor='w',pady=(0,22))
    clock_panel=tk.Frame(clock,bg=C['panel'],padx=28,pady=24);clock_panel.pack(fill='x')
    app.clock_preview=label(clock_panel,datetime.now().strftime('%H:%M'),size=68,color=C['blue']);app.clock_preview.pack(anchor='w')
    app.date_preview=label(clock_panel,datetime.now().strftime('%d / %m / %Y'),size=13,color=C['muted']);app.date_preview.pack(anchor='w',pady=(0,20))
    app.clock_button=ttk.Button(clock_panel,text='Acertar hora e mostrar relógio',style='Accent.TButton',state='disabled',command=lambda:app.change_screen('clock'));app.clock_button.pack(anchor='w',pady=(0,10))
    app.image_button=ttk.Button(clock_panel,text='Voltar à imagem salva',state='disabled',command=lambda:app.change_screen('image'));app.image_button.pack(anchor='w')
    label(clock,'A prévia usa o horário do Windows. O teclado é sincronizado ao clicar; suas imagens são preservadas.',color=C['muted'],wraplength=720).pack(anchor='w',pady=20)
    keys=app.pages['keys']
    label(keys,'Clique no teclado para mudar uma tecla.',color=C['muted']).pack(anchor='w',pady=(0,16))
    row=tk.Frame(keys,bg=C['base']);row.pack(fill='x')
    app.layer=tk.StringVar(value='Camada 1')
    app.layer_input=ttk.Combobox(row,textvariable=app.layer,values=['Camada 1'],width=14,state='disabled');app.layer_input.pack(side='left')
    app.layer_input.bind('<<ComboboxSelected>>',lambda event:app.load_keys())
    app.via_button=ttk.Button(row,text='Ler teclas e iluminação',command=app.load_keys);app.via_button.pack(side='left',padx=12)
    app.keyboard_view=KeyboardCanvas(keys,app.layout,app.select_key,height=275);app.keyboard_view.pack(fill='x',pady=16)
    edit=tk.Frame(keys,bg=C['panel'],padx=20,pady=18);edit.pack(fill='x')
    app.key_info=tk.StringVar(value='Leia a camada para ver as funções atuais.')
    label(edit,textvariable=app.key_info,size=12).pack(anchor='w',pady=(0,12))
    action=tk.Frame(edit,bg=C['panel']);action.pack(fill='x')
    app.new_key=tk.StringVar(value='A')
    app.key_input=ttk.Combobox(action,textvariable=app.new_key,values=list(KEYCODES.values()),state='disabled',width=21);app.key_input.pack(side='left')
    app.apply_key_button=ttk.Button(action,text='Aplicar tecla',style='Accent.TButton',state='disabled',command=app.apply_key);app.apply_key_button.pack(side='left',padx=10)
    app.undo_button=ttk.Button(edit,text='Desfazer última alteração',state='disabled',command=app.undo_key);app.undo_button.pack(anchor='w',pady=(12,0))
    label(keys,'O mapa vem do seu JSON VIA. Apenas a tecla selecionada é alterada; o valor anterior fica salvo para desfazer.',color=C['muted'],wraplength=730,size=9).pack(anchor='w',pady=16)
    lighting_page=app.pages['lighting']
    light_scroll=ttk.Scrollbar(lighting_page);light_scroll.pack(side='right',fill='y')
    light_canvas=tk.Canvas(lighting_page,bg=C['base'],highlightthickness=0,yscrollcommand=light_scroll.set)
    light_canvas.pack(side='left',fill='both',expand=True);light_scroll.configure(command=light_canvas.yview)
    lighting=tk.Frame(light_canvas,bg=C['base'])
    light_window=light_canvas.create_window((0,0),window=lighting,anchor='nw')
    lighting.bind('<Configure>',lambda event:light_canvas.configure(scrollregion=light_canvas.bbox('all')))
    light_canvas.bind('<Configure>',lambda event:light_canvas.itemconfigure(light_window,width=event.width))
    light_canvas.bind('<MouseWheel>',lambda event:light_canvas.yview_scroll(-int(event.delta/120),'units'))
    label(lighting,'A iluminação que o firmware disponibilizar.',color=C['muted']).pack(anchor='w',pady=(0,10))
    app.light_info=tk.StringVar(value='Clique em verificar para consultar os controles VIA disponíveis.')
    label(lighting,textvariable=app.light_info,wraplength=700).pack(anchor='w',pady=(0,10))
    app.light_probe=ttk.Button(lighting,text='Verificar iluminação',command=app.load_light);app.light_probe.pack(anchor='w',pady=(0,10))
    app.light_learn=ttk.Button(lighting,text='Adicionar estado atual',command=app.learn_light);app.light_learn.pack(anchor='w',pady=(0,10))
    label(lighting,'Mude o efeito ou a velocidade pelos atalhos do teclado e adicione o estado para ampliar as listas.',color=C['muted'],wraplength=720,size=9).pack(anchor='w',pady=(0,10))
    app.light_capture=ttk.Button(lighting,text='1 · Capturar antes',command=app.capture_light);app.light_capture.pack(anchor='w',pady=(0,10))
    label(lighting,'Capture antes, mude somente um ajuste e capture depois. Cada par começa uma nova comparação. Instruções na aba Manual.',color=C['muted'],wraplength=720,size=9).pack(anchor='w',pady=(0,14))
    light_panel=tk.Frame(lighting,bg=C['panel'],padx=24,pady=16);light_panel.pack(fill='x')
    label(light_panel,'Brilho',size=17).pack(anchor='w')
    app.brightness=tk.DoubleVar(value=128)
    app.brightness_input=tk.Scale(light_panel,from_=0,to=255,orient='horizontal',variable=app.brightness,bg=C['panel'],fg=C['text'],troughcolor=C['side'],highlightthickness=0,activebackground=C['blue'],state='disabled');app.brightness_input.pack(fill='x',pady=(6,10))
    options=tk.Frame(light_panel,bg=C['panel']);options.pack(fill='x',pady=(0,10))
    label(options,'Efeito',size=10).grid(row=0,column=0,sticky='w',pady=(0,5))
    label(options,'Velocidade',size=10).grid(row=0,column=1,sticky='w',padx=(18,0),pady=(0,5))
    app.effect_choice=tk.StringVar(value='Manter atual');app.speed_choice=tk.StringVar(value='Manter atual')
    app.effect_input=ttk.Combobox(options,textvariable=app.effect_choice,values=['Manter atual']+[f'Efeito {n}' for n in app.native_effects],width=18,state='disabled');app.effect_input.grid(row=1,column=0,sticky='w')
    app.speed_input=ttk.Combobox(options,textvariable=app.speed_choice,values=['Manter atual']+[f'Nível {n}' for n in app.native_speeds],width=18,state='disabled');app.speed_input.grid(row=1,column=1,sticky='w',padx=(18,0))
    label(options,'Cor',size=10).grid(row=2,column=0,sticky='w',pady=(10,5))
    app.native_color_choice=tk.StringVar(value='Manter atual')
    app.native_color_input=ttk.Combobox(options,textvariable=app.native_color_choice,values=['Manter atual','Cor personalizada']+list(app.native_colors),width=30,state='disabled');app.native_color_input.grid(row=3,column=0,columnspan=2,sticky='w')
    palette=tk.Frame(light_panel,bg=C['panel']);palette.pack(fill='x',pady=(0,10))
    app.color='#60caff';app.color_buttons=[]
    for color in ['#60caff','#9678fa','#f478a3','#f4c765','#ffffff']:
        button=tk.Button(palette,text='●',font=('Segoe UI',20),bg=C['panel'],fg=color,activebackground=C['edge'],activeforeground=color,relief='flat',width=3,command=lambda c=color:app.choose_color(c),state='disabled')
        button.pack(side='left',padx=(0,8));app.color_buttons.append(button)
    app.color_info=label(light_panel,'Cor: azul',color=C['muted'],size=10);app.color_info.pack(anchor='w',pady=(0,8))
    app.color_picker=ttk.Button(light_panel,text='Roda de cores / HEX…',command=app.pick_color,state='disabled');app.color_picker.pack(anchor='w',pady=(0,12))
    app.light_apply=ttk.Button(light_panel,text='Aplicar iluminação',style='Accent.TButton',state='disabled',command=app.apply_light);app.light_apply.pack(anchor='w')
    label(lighting,'A cor depende do efeito ativo. Os controles só são habilitados depois de uma resposta do teclado.',color=C['muted'],wraplength=720,size=9).pack(anchor='w',pady=18)
    manual=app.pages['manual']
    label(manual,'Seu guia para o TH80 Pro V2.',color=C['muted']).pack(anchor='w',pady=(0,14))
    ttk.Button(manual,text='Abrir manual oficial',command=app.open_manual).pack(anchor='w',pady=(0,16))
    guide=tk.Frame(manual,bg=C['panel']);guide.pack(fill='both',expand=True)
    scrollbar=ttk.Scrollbar(guide);scrollbar.pack(side='right',fill='y')
    text=tk.Text(guide,bg=C['panel'],fg=C['text'],font=('Segoe UI',11),wrap='word',relief='flat',borderwidth=0,padx=22,pady=20,yscrollcommand=scrollbar.set,height=12)
    text.pack(fill='both',expand=True);scrollbar.configure(command=text.yview)
    text.tag_configure('heading',font=('Bahnschrift',16),foreground=C['blue'],spacing1=16,spacing3=10)
    text.tag_configure('body',spacing3=12)
    from manual import SECTIONS
    for title,body in SECTIONS:
        text.insert('end',title+'\n','heading');text.insert('end',body+'\n\n','body')
    text.configure(state='disabled')
    footer=tk.Frame(shell,bg=C['side'],padx=24,pady=13);footer.pack(fill='x',side='bottom',pady=(18,0))
    app.status=tk.StringVar(value='Conecte o teclado por USB para começar.')
    label(footer,textvariable=app.status,size=10,wraplength=800).pack(anchor='w',pady=(0,8))
    app.bar=ttk.Progressbar(footer,mode='determinate',value=0);app.bar.pack(fill='x')
    app.show_page('images')
