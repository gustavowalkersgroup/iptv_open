#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IPTV Brasil 2026 - Desktop App"""
import os, sys, io, urllib.parse, subprocess, re, platform
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def get_resource_path(relative_path):
    """Get the absolute path to a resource, works for dev and PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

ADULT_KW = ['adulto', 'xxx', 'porn', 'xxx']

class IPTVApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("IPTV Brasil 2026")
        self.geometry("1100x700")
        self.minsize(700, 450)
        
        self.channels = self.load_channels()
        self.family_channels = [c for c in self.channels if not self.is_adult(c)]
        self.adult_channels = [c for c in self.channels if self.is_adult(c)]
        self.br_channels = [c for c in self.family_channels if self.is_br(c)]
        self.en_channels = [c for c in self.family_channels if not self.is_br(c)]
        
        self.current_filter = 'all'
        self.search_text = ''
        self.adult_unlocked = False
        
        self.build_ui()
    
    def load_channels(self):
        sob_path = get_resource_path('IPTV-Brasil-2026.sob')
        channels = []
        if not os.path.exists(sob_path):
            return channels
        with open(sob_path, 'r', encoding='utf-8') as f:
            content = f.read()
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(content)
            for item in root.findall('.//backupItem'):
                link = item.find('serviioLink')
                if link is None or not link.text:
                    continue
                match = re.match(r'serviio://(\w+):(\w+)\?(.+)', link.text)
                if not match:
                    continue
                params = urllib.parse.parse_qs(match.group(3))
                url = params.get('url', [''])[0]
                name = urllib.parse.unquote(params.get('name', [''])[0])
                th = urllib.parse.unquote(params.get('thUrl', [''])[0]) if 'thUrl' in params else ''
                if url and name:
                    channels.append({'name': name.strip(), 'url': url, 'thumbnail': th})
        except Exception as e:
            print(f"Error loading: {e}")
        return sorted(channels, key=lambda x: x['name'])
    
    def is_adult(self, ch):
        n = ch['name'].lower()
        return any(k in n for k in ADULT_KW)
    
    def is_br(self, ch):
        n = ch['name'].lower()
        return any(k in n for k in ['brasil','brazil','canal br','ipbr','grupo band','globo','sbt','record','band','rede','canais brasil','nacionais','bandeirantes','tv aberto','tv brasileira'])
    
    def build_ui(self):
        header = ctk.CTkFrame(self, height=70, corner_radius=0)
        header.pack(fill='x', padx=0, pady=0)
        header.pack_propagate(False)
        
        title = ctk.CTkLabel(header, text="📺 IPTV Brasil 2026", font=ctk.CTkFont(size=22, weight="bold"), text_color="#e94560")
        title.pack(pady=(12, 3))
        
        self.stat_label = ctk.CTkLabel(header, text=f"{len(self.family_channels)} canais familiares | {len(self.adult_channels)} adulto", font=ctk.CTkFont(size=11), text_color="#888")
        self.stat_label.pack()
        
        search_frame = ctk.CTkFrame(self, height=40, corner_radius=8)
        search_frame.pack(fill='x', padx=15, pady=(8, 3))
        search_frame.pack_propagate(False)
        
        self.search_var = ctk.StringVar()
        self.search_var.trace('w', lambda *a: self.filter_channels())
        search = ctk.CTkEntry(search_frame, placeholder_text="🔍 Buscar canal...", textvariable=self.search_var, height=30, font=ctk.CTkFont(size=13))
        search.pack(side='left', fill='x', expand=True, padx=10, pady=5)
        
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill='x', padx=15, pady=(0, 5))
        
        self.filter_buttons = {}
        for label, filter_val in [('Todos', 'all'), ('🇧🇷 BR', 'br'), ('🇺🇸 EN', 'en'), ('🔞 Adulto', 'adult')]:
            btn = ctk.CTkButton(filter_frame, text=label, width=80, height=28,
                                   command=lambda v=filter_val: self.set_filter(v),
                                   fg_color="#1a1a2e", hover_color="#e94560",
                                   text_color="#888", font=ctk.CTkFont(size=11))
            btn.pack(side='left', padx=3)
            self.filter_buttons[filter_val] = btn
        
        self.filter_buttons['all'].configure(fg_color="#e94560", text_color="white")
        
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill='both', expand=True, padx=15, pady=5)
        
        list_frame = ctk.CTkFrame(main_frame, width=280)
        list_frame.pack(side='left', fill='y', padx=(0, 5))
        list_frame.pack_propagate(False)
        
        self.listbox = tk.Listbox(list_frame, font=('Segoe UI', 10), bg='#1a1a2e', fg='white',
                                       selectbackground='#e94560', selectforeground='white',
                                       borderwidth=0, highlightthickness=0, activestyle='none',
                                       selectmode=tk.SINGLE)
        self.listbox.pack(fill='both', expand=True)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)
        
        scrollbar = ttk.Scrollbar(self.listbox, command=self.listbox.yview)
        self.listbox.config(yscrollcommand=scrollbar.set)
        
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(side='right', fill='both', expand=True)
        
        self.status_label = ctk.CTkLabel(info_frame, text="Selecione um canal para assistir", font=ctk.CTkFont(size=14), text_color="#666")
        self.status_label.pack(pady=(20, 15))
        
        self.name_label = ctk.CTkLabel(info_frame, text="", font=ctk.CTkFont(size=11), text_color="#aaa")
        self.name_label.pack()
        
        url_label = ctk.CTkLabel(info_frame, text="", font=ctk.CTkFont(size=9), text_color="#555", wraplength=500)
        url_label.pack()
        
        btn_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        play_btn = ctk.CTkButton(btn_frame, text="▶ Play no VLC", width=150, height=35,
                                     command=self.play_channel, fg_color="#e94560",
                                     hover_color="#c73652", font=ctk.CTkFont(size=13, weight="bold"))
        play_btn.pack(side='left', padx=5)
        
        stop_btn = ctk.CTkButton(btn_frame, text="⏹ Stop", width=120, height=35,
                                     command=self.stop_channel, fg_color="#333",
                                     hover_color="#555", font=ctk.CTkFont(size=12))
        stop_btn.pack(side='left', padx=5)
        
        m3u_btn = ctk.CTkButton(btn_frame, text="📋 M3U", width=100, height=35,
                                    command=self.open_m3u, fg_color="#0f3460",
                                    hover_color="#1a5276", font=ctk.CTkFont(size=12))
        m3u_btn.pack(side='left', padx=5)
        
        self.populate_list()
    
    def populate_list(self):
        self.listbox.delete(0, tk.END)
        filtered = self.get_filtered()
        for ch in filtered:
            self.listbox.insert(tk.END, ch['name'])
    
    def get_filtered(self):
        if self.current_filter == 'adult':
            if not self.adult_unlocked:
                return []
            return self.adult_channels
        filtered = self.family_channels
        if self.current_filter == 'br':
            filtered = self.br_channels
        elif self.current_filter == 'en':
            filtered = self.en_channels
        if self.search_text:
            filtered = [c for c in filtered if self.search_text.lower() in c['name'].lower()]
        return filtered
    
    def filter_channels(self):
        self.search_text = self.search_var.get()
        if self.current_filter == 'adult' and not self.adult_unlocked:
            self.listbox.delete(0, tk.END)
            self.listbox.insert(tk.END, "🔒 Categoria Adulto bloqueada")
            return
        self.populate_list()
    
    def set_filter(self, filter_val):
        if filter_val == 'adult' and not self.adult_unlocked:
            self.prompt_adult_password()
            return
        self.current_filter = filter_val
        for key, btn in self.filter_buttons.items():
            if key == filter_val:
                btn.configure(fg_color="#e94560", text_color="white")
            else:
                btn.configure(fg_color="#1a1a2e", text_color="#888")
        self.populate_list()
    
    def prompt_adult_password(self):
        pw_win = ctk.CTkToplevel(self)
        pw_win.title("🔞 Categoria Adulto")
        pw_win.geometry("400x200")
        pw_win.resizable(False, False)
        pw_win.grab_set()
        
        ctk.CTkLabel(pw_win, text="⚠️ Categoria Adulto", font=ctk.CTkFont(size=16, weight="bold"), text_color="#e94560").pack(pady=(20, 5))
        ctk.CTkLabel(pw_win, text="Digite a senha para continuar:", font=ctk.CTkFont(size=12), text_color="#aaa").pack()
        
        pw_var = ctk.StringVar()
        pw_entry = ctk.CTkEntry(pw_win, textvariable=pw_var, placeholder_text="Senha", height=35, font=ctk.CTkFont(size=14), show="*")
        pw_entry.pack(pady=15, padx=40, fill='x')
        pw_entry.focus()
        
        def check_pw():
            if pw_var.get() == "0000":
                self.adult_unlocked = True
                pw_win.destroy()
                self.set_filter('adult')
            else:
                messagebox.showerror("Erro", "Senha incorreta!")
                pw_entry.delete(0, tk.END)
        
        ctk.CTkButton(pw_win, text="Entrar", width=120, height=35, command=check_pw, fg_color="#e94560").pack(pady=5)
        
        pw_entry.bind('<Return>', lambda e: check_pw())
    
    def on_select(self, event):
        sel = self.listbox.curselection()
        if not sel:
            return
        filtered = self.get_filtered()
        if sel[0] < len(filtered) and isinstance(filtered[sel[0]], dict):
            ch = filtered[sel[0]]
            self.status_label.configure(text=f"📺 {ch['name']}")
            self.name_label.configure(text=f"Nome: {ch['name']}")
            self.url_label.configure(text=f"URL: {ch['url'][:80]}...")
    
    def get_selected_channel(self):
        sel = self.listbox.curselection()
        if not sel:
            return None
        filtered = self.get_filtered()
        if sel[0] < len(filtered):
            ch = filtered[sel[0]]
            if isinstance(ch, dict):
                return ch
        return None
    
    def play_channel(self):
        ch = self.get_selected_channel()
        if not ch:
            return
        vlc_path = get_resource_path('vlc')
        vlc_exe = os.path.join(vlc_path, 'vlc.exe')
        if not os.path.exists(vlc_exe):
            vlc_exe = r'C:\Program Files\VideoLAN\VLC\vlc.exe'
        try:
            subprocess.Popen([vlc_exe, ch['url']])
            self.status_label.configure(text=f"▶ Abrindo: {ch['name']}")
        except Exception as e:
            self.status_label.configure(text=f"Erro: {e}")
    
    def stop_channel(self):
        try:
            subprocess.run(['taskkill', '/F', '/IM', 'vlc.exe'], capture_output=True)
            self.status_label.configure(text="⏹ Parado")
        except:
            self.status_label.configure(text="⏹ Parado")
    
    def open_m3u(self):
        if self.current_filter == 'adult' and not self.adult_unlocked:
            messagebox.showerror("Erro", "Categoria Adulto bloqueada! Use a senha para acessar.")
            return
        m3u_path = get_resource_path('IPTV-Brasil-VLC.m3u8')
        os.startfile(m3u_path)
    
    def on_closing(self):
        self.destroy()

if __name__ == '__main__':
    app = IPTVApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
