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

# 1번 기능: 여러 줄 -> 한 문단
def merge_sentences_to_paragraph(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    paragraph = ' '.join(lines)
    return re.sub(r"\s+", " ", paragraph)

# 2번 기능: 문단 -> 문장별 줄바꿈
def split_paragraph_to_sentences(text: str) -> str:
    text = text.replace('"', "'")
    # 스마트 큰따옴표 및 작은따옴표 통일
    text = (text
            .replace('“', '"').replace('”', '"')
            .replace('‘', "'").replace('’', "'"))
    # 큰따옴표(") 또는 작은따옴표(')로 감싼 구간 분리
    segments = re.split(r'(".*?"|\'.*?\')', text, flags=re.DOTALL)
    sentences = []
    for seg in segments:
        if (seg.startswith('"') and seg.endswith('"')) or (seg.startswith("'") and seg.endswith("'")):
            quote_char = seg[0]
            inner = seg[1:-1]
            parts = re.findall(r'.+?[\.!?](?=\s|$)|.+?$', inner, flags=re.DOTALL)
            parts = [s.strip() for s in parts if s.strip()]
            for i, part in enumerate(parts):
                if i == 0:
                    part = quote_char + part
                if i == len(parts) - 1:
                    part = part + quote_char
                sentences.append(part)
        else:
            parts = re.findall(r'.+?[\.!?](?=\s|$)|.+?$', seg, flags=re.DOTALL)
            for p in parts:
                p = p.strip()
                if p: sentences.append(p)
    return "\n\n".join(sentences)


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
root = tk.Tk()
# 기본 창 크기 및 최소 크기 설정
root.geometry("800x600")
root.minsize(800, 600)
text_font = tkfont.nametofont('TkTextFont').copy()
text_font.configure(size=12)
root.title("문단 변환기")

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
input_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=6, font = text_font)
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

output_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, font = text_font)
output_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
output_box.bind('<KeyPress>', handle_shortcut)

root.mainloop()