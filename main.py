#!/usr/bin/env python3
import re
import tkinter as tk
from tkinter import messagebox, scrolledtext
import tkinter.font as tkfont


# 키보드 단축키 통합 처리: Ctrl/Command+키 regardless of IME mode
def handle_shortcut(event):
    # Check for Control (state & 0x4) or Command/Meta (state & 0x8)
    if not (event.state & 0x4 or event.state & 0x8):
        return
    # Use event.char to capture both English and Korean jamo characters
    ch = event.char.lower()
    mapping = {
        'c': '<<Copy>>', 'v': '<<Paste>>',
        'x': '<<Cut>>',  'a': '<<SelectAll>>',
        'ㅊ': '<<Copy>>', 'ㅍ': '<<Paste>>',
        'ㅌ': '<<Cut>>',  'ㅁ': '<<SelectAll>>'
    }
    action = mapping.get(ch)
    if action:
        event.widget.event_generate(action)
        return "break"

def merge_sentences_to_paragraph(text: str) -> str:
    """
    여러 줄로 나누어진 문장들을 하나의 문단으로 합칩니다.
    빈 줄을 제거하고, 문장 사이에 하나의 공백을 삽입합니다.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    paragraph = ' '.join(lines)
    paragraph = re.sub(r"\s+", " ", paragraph)
    return paragraph

import re

def split_paragraph_to_sentences(text: str) -> str:
    """
    하나의 문단을 문장 단위로 나누어 각 문장을 줄바꿈합니다.
    ASCII 따옴표(")와 스마트 따옴표(“ ”)를 모두 인식하며,
    따옴표 안의 여러 문장도 개별적으로 줄바꿈하되,
    첫 문장 앞에 열림 따옴표, 마지막 문장 뒤에 닫힘 따옴표를 붙여 준 뒤,
    문장 사이에 빈 줄을 한 줄씩 추가합니다.
    """
    # 스마트 따옴표를 ASCII 따옴표로 통일
    text = text.replace('“', '"').replace('”', '"')
    
    # 따옴표 세그먼트 분리 (따옴표 포함)
    segments = re.split(r'(".*?")', text, flags=re.DOTALL)
    sentences = []
    
    for seg in segments:
        if seg.startswith('"') and seg.endswith('"'):
            inner = seg[1:-1].strip()
            # 따옴표 안 문장 분리: 마침표, 물음표, 느낌표 뒤까지 포함
            parts = re.findall(r'.+?[\.!?]', inner, flags=re.DOTALL)
            for i, part in enumerate(parts):
                part = part.strip()
                if i == 0:
                    part = '"' + part
                if i == len(parts) - 1:
                    part = part + '"'
                sentences.append(part)
        else:
            # 따옴표 밖 문장 분리
            parts = re.findall(r'.+?[\.!?]', seg, flags=re.DOTALL)
            for part in parts:
                sentences.append(part.strip())
    
    # 각 문장 사이에 한 줄 공백을 넣어 결합
    return '\n\n'.join(sentences)

def on_merge():
    input_text = input_box.get("1.0", tk.END)
    if not input_text.strip():
        messagebox.showwarning("입력 오류", "변환할 텍스트를 입력하세요.")
        return
    result = merge_sentences_to_paragraph(input_text)
    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, result)

def on_split():
    input_text = input_box.get("1.0", tk.END)
    if not input_text.strip():
        messagebox.showwarning("입력 오류", "변환할 텍스트를 입력하세요.")
        return
    result = split_paragraph_to_sentences(input_text)
    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, result)


# GUI setup
# GUI setup
root = tk.Tk()
# 기본 창 크기 및 최소 크기 설정
root.geometry("800x600")
root.minsize(800, 600)
# 텍스트 위젯 전용 폰트 객체 생성 및 크기 조절 UI
text_font = tkfont.nametofont('TkTextFont').copy()
text_font.configure(size=14)

# 폰트 크기 변수 및 적용 함수
font_size_var = tk.StringVar(master=root, value='14')
def apply_font_size():
    try:
        size = int(font_size_var.get())
        text_font.configure(size=size)
    except ValueError:
        pass

control_frame = tk.Frame(root)
control_frame.pack(fill=tk.X, padx=10, pady=(5, 0))
tk.Label(control_frame, text="폰트 크기:").pack(side=tk.LEFT)
tk.Entry(control_frame, textvariable=font_size_var, width=4).pack(side=tk.LEFT)
tk.Button(control_frame, text="적용", command=apply_font_size).pack(side=tk.LEFT, padx=5)

# 텍스트 위젯 전용 폰트 크기 조정
root.title("문단 변환기")
# 창 크기 고정 (폰트 변경 시 자동 리사이즈 방지)
root.update_idletasks()
_current_geom = root.geometry()
root.geometry(_current_geom)

# 메뉴바에 Edit 기능 추가
menubar = tk.Menu(root)
editmenu = tk.Menu(menubar, tearoff=0)
editmenu.add_command(label="잘라내기", command=lambda: root.focus_get().event_generate('<<Cut>>'))
editmenu.add_command(label="복사", command=lambda: root.focus_get().event_generate('<<Copy>>'))
editmenu.add_command(label="붙여넣기", command=lambda: root.focus_get().event_generate('<<Paste>>'))
editmenu.add_separator()
editmenu.add_command(label="전체선택", command=lambda: root.focus_get().event_generate('<<SelectAll>>'))
menubar.add_cascade(label="Edit", menu=editmenu)
root.config(menu=menubar)

 # 입력 영역
tk.Label(root, text="입력 텍스트:").pack(anchor='w', padx=10, pady=(10, 0))
input_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=text_font, height=6)
input_box.pack(fill=tk.BOTH, expand=False, padx=10, pady=(0, 10))
input_box.bind('<KeyPress>', handle_shortcut)

# SelectAll 이벤트 처리
input_box.bind('<<SelectAll>>', lambda e: (e.widget.tag_add('sel', '1.0', 'end-1c'), 'break')[1])

# 우클릭 컨텍스트 메뉴 설정
ctx_menu = tk.Menu(root, tearoff=0)
ctx_menu.add_command(label="잘라내기",   command=lambda: input_box.event_generate('<<Cut>>'))
ctx_menu.add_command(label="복사",       command=lambda: input_box.event_generate('<<Copy>>'))
ctx_menu.add_command(label="붙여넣기",   command=lambda: input_box.event_generate('<<Paste>>'))
ctx_menu.add_separator()
ctx_menu.add_command(label="전체선택",   command=lambda: input_box.event_generate('<<SelectAll>>'))
for btn in ("<Button-2>", "<Button-3>"):
    input_box.bind(btn, lambda e, m=ctx_menu: m.tk_popup(e.x_root, e.y_root))

# 버튼들
button_frame = tk.Frame(root)
button_frame.pack(pady=5)
tk.Button(button_frame, text="합치기 (줄 → 문단)", command=on_merge).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="나누기 (문단 → 줄)", command=on_split).pack(side=tk.LEFT, padx=5)

# 출력 영역
tk.Label(root, text="결과 텍스트:").pack(anchor='w', padx=10, pady=(10, 0))

output_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=text_font)
output_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
output_box.bind('<KeyPress>', handle_shortcut)

root.mainloop()