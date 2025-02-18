from contextlib import closing
from doctest import script_from_examples
import glob
from shutil import move
from tkinter import *  # type: ignore
from tkinter import ttk
from tkinter import filedialog
from tkinter.font import nametofont
from tkinter import messagebox
from tkinter.font import Font
from turtle import back, update
import sv_ttk
import ctypes
import os
import re

import numpy
import main
import classes
from PIL import ImageTk, Image
import threading
import time
import io
import sqlite3

## SETUP ##
values = {}
values_memory = []
values_index = -1
background_color = "#424549"
text_color = "#99aab5"
second_background_color = "#36393e"

preview_count = 0

enable_forward = False
enable_back = False

conn = sqlite3.connect('cards.db')
c = conn.cursor()

window = Tk()
style = ttk.Style()
sv_ttk.set_theme("dark")

#windows only
# window_id = "card.generator.window"  # will only work once compiled I think
# ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(window_id)

small_font = Font(family='Roboto', size=10, weight='bold')
mid_font = Font(family='Roboto', size=15, weight='bold')
big_font = Font(family='Roboto', size=20, weight='bold')

window.title("Card generator")

icon = Image.open(io.BytesIO(main.get_asset('Energy neutral', c)))
buffer = io.BytesIO()
icon.save(buffer, format="PNG")
buffer.seek(0)
tk_icon = PhotoImage(data=buffer.getvalue())

# Set the icon
window.iconphoto(True, tk_icon)
window.config(background=background_color)

## FUNCTIONS ##
move_count = 1
limit = 3

update_canv = False
def update_canvas():
    global move_count
    global limit
    global ind_move_frame
    global update_canv

    if not update_canv: return
    update_canv = False

    print("Updating canvas")

    #resize scroll canvas
    scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))
    scroll_canvas.configure(width=mainframe.winfo_width())




def resize_font(incr):
    '''Change the size of SunValley fonts by the incr factor '''
    for font_name in (
        "Caption", "Body", "BodyStrong", "BodyLarge",
        "Subtitle", "Title", "TitleLarge", "Display"
    ):
        font = nametofont(f"SunValley{font_name}Font")
        size = font.cget("size")
        font.configure(size=size-incr)

def character_limit(entry_text, power, max=0): # only allow numbers in field
    # remove non-numeric characters and leading zeros. Round to the nearest power of ten given by the power.
    if '.' in entry_text.get():
        value = entry_text.get().split('.')[0]
    else:
        value = entry_text.get()

    value = re.sub(r'^0+', '', value)
    value = re.sub(r'\D', '', value)

    if value == '': value = '0'
    value = int(value)    

    if len(str(value)) == 1:
        value = value * 10**power
    else:
        value = int(round(value, -power))

    value = str(value)
    if value != '0': entry_text.set(re.sub(r'^0+', '', value))
    else: entry_text.set('0')
    if max != 0 and int(value) > max: entry_text.set(str(max))


def match_vars_to_values():
    #perform all resets
    reset_name()
    reset_hp()
    reset_evo()
    reset_rarity()
    reset_type()
    reset_moves()
    reset_retreat()
    reset_desc()
    reset_index()
    reset_illustrator()
    import_image(io.BytesIO(values['image']))
    reset_rect()

update_prev = False
update_value = True
def update_preview(conn):
    global values
    global picture_frame
    global photo
    global preview_label
    global update_prev
    global preview_count
    global update_value
    
    if not update_prev: return
    update_prev = False
    preview_count += 1
    print("Updating preview " + str(preview_count))
    
    width = window.winfo_width() - scrollbar.winfo_width() - scroll_canvas.winfo_width()
    height = preview_label.winfo_height()
    
    image = main.preview_card(values, conn, editor_mode=True)
    heightScale = height/image.height
    widthScale = width/image.width
    scale = min(heightScale, widthScale)
    image = image.resize((int(image.width*scale), int(image.height*scale)), resample=0)
    photo = ImageTk.PhotoImage(image)
    preview_label['image'] = photo
    
    if update_value:
        update_value_index(values)
    
    update_value = False

def set_update_prev(update_val = True):
    global update_prev
    global update_value
    update_value = update_val
    update_prev = True

def set_update_canv():
    global update_canv
    update_canv = True


closing = False
def update_prevncanv():
    conn2 = sqlite3.connect('cards.db')

    while not closing:
        time.sleep(0.1)
        update_preview(conn2)

        update_canvas()

    conn2.close()


## EVENT HANDLERS ##
update_thread = threading.Thread(target=update_prevncanv)

def on_closing():
    global closing
    global update_thread


    if messagebox.askokcancel("Quit", "Are you sure you want to quit? Unsaved progress will be lost."):
        closing = True

        if update_thread is not None and update_thread.is_alive():
            update_thread.join(timeout=0.3)

        window.destroy()
        conn.close()
        print("Connection closed succesfully")

def open_existing(name):
    global enable_back
    global values
    global active_page

    options = search_cards(name)
    if len(options) == 1:
        values['name'] = options[0]
        get_card()        
        page2.lift()
        active_page = 2
        enable_back = True
        match_vars_to_values()
        set_update_prev()

def create_new():
    global enable_back
    global values
    global c
    global update_canv
    global active_page

    values = main.set_default(c)
    page2.lift()
    active_page = 2
    enable_back = True
    update_value_index(values)
    match_vars_to_values()
    set_update_canv()
    set_update_prev()

active_page = 0
def go_back(event):
    global enable_back

    if enable_back:
        enable_back = False
        page1.lift()
    

def go_forward(event):
    global active_page
    global enable_back

    if active_page == 2:
        enable_back = True
        page2.lift()
    elif active_page == 3:
        enable_back = True
        pass #TODO: add pages
    else:
        pass
    

def ctrlz(event):
    global values_index
    global values_memory
    global values
    global update_value

    if values_index != 0:
        values_index = values_index - 1
        values = values_memory[values_index].copy()
        match_vars_to_values()
        set_update_prev(False)


def ctrly(event):
    global values_index
    global values_memory
    global values
    global update_value
    
    if values_index != len(values_memory) - 1:
        values_index = values_index + 1
        values = values_memory[values_index].copy()
        match_vars_to_values()
        set_update_prev(False)

def ctrls(event):
    main.store_card(c, conn)

def search_cards(search):
    global existing_cards
    options = [x for x in existing_cards if search.lower() in x.lower()]
    return options

def search_moves(search):
    global existing_moves
    options = [x for x in existing_moves if search.lower() in x.lower()]
    return options

def get_card():
    global values
    global values_memory
    global values_index
    global c

    values = main.generate_dict(values['name'], c)
    update_value_index(values)

def update_value_index(values):
    global values_index
    global values_memory

    values_memory = values_memory[:values_index + 1] # remove all values after current index
    values_memory.append(values.copy()) # add new values
    values_index = values_index + 1 # update index
    


## INITIALISATION ##

values = main.set_default(c)


window.protocol("WM_DELETE_WINDOW", on_closing)
window.bind("<Button-4>", go_back)
window.bind("<Button-5>", go_forward)
window.bind("<Control-z>", ctrlz)
window.bind("<Control-y>", ctrly)
window.bind("<Control-s>", ctrls)
window.bind('<Configure>', lambda event: set_update_canv())

c.execute("SELECT name FROM get_cards")
existing_cards = c.fetchall()
existing_cards = [x[0] for x in existing_cards]
c.execute("SELECT moveName FROM get_moves")
existing_moves = c.fetchall()
existing_moves = [x[0] for x in existing_moves]

resize_font(2)
borderwidth = 5
padding = 2

## PAGE CONTROL ##

page1 = Frame(window, background=background_color)
page1.place(in_=window, x=0, y=0, relwidth=1, relheight=1)

page2 = Frame(window, background=background_color)
page2.place(in_=window, x=0, y=0, relwidth=1, relheight=1)

page1.lift()

## PAGE 1 ##

# Title frame
p1_button_frame = Frame(page1, background=background_color)
p1_button_frame.pack(pady=10)

filler = ttk.Label(p1_button_frame,background=background_color, width=10)
filler.pack(side=LEFT)

title = ttk.Label(p1_button_frame, text="Card generator", font=big_font, background=background_color, foreground=text_color, anchor=CENTER)
title.pack(expand=True, side=LEFT, fill=BOTH,padx=20)

# forward button
forward = ttk.Button(p1_button_frame, text='Forward', width=10, command=lambda: go_forward(None))
forward.pack(side=RIGHT)

# Search bar for existing cards
options = search_cards("")

open_name = StringVar(page1)

card_list = ttk.Combobox(page1, textvariable=open_name, values=options, font=mid_font)
card_list.pack(pady=10)

card_list.bind("<KeyRelease>", lambda event: card_list.configure(values=search_cards(card_list.get())))
card_list.bind("<Return>", lambda event: open_existing(open_name.get()))

# button to open existing card
open_card = ttk.Button(page1, text="Open existing card", command=lambda: open_existing(open_name.get()))
open_card.pack(pady=10)

# button to create new card
new_card = ttk.Button(page1, text="Create new card", command=create_new)
new_card.pack(pady=10)


## PAGE 2 ##


########## Scrollable canvas ##########
scroll_canvas = Canvas(page2, background=background_color, takefocus=False, highlightthickness=0)
scroll_canvas.pack(fill=BOTH, side=LEFT)


########## Scrollbar ##########
scrollbar = ttk.Scrollbar(page2,
                       orient=VERTICAL, 
                       command=scroll_canvas.yview)
scrollbar.pack(side=LEFT, fill=Y)

scroll_canvas.configure(yscrollcommand=scrollbar.set)
scroll_canvas.bind('<Configure>', lambda e: scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all")))

def on_mousewheel(event):
    scroll_canvas.yview_scroll(int(-1*(event.delta/120)), "units")


scroll_canvas.bind_all("<MouseWheel>", on_mousewheel)


########## Preview frame ##########

preview_label = ttk.Label(page2)
preview_label.pack(fill=BOTH, side=LEFT)
# limit size of canvas to half of the window


########## Mainframe ##########

mainframe = ttk.Frame(scroll_canvas, takefocus=False)
mainframe.pack(fill=BOTH, side=LEFT)
scroll_canvas.create_window((0, 0), window=mainframe, anchor=NW)

mainframe.bind("<FocusIn>", lambda e: mainframe.focus_set())


########## Title ##########

# sets width of the entire frame
filler_frame = ttk.Frame(mainframe, padding=padding)
filler_frame.pack(expand=True, fill=BOTH, side='top')

filler_label = ttk.Label(filler_frame, text="Card generator", font=big_font, borderwidth=borderwidth, anchor=CENTER, width=50)
filler_label.pack(expand=True, fill=BOTH, side='left')

###### navigation frame ##########
navigation_frame = ttk.Frame(mainframe, padding=padding)
navigation_frame.pack(expand=True, fill=BOTH, side='top')

back_button = ttk.Button(navigation_frame, text="Back", command=lambda: go_back(None), style="TButton", takefocus=False)
back_button.pack(side=LEFT, padx=10)

save_button = ttk.Button(navigation_frame, text="Save", command=lambda: main.store_card(c, conn), takefocus=False)
save_button.pack(side=RIGHT)

refresh_preview_button = ttk.Button(navigation_frame, text="Refresh preview", command=lambda: (set_update_prev(), match_vars_to_values()), takefocus=False)
refresh_preview_button.pack(side=RIGHT, padx=10)

########## Name frame ##########
ttk.Separator(mainframe, orient=HORIZONTAL).pack(expand=True, fill=BOTH)

name_frame = ttk.Frame(mainframe, padding=padding)
name_frame.pack(expand=True, fill=BOTH, side='top')

# name label
card_name = ttk.Label(name_frame, text="Card name:", borderwidth=borderwidth)
card_name.pack(expand=True, fill=BOTH, side='left')

# name change function
def reset_name():
    name_var.set(values['name'])
    set_update_prev(False)

def change_name():

    values['name'] = name_var.get()
    values['name'] = "".join(c for c in values['name'] if c.isalpha())
    if values['name'] == '': values['name'] = 'nameless'  
    if values['name'] != 'nameless': name_var.set(values['name'])
    set_update_prev()

# name entry
name_var = StringVar()
name_entry = ttk.Entry(name_frame, textvariable=name_var, takefocus=False)
name_entry.pack(expand=True, fill=BOTH, side='left')
name_var.trace_add('write', lambda *args: change_name())

########## HP frame ##########   
hp_label = ttk.Label(name_frame, text="HP:", borderwidth=borderwidth)
hp_label.pack(expand=True, fill=BOTH, side='left')

# hp change function
def reset_hp():
    hp_var.set(values['hp'])
    set_update_prev(False)

def change_hp():
    character_limit(hp_var, 1, 500)
    values['hp'] = hp_var.get()
    if values['hp'] == '': values['hp'] = '0'
    set_update_prev()

# hp entry and limiter
hp_var = StringVar()
spin = ttk.Entry(name_frame, textvariable=hp_var, width=3, takefocus=False)
spin.pack(expand=True, fill=BOTH, side='left')

hp_entry = classes.Limiter(name_frame,
                          variable=hp_var,
                          orient=HORIZONTAL,
                          takefocus=False,
                          from_=0,
                          to=500,
                          precision=1)
hp_var.trace_add('write', lambda *args: change_hp())

hp_entry.pack(expand=True, fill=BOTH, side='left')
hp_entry.pack(expand=True, fill=BOTH, side='left')


########## Evolution frame ##########
evo_frame = ttk.Frame(mainframe, padding=padding)
evo_frame.pack(expand=True, fill=BOTH, side='top')

# evo label
evo_name = ttk.Label(evo_frame, text="Previous stage name:", borderwidth=borderwidth)
evo_name.pack(expand=True, fill=BOTH, side='left')

# evo change function
def reset_evo():
    if 'prevolve'in values: evo_var.set(values['prevolve'])
    else: evo_var.set('')
    set_update_prev(False)

def change_evo():
    values['prevolve'] = evo_var.get()
    if values['prevolve'] == '': values.pop('prevolve', None)
    set_update_prev()

# evo entry
evo_options = search_cards("")

evo_var = StringVar()

evo_entry = ttk.Combobox(evo_frame, textvariable=evo_var, values=evo_options, font=mid_font, takefocus=False)
evo_entry.pack(expand=True, fill=BOTH, side='left')
evo_entry.bind("<KeyRelease>", lambda event: evo_entry.configure(values=search_cards(evo_entry.get())))
evo_var.trace_add('write', lambda *args: change_evo())


########## Rarity frame ##########
ttk.Separator(mainframe, orient=HORIZONTAL).pack(expand=True, fill=BOTH)

rarity_frame = ttk.Frame(mainframe, padding=padding)
rarity_frame.pack(expand=True, fill=BOTH, side='top')

tiers = ["Common", "Uncommon", "Rare", "Unique"]
x = IntVar()

# rarity label
ttk.Label(rarity_frame, text="Rarity:", borderwidth=borderwidth).pack(expand=True, fill=BOTH, side='left')

# rarity change function
def reset_rarity():
    rarity_var.set(values['rarity'])
    set_update_prev(False)

def change_rarity():
    values["rarity"] = rarity_var.get()
    set_update_prev()

# rarity buttons
rarity_var = StringVar()
rarity_var.set(tiers[0].lower())
for index in range(len(tiers)):
    rarity_select = ttk.Radiobutton(rarity_frame,
                              text=tiers[index],
                              variable=rarity_var,
                              value=tiers[index].lower()
                              )
    rarity_select.pack(expand=True, fill=BOTH, side='left')
rarity_var.trace_add('write', lambda *args: change_rarity())


########## Card type frame ##########
type_frame = ttk.Frame(mainframe, padding=padding)
type_frame.pack(expand=True, fill=BOTH, side='top')

card_types = values['existing types']
card_types.append('none')
types_dict = {}
volatile_types_dict = {}
initial_icon_size = 30
type_var = StringVar()
type_var.set(card_types[0])

type_images = []
volatile_type_images = []
resized_images = []

def reset_type():
    global values
    types = values['type']

    type_var.set(types[0])
    if len(types) == 2 and types[1] != 'none' and types[0] != types[1]:
        type_var2.set(types[1])
    else:
        type_var2.set('none')
    set_update_prev(False)

def change_type():
    if (type_var.get() == type_var2.get() and type_var.get() != 'none') or (type_var2.get() == 'none'):
        values['type'] = [type_var.get()]
    elif type_var.get() == 'none' and type_var2.get() != 'none':
        values['type'] = [type_var2.get()]
    else:
        values['type'] = [type_var.get(), type_var2.get()]
    set_update_prev()

# type 1 label
ttk.Label(type_frame, text="Type 1:", borderwidth=borderwidth).grid(column=0, row=0, sticky=NSEW)
type_frame.columnconfigure(0,weight=1)

# type 1 buttons
type_icons = []
type_select = []
for index in range(len(card_types)):
    if index != len(card_types)-1:
        type_images.append(main.get_asset("Energy " + card_types[index]))
        volatile_type_images.append(main.get_asset("Energy " + card_types[index] + " volatile"))
    else:
        type_images.append(main.get_asset("none"))
        volatile_type_images.append(main.get_asset("none"))	

    type_images[index] = Image.open(io.BytesIO(type_images[index]))
    resized_images.append(type_images[index].resize((initial_icon_size,initial_icon_size), resample=0))
    types_dict[card_types[index]] = ImageTk.PhotoImage(resized_images[index])

    volatile_type_images[index] = Image.open(io.BytesIO(volatile_type_images[index]))
    volatile_types_dict[card_types[index]] = ImageTk.PhotoImage(volatile_type_images[index].resize((initial_icon_size,initial_icon_size), resample=0))

    type_select.append(Radiobutton(type_frame,
                              variable=type_var,
                              value=card_types[index],
                              image=types_dict[card_types[index]],
                              foreground='Black',
                              background=background_color,
                              activebackground=background_color,
                              activeforeground='black',
                              indicatoron=False,
                              selectcolor=second_background_color
                              ))
    type_select[index].grid(row=0, column=index+1, sticky=NSEW)
    type_frame.columnconfigure(index+1,weight=1)
    type_frame.rowconfigure(0,weight=1)
type_var.trace_add('write', lambda *args: change_type())

# type 2 label
ttk.Label(type_frame, text="Type 2:", borderwidth=borderwidth).grid(column=0, row=1, sticky=NSEW)

# type 2 buttons
type2_select = []
type_var2 = StringVar()
type_var2.set(card_types[-1])
for index in range(len(card_types)):
    type2_select.append(Radiobutton(type_frame,
                              variable=type_var2,
                              value=card_types[index],
                              image=types_dict[card_types[index]],
                              foreground='Black',
                              background=background_color,
                              activebackground=background_color,
                              activeforeground='black',
                              indicatoron=False,
                              selectcolor=second_background_color
                              ))
    type2_select[index].grid(row=1, column=index+1, sticky=NSEW)
    type_frame.columnconfigure(index+1,weight=1)
    type_frame.rowconfigure(1,weight=1)
type_var2.trace_add('write', lambda *args: change_type())


############### Moves frame ###############
add_subtract_frame = ttk.Frame(mainframe, padding=padding)
add_subtract_frame.pack(expand=True, fill=BOTH, side='top')

def add_move(update=True):
    global move_count
    global limit
    global ind_move_frame
    if move_count < limit:
        move_count += 1
        mainframe.rowconfigure(3,weight=move_count*3)
        ind_move_frame[move_count - 1].pack(expand=True, fill=BOTH)

    change_moves(update)
    if update: set_update_canv()


def subtract_move(update=True):
    global move_count
    global limit
    global ind_move_frame
    
    if move_count > 1:
        move_count -= 1
        mainframe.rowconfigure(3,weight=move_count*3)
        ind_move_frame[move_count].pack_forget()

    change_moves(update)
    if update: set_update_canv()

# buttons to add and subtract moves
ttk.Button(add_subtract_frame, text="+", command=add_move, takefocus=False).pack(expand=True, fill=BOTH, side='left')
ttk.Button(add_subtract_frame, text="-", command=subtract_move, takefocus=False).pack(expand=True, fill=BOTH, side='left')

# move variables
move_var = []
damage_var = []
damage_type_var = []
move_desc_var = []
move_costs = []
move_types_dict = {}
volatile_move_types_dict = {}
for index in range(len(card_types)):
    move_types_dict[card_types[index]] = 0
    volatile_move_types_dict[f"{card_types[index]} volatile"] = 0

# combine move type dicts into move_types_dict
for key in volatile_move_types_dict:
    move_types_dict[key] = volatile_move_types_dict[key]

total_cost = []

move_description_entry = []
move_name_entry = []
damage_entry = []
damage_type_entry = []
move_cost_buttons = []

ind_move_frame = []
toggle_move_type_button = []

move_description_label = []
move_damage_label = []
move_name_label = []
move_cost_label = []
move_type_label = []

move_name_frame = []
move_description_frame = []
move_damage_frame = []
move_type_frame = []
move_cost_frame = []
selected_cost_frame = []

# change moves function
def reset_moves():
    global values
    global update_canv
    global move_count
    
    new_move_count = 0

    init_values = values.copy()

    ability_count = 0
    for nr in range(0, limit):
        if f"ability {nr+1} name" in init_values:
            if nr+1 > move_count:
                add_move(False)
            if toggle_move_type_button[nr]['text'] == 'Move':
                toggle_button_type(nr, False)
            move_var[nr].set(init_values[f"ability {nr+1} name"])
            ability_count = nr+1

        if f"ability {nr+1} desc" in init_values:
            if nr+1 > move_count:
                add_move(False)
            if toggle_move_type_button[nr]['text'] == 'Move':
                toggle_button_type(nr, False)
            move_desc_var[nr].set(init_values[f"ability {nr+1} desc"])
            ability_count = nr+1

    for nr in range(0, limit):
        if f"move {nr+1} name" in init_values and init_values[f"move {nr+1} name"] != '':
            if ability_count + nr + 1 > move_count:
                add_move(False)
            if toggle_move_type_button[nr+ability_count]['text'] == 'Ability':
                toggle_button_type(nr+ability_count, False)
            move_var[nr+ability_count].set(init_values[f"move {nr+1} name"])
            new_move_count = ability_count + nr + 1

            if f"move {nr+1} damage" not in init_values:
                damage_var[nr+ability_count].set('')
                damage_type_var[nr+ability_count].set('neutral')

        if f"move {nr+1} damage" in init_values and init_values[f"move {nr+1} damage"] != '':
            if ability_count + nr + 1 > move_count:
                add_move(False)
            if toggle_move_type_button[nr+ability_count]['text'] == 'Ability':
                toggle_button_type(nr+ability_count, False)
            damage_var[nr+ability_count].set(init_values[f"move {nr+1} damage"].split()[0])
            damage_type_var[nr+ability_count].set(init_values[f"move {nr+1} damage"].split()[1])
            new_move_count = ability_count + nr + 1

        if f"move {nr+1} desc" in init_values and init_values[f"move {nr+1} desc"] != '':
            if ability_count + nr + 1 > move_count:
                add_move(False)
            if toggle_move_type_button[nr+ability_count]['text'] == 'Ability':
                toggle_button_type(nr+ability_count, False)
            move_desc_var[nr+ability_count].set(init_values[f"move {nr+1} desc"])
            new_move_count = ability_count + nr + 1

        if f"move {nr+1} cost" in init_values and init_values[f"move {nr+1} cost"] != '':
            if ability_count + nr + 1 > move_count:
                add_move(False)
            if toggle_move_type_button[nr+ability_count]['text'] == 'Ability':
                toggle_button_type(nr+ability_count, False)
            new_move_count = ability_count + nr + 1

            costs = init_values[f"move {nr+1} cost"]
            move_cost_reset(nr+ability_count)  
            for cost in costs:
                count = int(cost.split()[0])
                type = cost.split()[1]
                volatile = len(cost.split()) == 3
                for index in range(len(card_types)-1):
                    if type == card_types[index]:
                        for j in range(count):
                            move_cost_update(nr+ability_count, index + volatile * len(card_types), False)

    if move_count > new_move_count:
        for i in range(move_count - new_move_count):
            subtract_move(False)

    values = init_values

    set_update_prev(False)
    set_update_canv()

def change_moves(update=True): # save moves and abilities to values
    global values
    
    abilities = 0
    moves = 0
    for nr in range(0, limit): 
        # see if the move belongs to any other card as well, then ask to overwrite or use existing
        c.execute("""SELECT moveName FROM get_moves WHERE name != ? AND moveName = ?""", (values['name'], move_var[nr].get()) )
        results = c.fetchall()
        pre_existing_move = len(results) > 0
        #TODO: add move regeneration


        if toggle_move_type_button[nr]['text'] == 'Move':
            moves += 1
            if nr>=move_count:
                values.pop(f"move {moves} name", None)
                values.pop(f"move {moves} damage", None)
                values.pop(f"move {moves} desc", None) 
                values.pop(f"move {moves} cost", None)
                continue
            values[f"move {moves} name"] = move_var[nr].get()
            if values[f"move {moves} name"] == '': values[f"move {moves} name"] = 'moveless'
            if damage_var[nr].get() != "0" and damage_var[nr].get() != '':
                values[f"move {moves} damage"] = str(damage_var[nr].get()) + " " + damage_type_var[nr].get()
            else:
                values.pop(f"move {moves} damage", None)
            values[f"move {moves} desc"] = move_desc_var[nr].get()
            if values[f"move {moves} desc"] == '': values[f"move {moves} desc"] = 'no description'
            
            values[f"move {moves} cost"] = []
            for key in move_costs[nr]:
                if move_costs[nr][key] != 0:
                    values[f"move {moves} cost"].append(str(move_costs[nr][key]) + " " + key)

            if values[f"move {moves} cost"] == []: values[f"move {moves} cost"].append('0 none')

        if toggle_move_type_button[nr]['text'] == 'Ability':
            abilities += 1
            if nr>=move_count:
                values.pop(f"ability {abilities} name", None)
                values.pop(f"ability {abilities} desc", None)   
                continue
            values[f"ability {abilities} name"] = move_var[nr].get()
            if values[f"ability {abilities} name"] == '': values[f"ability {abilities} name"] = 'abilityless'
            values[f"ability {abilities} desc"] = move_desc_var[nr].get()
            if values[f"ability {abilities} desc"] == '': values[f"ability {abilities} desc"] = 'no description'

    for nr in range(0, limit):
        moves += 1
        abilities += 1
        values.pop(f"move {moves} name", None)
        values.pop(f"move {moves} damage", None)
        values.pop(f"move {moves} desc", None)
        values.pop(f"move {moves} cost", None)
        values.pop(f"ability {abilities} name", None)
        values.pop(f"ability {abilities} desc", None)  

    set_update_prev(update)

# toggle move type function
def toggle_button_type(nr, update=True):
    global toggle_move_type_button

    if toggle_move_type_button[nr]['text'] == 'Move':
        toggle_move_type_button[nr].config(text='Ability')
        move_damage_frame[nr].pack_forget()
        move_type_frame[nr].pack_forget()
        move_cost_frame[nr].pack_forget()
        selected_cost_frame[nr].pack_forget()
    else:
        toggle_move_type_button[nr].config(text='Move')
        move_damage_frame[nr].pack(expand=True, fill=BOTH)
        move_type_frame[nr].pack(expand=True, fill=BOTH)
        move_cost_frame[nr].pack(expand=True, fill=BOTH)
        selected_cost_frame[nr].pack(expand=True, fill=BOTH)

    ability_number = 0
    move_number = 0
    for j in range(0, limit):
        if toggle_move_type_button[j]['text'] == 'Ability':
            ability_number += 1
            move_description_label[j].config(text="Ability " + str(ability_number) + " description:")
            move_name_label[j].config(text=str(ability_number) + " name:")
        else:
            move_number += 1
            move_description_label[j].config(text="Move " + str(move_number) + " description:")
            move_damage_label[j].config(text="Move " + str(move_number) + " damage:")
            move_name_label[j].config(text=str(move_number) + " name:")
            move_cost_label[j].config(text="Move " + str(move_number) + " cost:")
            move_type_label[j].config(text="Move " + str(move_number) + " type:")
    
    change_moves()
    if update: set_update_canv()

buttons = []

def move_cost_reset(nr):
    global move_costs
    global total_cost
    global buttons

    for key in move_costs[nr]:
        move_costs[nr][key] = 0
    total_cost[nr] = 0

    for i in range(len(buttons)-1, -1, -1):
        button = buttons[i]
        if button[1] == nr:
            button[0].destroy()
            buttons.pop(i)

def move_cost_update(nr, index, update=True):
    global move_costs
    global card_types
    global total_cost
    global buttons

    if index != len(card_types)-1 and total_cost[nr] < 8:
        total_cost[nr] += 1

        if index < len(card_types):
            move_costs[nr][card_types[index]] = int(move_costs[nr][card_types[index]])+1
            btn = ttk.Button(selected_cost_frame[nr], takefocus=False, image=types_dict[card_types[index]])
            move_cost_buttons.append(btn)
            btn['command'] = lambda button=btn, a=nr, type=card_types[index]: remove_button(button, nr, type)
            btn.pack(side=LEFT)

            buttons.append([btn, nr, card_types[index]])

        else:
            move_costs[nr][f"{card_types[index-len(card_types)]} volatile"] = int(move_costs[nr][f"{card_types[index-len(card_types)]} volatile"])+1
            btn = ttk.Button(selected_cost_frame[nr], takefocus=False, image=volatile_types_dict[card_types[index-len(card_types)]])
            move_cost_buttons.append(btn)
            btn['command'] = lambda button=btn, a=nr, type=f"{card_types[index - len(card_types)]} volatile": remove_button(button, nr, type)
            btn.pack(side=LEFT)

            buttons.append([btn, nr, f"{card_types[index-len(card_types)]} volatile"])


        if update: set_update_canv()
    
    change_moves()

def remove_button(button, nr, type, update=True):
    global move_costs
    global total_cost
    global buttons

    total_cost[nr] -= 1
    move_costs[nr][type] = int(move_costs[nr][type])-1
    
    buttons.remove([button, nr, type])
    button.destroy()

    if update: set_update_canv()

    change_moves()

move_frame = ttk.Frame(mainframe, padding=padding*3)
move_frame.pack(expand=True, fill=BOTH, side='top')

move_options = search_moves('')

for i in range(0, limit):
    ind_move_frame.append(ttk.Frame(move_frame, padding=padding*2))
    ind_move_frame[i].pack(expand=True, fill=BOTH)

    # collapsible frames
    move_name_frame.append(ttk.Frame(ind_move_frame[i], padding=padding))
    move_name_frame[i].pack(expand=True, fill=BOTH)
    move_description_frame.append(ttk.Frame(ind_move_frame[i], padding=padding))
    move_description_frame[i].pack(expand=True, fill=BOTH)
    move_damage_frame.append(ttk.Frame(ind_move_frame[i], padding=padding))
    move_damage_frame[i].pack(expand=True, fill=BOTH)
    move_type_frame.append(ttk.Frame(ind_move_frame[i], padding=padding))
    move_type_frame[i].pack(expand=True, fill=BOTH)
    move_cost_frame.append(ttk.Frame(ind_move_frame[i], padding=padding))
    move_cost_frame[i].pack(expand=True, fill=BOTH)
    selected_cost_frame.append(ttk.Frame(ind_move_frame[i], padding=padding))
    selected_cost_frame[i].pack(expand=True, fill=BOTH)

    #seperator
    ttk.Separator(ind_move_frame[i], orient=HORIZONTAL).pack(expand=True, fill=BOTH)

    # name
    toggle_move_type_button.append(ttk.Button(move_name_frame[i], text='Move', command=lambda a=i: toggle_button_type(a), takefocus=False))
    toggle_move_type_button[i].grid(row=0, column=0, sticky=NSEW)
    move_name_frame[i].columnconfigure(0, weight=1)
    move_name_frame[i].rowconfigure(0, weight=1)


    move_name_label.append(ttk.Label(move_name_frame[i], text=str(i + 1) + " name:", borderwidth=borderwidth))
    move_name_label[i].grid(row=0, column=1, sticky=NSEW)
    move_name_frame[i].columnconfigure(1, weight=1)
    move_name_frame[i].rowconfigure(0, weight=1)


    move_var.append(StringVar())
    move_name_entry.append(ttk.Combobox(move_name_frame[i], textvariable=move_var[i], values=move_options, takefocus=False))
    move_name_entry[i].bind("<KeyRelease>", lambda event: evo_entry.configure(values=search_moves(move_var[i].get())))
    move_var[i].trace_add('write', lambda *args: change_moves())
    move_name_entry[i].grid(row=0, column=2, sticky=NSEW)
    move_name_frame[i].columnconfigure(2, weight=1)
    move_name_frame[i].rowconfigure(0, weight=1)

    # damage
    move_damage_label.append(ttk.Label(move_damage_frame[i], text="Move " + str(i + 1) + " damage:", borderwidth=borderwidth))
    move_damage_label[i].grid(row=0, column=0, sticky=NSEW)
    move_damage_frame[i].columnconfigure(0, weight=1)
    move_damage_frame[i].rowconfigure(0, weight=1)


    damage_var.append(StringVar())
    spin = ttk.Entry(move_damage_frame[i], textvariable=damage_var[i], width=3, takefocus=False)
    spin.grid(row=0, column=1, sticky=NSEW)
    move_damage_frame[i].columnconfigure(1, weight=1)
    def damage_change(a):
        character_limit(damage_var[a], 1, 300)
        change_moves()

    damage_entry.append(classes.Limiter(move_damage_frame[i],
                            variable=damage_var[i],
                            orient=HORIZONTAL,
                            takefocus=False,
                            from_=0,
                            to=300,
                            precision=1))
    damage_var[i].trace_add('write', lambda *args, a=i: damage_change(a))

    damage_entry[i].grid(row=0, column=2, sticky=NSEW)
    move_damage_frame[i].columnconfigure(2, weight=1)
    move_damage_frame[i].rowconfigure(0, weight=1)

    move_type_label.append(
        ttk.Label(move_type_frame[i], text="Move " + str(i + 1) + " type:", borderwidth=borderwidth))
    move_type_label[i].grid(row=0, column=0, sticky=NSEW)
    move_type_frame[i].columnconfigure(0,weight=1)
    move_type_frame[i].rowconfigure(0,weight=1)

    damage_type_entry.append([],)
    damage_type_var.append(StringVar())
    damage_type_var[i].set(card_types[0])
    for index in range(len(card_types)-1):
        damage_type_entry[i].append(Radiobutton(move_type_frame[i],
                                variable=damage_type_var[i],
                                value=card_types[index],
                                image=types_dict[card_types[index]],
                                foreground='Black',
                                background=background_color,
                                activebackground=background_color,
                                activeforeground='black',
                                indicatoron=False,
                                selectcolor=second_background_color
                                ))
        damage_type_entry[i][index].grid(row=0, column=index+1, sticky=NSEW)
        move_type_frame[i].columnconfigure(index+1, weight=1)
        move_type_frame[i].rowconfigure(1,weight=1)
    damage_type_var[i].trace_add('write', lambda *args: change_moves())
    
    # description
    move_description_label.append(ttk.Label(move_description_frame[i], text="Move " + str(i + 1) + " description:", borderwidth=borderwidth))
    move_description_label[i].grid(row=0, column=0, sticky=NSEW)
    move_description_frame[i].columnconfigure(0, weight=1)
    move_description_frame[i].rowconfigure(0, weight=1)

    move_desc_var.append(StringVar())
    move_description_entry.append(ttk.Entry(move_description_frame[i], textvariable=move_desc_var[i], takefocus=False))
    move_desc_var[i].trace_add('write', lambda *args: change_moves())
    move_description_entry[i].grid(row=0, column=1, sticky=NSEW)
    move_description_frame[i].columnconfigure(1, weight=1)
    move_description_frame[i].rowconfigure(0, weight=1)

    # cost
    ttk.Label(move_cost_frame[i], text="Add cost:", borderwidth=borderwidth).grid(row=0, column=0, sticky=NSEW)
    move_cost_frame[i].columnconfigure(0,weight=1)
    move_cost_frame[i].rowconfigure(0,weight=1)

    move_costs.append(move_types_dict.copy())
    total_cost.append(0)
    for index in range(len(card_types)-1):
        cost_button = ttk.Button(move_cost_frame[i], takefocus=False, image=types_dict[card_types[index]], command=lambda a=i, b=index: move_cost_update(a, b))
                                
        cost_button.grid(row=0, column=index+1, sticky=NSEW)
        move_cost_frame[i].columnconfigure(index+1, weight=1)
        move_cost_frame[i].rowconfigure(0,weight=1)

    # volatile cost
    ttk.Label(move_cost_frame[i], text="Add volatile cost:", borderwidth=borderwidth).grid(row=1, column=0, sticky=NSEW)
    move_cost_frame[i].columnconfigure(0,weight=1)
    move_cost_frame[i].rowconfigure(1,weight=1)

    total_cost.append(0)
    for index in range(len(card_types)-1):
        cost_button = ttk.Button(move_cost_frame[i], takefocus=False, image=volatile_types_dict[card_types[index]], command=lambda a=i, b=index+len(card_types): move_cost_update(a, b))
                                
        cost_button.grid(row=1, column=index+1, sticky=NSEW)
        move_cost_frame[i].columnconfigure(index+1, weight=1)
        move_cost_frame[i].rowconfigure(1,weight=1)

    move_cost_label.append(ttk.Label(selected_cost_frame[i], text="Move " + str(i + 1) + " cost:", borderwidth=borderwidth))
    move_cost_label[i].pack(side=LEFT)

    if i != 0:
        ind_move_frame[i].pack_forget()

########## End of moves ##########


########## Retreat frame ##########
retreat_frame = ttk.Frame(mainframe, padding=padding)
retreat_frame.pack(expand=True, fill=BOTH, side='top')  

# retreat label
ttk.Label(retreat_frame, text="Retreat cost:", borderwidth=borderwidth).pack(expand=True, fill=BOTH, side='left')

# retreat change function
def reset_retreat():
    retreat_var.set(values['retreat'])
    set_update_prev(False)

def change_retreat():
    character_limit(retreat_var, 0, 7)
    values["retreat"] = retreat_var.get()
    if values["retreat"] == '': values["retreat"] = '0'
    set_update_prev()

# retreat entry and limiter
retreat_var = StringVar()
spin = ttk.Entry(retreat_frame, textvariable=retreat_var, width=1, takefocus=False)
spin.pack(expand=True, fill=BOTH, side='left')

retreat_entry = classes.Limiter(retreat_frame,
                          variable=retreat_var,
                          orient=HORIZONTAL,
                          from_=0,
                          to=7,
                          precision=0,
                          takefocus=False)
retreat_entry.pack(expand=True, fill=BOTH, side='left')
retreat_var.trace_add('write', lambda *args: change_retreat())


########## Description frame ##########
description_frame = ttk.Frame(mainframe, padding=padding)
description_frame.pack(expand=True, fill=BOTH, side='top')

# description label
ttk.Label(description_frame, text="Card description:", borderwidth=borderwidth).pack(expand=True, fill=BOTH, side='left')

# description change function
def reset_desc():
    desc_var.set(values['description'])
    set_update_prev(False)

def change_desc():
    values["description"] = desc_var.get()
    if values["description"] == '': values["description"] = 'bitch lasagna'
    set_update_prev()

desc_var = StringVar()
description_entry = ttk.Entry(description_frame, textvariable=desc_var)
description_entry.pack(expand=True, fill=BOTH, side='left')
desc_var.trace_add('write', lambda *args: change_desc())


########## Illustrator frame ##########
illustrator_frame = ttk.Frame(mainframe, padding=padding)
illustrator_frame.pack(expand=True, fill=BOTH, side=TOP)

# illustrator label
ttk.Label(illustrator_frame, text="Card illustrator:", borderwidth=borderwidth).pack(expand=True, fill=BOTH, side='left')

# illustrator change function
def reset_illustrator():
    illustrator_var.set(values['illustrator'])
    set_update_prev(False)

def change_illustrator():
    values["illustrator"] = illustrator_var.get()
    if values["illustrator"] == '': values["illustrator"] = 'no illustrator'
    set_update_prev()

# illustrator entry
illustrator_var = StringVar()
illustrator_entry = ttk.Entry(illustrator_frame, textvariable=illustrator_var).pack(expand=True, fill=BOTH, side='left')
illustrator_var.trace_add('write', lambda *args: change_illustrator())


########## Card index frame ##########
index_frame = ttk.Frame(mainframe, padding=padding)
index_frame.pack(expand=True, fill=BOTH, side=TOP)

ttk.Label(index_frame, text="Card index:", borderwidth=borderwidth).pack(expand=True, fill=BOTH, side='left')

index_var = StringVar()
index_entry = ttk.Entry(index_frame, textvariable=index_var)
index_entry.pack(expand=True, fill=BOTH, side='left')

def reset_index():
    index_var.set(values['entry'])
    set_update_prev(False)

def change_index():
    character_limit(index_var, 0)
    values["entry"] = index_var.get()
    if values["entry"] == '': values["entry"] = '0'
    set_update_prev()
index_var.trace_add('write', lambda *args: change_index())


########## Crop image ##########
crop_frame = ttk.Frame(mainframe, padding=padding)
crop_frame.pack(expand=True, fill=BOTH, side='top')

scoped_image = None

def import_image(path=None, update=True):   
    global values
    global image
    global rect
    global card_image
    global scoped_image
    global update_canv
    
    if path is None:
        use_this_path = filedialog.askopenfilename(initialdir=f"{os.getcwd()}", title="Select file", filetypes=(("png files", "*.png"), ("all files", "*.*")))
    else:
        use_this_path = path
    if use_this_path is None: return

    
    card_image = Image.open(use_this_path)
    if card_image.mode != 'RGBA':
        card_image = card_image.convert('RGBA')
    
    # add to canvas
    scale = card_image.width/crop_frame.winfo_width()
    card_image = card_image.resize((crop_frame.winfo_width(), int(card_image.height/scale)), resample=0)
    canvas.config(height=card_image.height)
    localphoto = ImageTk.PhotoImage(card_image)
    canvas.itemconfig(image, image=localphoto)
    scoped_image = localphoto


    # add rectangle to canvas to show where the image will be cropped
    unique_size = (727, 1013)
    normal_size = (607, 375)

    if 'rarity' in values and values['rarity'] == 'unique':
        aspect_ratio = unique_size[1]/unique_size[0]
    else:
        aspect_ratio = normal_size[1]/normal_size[0]

    canvas.coords(rect, 0, 0, 100, 100*aspect_ratio)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<B3-Motion>", on_move_drag)
    canvas.bind("<ButtonRelease-1>", lambda event: set_update_prev())
    canvas.bind("<ButtonRelease-3>", lambda event: set_update_prev())

    # convert card image to blob
    values['image'] = io.BytesIO()
    card_image.save(values['image'], format='PNG')
    values['image'] = values['image'].getvalue()
    
    set_update_canv()
    set_update_prev(update)

#### seperating line ####
ttk.Separator(crop_frame, orient=HORIZONTAL).pack(expand=True, fill=BOTH, side='top')

##### instructions #####
instructions = ttk.Label(crop_frame, text="Right click and drag to move the rectangle\nLeft click and drag to resize the rectangle",anchor=CENTER, borderwidth=borderwidth)
instructions.pack(expand=True, fill=BOTH)

##### import image button #####
import_button = ttk.Button(crop_frame, text="Import image", command=import_image, takefocus=False)
import_button.pack(expand=True, fill=BOTH)

##### Image canvas #####
canvas = Canvas(crop_frame, width=90, height=400, background=background_color)
canvas.pack(expand=True, fill=BOTH)

card_image = Image.open(io.BytesIO(main.get_asset('nameless', c)))
image = canvas.create_image(0, 0, anchor=NW, tag='photo')
rect = canvas.create_rectangle(0, 0, 0, 0, outline='black', width=2)

def reset_rect():
    global values
    global rect

    if 'crop' in values: canvas.coords(rect, values['crop'][0], values['crop'][1], values['crop'][2], values['crop'][3])
    set_update_prev(False)

# make rectangle draggable
def on_move_drag(event):
    global values
    global rect

    x, y = event.x, event.y

    rectx = canvas.coords(rect)[0]
    recty = canvas.coords(rect)[1]
    rectx2 = canvas.coords(rect)[2]
    recty2 = canvas.coords(rect)[3]

    unique_size = (727, 1013)
    normal_size = (607, 375)

    if 'rarity' in values and values['rarity'] == 'unique':
        aspect_ratio = unique_size[1]/unique_size[0]
    else:
        aspect_ratio = normal_size[1]/normal_size[0]

    width = max(rectx2-rectx, 50)
    height = int(width*aspect_ratio)

    rectx2 = rectx+width
    recty2 = recty+height

    rectwidth = rectx2-rectx
    rectheight = recty2-recty
    
    if rectheight > canvas.winfo_height():
        recty2 = int(canvas.winfo_height())
        height = recty2-recty
        rectx2 = int(rectx+height/aspect_ratio)

    if rectwidth > canvas.winfo_width():
        rectx2 = int(canvas.winfo_width())
        width = rectx2-rectx
        recty2 = int(recty+width*aspect_ratio)

    rectwidth = rectx2-rectx
    rectheight = recty2-recty
    

    x = int(max(1, min(x, canvas.winfo_width()-rectwidth-1)))
    y = int(max(1, min(y, canvas.winfo_height()-rectheight-1)))

    canvas.coords(rect, x, y, x+rectwidth, y+rectheight)

    # crop image
    values['crop'] = (x, y, int(x+rectwidth), int(y+rectheight))

    set_update_prev()

def on_drag(event):
    global values
    global rect
    
    x, y = event.x, event.y
    rectx = canvas.coords(rect)[0]
    recty = canvas.coords(rect)[1]
    rectx2 = canvas.coords(rect)[2]
    recty2 = canvas.coords(rect)[3]
    
    unique_size = (727, 1013)
    normal_size = (607, 375)

    if 'rarity' in values and values['rarity'] == 'unique':
        aspect_ratio = unique_size[1]/unique_size[0]
    else:
        aspect_ratio = normal_size[1]/normal_size[0]

    rectx2 = min(x, canvas.winfo_width())

    width = max(rectx2-rectx, 50)
    height = int(width*aspect_ratio)

    rectx2 = rectx+width
    recty2 = recty+height

    if recty2 > canvas.winfo_height():
        recty2 = int(canvas.winfo_height())
        height = recty2-recty
        rectx2 = int(rectx+height/aspect_ratio)

    canvas.coords(rect, rectx, recty, rectx2, recty2)

    values['crop'] = (int(rectx), int(recty), int(rectx2), int(recty2))

    set_update_prev()

########## End of GUI ##########
update_prev = False
window.update()

# start the canvas at the top
scroll_canvas.yview_moveto(0)
scroll_canvas.xview_moveto(0)


####### Initialise width of window to be the same as the frame #######
width = mainframe.winfo_width()+scrollbar.winfo_width()+preview_label.winfo_width()
height = min(mainframe.winfo_height(), 600)
scroll_canvas.configure(width=mainframe.winfo_width(), height=height)
scroll_canvas.configure(scrollregion=(0, 0, mainframe.winfo_width(), height))

####### start the update thread #######
update_thread.start()

## window mainloop ##
window.update()

update_canv = False
update_prev = False

window.mainloop()