from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter.font import nametofont
import ctypes
import os
import re
from tkinter.font import Font
import main
import classes
from PIL import ImageTk, Image
import sv_ttk
import threading
import time

values = {}
file_path = "card files/"
assets_path = "assets/"
storage_path = "generated cards/"
background_color = "#424549"
text_color = "#99aab5"
second_background_color = "#36393e"

# save file
previous_name = ''

allow_save = True

def save_file(overwrite=False, from_close=False, *args):
    global previous_name
    global move_count
    global toggle_move_type_button
    global values

    window.update()

    values["name"] = name_var.get()
    if values["name"] == '': values["name"] = 'nameless'
    if evo_var.get() != '': values["prev stage"] = evo_var.get()

    values["rarity"] = rarity_var.get()

    if (type_var.get() == type_var2.get() and type_var.get() != 'none') or (type_var2.get() == 'none'):
        values['type'] = [type_var.get()]
    elif type_var.get() == 'none' and type_var2.get() != 'none':
        values['type'] = [type_var2.get()]
    else:
        values['type'] = [type_var.get(), type_var2.get()]

    values["description"] = desc_var.get()
    if values["description"] == '': values["description"] = 'bitch lasagna'
    values["illustrator"] = illustrator_var.get()
    if values["illustrator"] == '': values["illustrator"] = 'no illustrator'
    values["entry"] = index_var.get()
    if values["entry"] == '': values["entry"] = '0'
    values["retreat"] = retreat_var.get()
    if values["retreat"] == '': values["retreat"] = '0'
    values["hp"] = hp_var.get()
    if values["hp"] == '': values["hp"] = '0'
    if 'image' not in values:
        values['image'] = Image.open(assets_path + "nameless.jpg")

    abilities = 0
    moves = 0
    for nr in range(0, limit):  
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
            for index in range(len(moods)-1):
                if move_costs[nr][moods[index]] != 0:
                    values[f"move {moves} cost"].append(str(move_costs[nr][moods[index]]) + " " + moods[index])
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

    if allow_save or overwrite:
        if values['name'] not in ('', ' '):
            if from_close:
                f = open(file_path + 'recovered.txt', "w+")
            else: f = open(file_path + values['name'] + '.txt', "w+")
            for key in values:
                if key == 'image': continue
                if type(values[key]) == list:
                    f.write(f'{key}: {values[key][0]}')
                    for i in range(1, len(values[key])):
                        f.write(f', {values[key][i]}')
                    f.write('\n')
                else: f.write(f'{key}: {values[key]}\n')
            f.close()
            if 'image' in values and (overwrite or from_close):
                values['image'].save(file_path + values['name'] + '.png')

        if previous_name != '' and previous_name != values['name']: os.remove(file_path + previous_name + '.txt')
        previous_name = values["name"]
        
    update_preview()


def on_closing():
    try: save_file(True, True)
    except: "error saving file"
    window.destroy()

def toggle_auto_save(state = None):
    global allow_save
    if state != None:
        allow_save = not state

    if allow_save:
        enable_auto_save.config(text="Auto save Off")
        allow_save = not allow_save
    else:
        enable_auto_save.config(text="Auto save On")
        allow_save = not allow_save


# functions
move_count = 1
limit = 3

def update_canvas(update=True):
    global move_count
    global limit
    global ind_move_frame

    #get mainframe height
    window.update()
    width = mainframe.winfo_width()
    height = mainframe.winfo_height()
    scroll_canvas.configure(scrollregion=(0, 0, width, height)) 

    if update: save_file()


def add_move(update=True):
    global move_count
    global limit
    global ind_move_frame
    
    if move_count < limit:
        move_count += 1
        mainframe.rowconfigure(3,weight=move_count*3)
        ind_move_frame[move_count - 1].pack(expand=True, fill=BOTH)

    if update: update_canvas()


def subtract_move(update=True):
    global move_count
    global limit
    global ind_move_frame
    
    if move_count > 1:
        move_count -= 1
        mainframe.rowconfigure(3,weight=move_count*3)
        ind_move_frame[move_count].pack_forget()

    if update: update_canvas()


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
    
    if update: update_canvas()


def move_cost_update(nr, index, update=True):
    global move_costs
    global moods
    global total_cost

    if index != len(moods)-1 and total_cost[nr] < 8:
        total_cost[nr] += 1
        move_costs[nr][moods[index]] = int(move_costs[nr][moods[index]])+1

        btn = ttk.Button(selected_cost_frame[nr], takefocus=False, image=types_dict[moods[index]])
        move_cost_buttons.append(btn)
        btn['command'] = lambda button=btn, a=nr, type=moods[index]: remove_button(button, nr, type)
        btn.pack(side=LEFT)

        if update: update_canvas()

def remove_button(button, nr, type, update=True):
    global move_costs
    global total_cost

    total_cost[nr] -= 1
    move_costs[nr][type] = int(move_costs[nr][type])-1
    button.destroy()

    if update: update_canvas()

def open_file():
    global allow_save
    global move_count
    global image
    global card_image

    allow_save = toggle_auto_save(False)

    use_this_path = filedialog.askopenfilename(initialdir=f"{os.getcwd()}\\{file_path}", title="Select file", filetypes=(("text files", "*.txt"), ("all files", "*.*")))
    if use_this_path == '': return
    existing = open(use_this_path, "r")
    old_values = main.generate_dict(existing)
    existing.close()

    if 'name' in old_values and old_values['name'] != '':
        name_var.set(old_values['name'])
        card_image = Image.open(file_path + name_var.get() + '.png')
        scale = card_image.width/mainframe.winfo_width()
        card_image = card_image.resize((int(card_image.width/scale), int(card_image.height/scale)), resample=0)
        canvas.config(width=card_image.width, height=card_image.height)
        localphoto = ImageTk.PhotoImage(card_image)
        canvas.itemconfig(image, image=localphoto)
        canvas.image = localphoto
        values['image'] = card_image
    if 'prev stage' in old_values and old_values['prev stage'] != '':
        evo_var.set(old_values['prev stage'])
    if 'rarity' in old_values and old_values['rarity'] != '':
        rarity_var.set(old_values['rarity'])
    if 'type' in old_values and len(old_values['type']) != 0:
        type_var.set(old_values['type'][0])
        if len(old_values['type']) != 1:
            type_var2.set(old_values['type'][1])
    if 'description' in old_values and old_values['description'] != '':
        desc_var.set(old_values['description'])
    if 'illustrator' in old_values and old_values['illustrator'] != '':
        illustrator_var.set(old_values['illustrator'])
    if 'entry' in old_values and old_values['entry'] != '':
        index_var.set(old_values['entry'])
    if 'retreat' in old_values and old_values['retreat'] != '':
        retreat_var.set(old_values['retreat'])
    if 'hp' in old_values and old_values['hp'] != '':
        hp_var.set(old_values['hp'])
    
    old_move_count = 0
    for nr in range(0, limit):
        if f"ability {nr+1} name" in old_values and old_values[f"ability {nr+1} name"] != '':
            old_move_count = nr+1
            if old_move_count > move_count:
                add_move(False)
            if toggle_move_type_button[old_move_count-1]['text'] == 'Move':
                toggle_button_type(old_move_count-1, False)
            move_var[old_move_count-1].set(old_values[f"ability {nr+1} name"])
        if f"ability {nr+1} desc" in old_values and old_values[f"ability {nr+1} desc"] != '':
            old_move_count = nr+1
            if old_move_count > move_count:
                add_move(False)
            if toggle_move_type_button[old_move_count-1]['text'] == 'Move':
                toggle_button_type(old_move_count-1, False)
            move_desc_var[old_move_count-1].set(old_values[f"ability {nr+1} desc"])

    for nr in range(0, limit):
        i = old_move_count
        if f"move {nr+1} name" in old_values and old_values[f"move {nr+1} name"] != '':
            old_move_count = i+1
            if old_move_count > move_count:
                add_move(False)
            if toggle_move_type_button[old_move_count-1]['text'] == 'Ability':
                toggle_button_type(old_move_count-1, False)
            move_var[old_move_count-1].set(old_values[f"move {nr+1} name"])
        if f"move{nr+1} damage" in old_values and old_values[f"move {nr+1} damage"] != '':
            old_move_count = i+1
            if old_move_count > move_count:
                add_move(False)
            if toggle_move_type_button[old_move_count-1]['text'] == 'Ability':
                toggle_button_type(old_move_count-1, False)
            damage_var[old_move_count-1].set(old_values[f"move {nr+1} damage"].split()[0])
            damage_type_var[old_move_count-1].set(old_values[f"move {nr+1} damage"].split()[1])
        if f"move {nr+1} desc" in old_values and old_values[f"move {nr+1} desc"] != '':
            old_move_count = i+1
            if old_move_count > move_count:
                add_move(False)
            if toggle_move_type_button[old_move_count-1]['text'] == 'Ability':
                toggle_button_type(old_move_count-1, False)
            move_desc_var[old_move_count-1].set(old_values[f"move {nr+1} desc"])
        if f"move {nr+1} cost" in old_values and old_values[f"move {nr+1} cost"] != '':
            old_move_count = i+1
            if old_move_count > move_count:
                add_move(False)
            if toggle_move_type_button[old_move_count-1]['text'] == 'Ability':
                toggle_button_type(old_move_count-1, False)
            costs = old_values[f"move {nr+1} cost"]
            for cost in costs:
                count = int(cost.split()[0])
                type = cost.split()[1]
                for index in range(len(moods)-1):
                    if type == moods[index]:
                        for j in range(count):
                            move_cost_update(old_move_count-1, index, False)
    
    if old_move_count < move_count:
        for nr in range(old_move_count, move_count):
            subtract_move(False)

    update_canvas(False)

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
    save_file()

def resize_font(incr):
    '''Change the size of SunValley fonts by the incr factor '''
    for font_name in (
        "Caption", "Body", "BodyStrong", "BodyLarge",
        "Subtitle", "Title", "TitleLarge", "Display"
    ):
        font = nametofont(f"SunValley{font_name}Font")
        size = font.cget("size")
        font.configure(size=size-incr)

def update_preview():
    global values
    global picture_frame
    global photo
    global preview_label
    global assets_path
    
    height = window.winfo_height()

    image = main.generate_card_from_values(values, editor_mode=True)
    scale = height/image.height
    image = image.resize((int(image.width*scale), int(image.height*scale)), resample=0)
    photo = ImageTk.PhotoImage(image)
    preview_label['image'] = photo

    #resize to fit preview
    window.update()
    width = mainframe.winfo_width()+scrollbar.winfo_width()+picture_frame.winfo_width()
    window.geometry(f"{width}x{height}")


def update_size():
    return


# Window
window = Tk()
style = ttk.Style()
sv_ttk.set_theme("dark")

window_id = "card.generator.window"  # will only work once compiled I think
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(window_id)

small_font = Font(family='Roboto', size=10, weight='bold')
mid_font = Font(family='Roboto', size=15, weight='bold')
big_font = Font(family='Roboto', size=20, weight='bold')

window.title("Card generator")

icon = PhotoImage(file=assets_path + "Energy neutral.png")
window.iconphoto(True, icon)
window.config(background=background_color)

outer_frame = Frame(window, background=background_color)
outer_frame.pack(fill=BOTH, expand=True)

scroll_canvas = Canvas(outer_frame, background=background_color)
scroll_canvas.grid(row=0, column=0, sticky=NSEW)

scrollbar = ttk.Scrollbar(outer_frame,
                       orient=VERTICAL, 
                       command=scroll_canvas.yview)
scrollbar.grid(row=0, column=1, sticky=NS)

scroll_canvas.configure(yscrollcommand=scrollbar.set)
scroll_canvas.bind(
    '<Configure>', lambda e: scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))
)

def on_mousewheel(event):
    scroll_canvas.yview_scroll(int(-1*(event.delta/120)), "units")


scroll_canvas.bind_all("<MouseWheel>", on_mousewheel)


mainframe = ttk.Frame(scroll_canvas)
scroll_canvas.create_window((0, 0), window=mainframe, anchor=NW)

picture_frame = ttk.Frame(outer_frame)
picture_frame.grid(row=0, column=2, sticky=NSEW)

# GUI
resize_font(2)
borderwidth = 5
padding = 2
row = 0

# picture frame
preview_label = ttk.Label(picture_frame, borderwidth=borderwidth)
preview_label.pack(expand=True, fill=BOTH)


# mainframe
# filler frame to set width of mainframe
filler_frame = ttk.Frame(mainframe, padding=padding)
filler_frame.grid(row=row, column=0, sticky=NSEW)
mainframe.rowconfigure(row,weight=1)
mainframe.columnconfigure(0,weight=1)
row += 1

# filler label
filler_label = ttk.Label(filler_frame, text="Card generator", font=big_font,
                        borderwidth=borderwidth, anchor=CENTER, width=50)
filler_label.grid(row=0, column=0, sticky=NSEW)
filler_frame.columnconfigure(0,weight=1)

# open existing file
existing_frame = ttk.Frame(mainframe, padding=padding)
existing_frame.grid(row=row, column=0, sticky=NSEW)
mainframe.rowconfigure(row,weight=1)
mainframe.columnconfigure(0,weight=1)
row += 1

ttk.Label(existing_frame, text="Open existing file:", borderwidth=borderwidth).grid(row=0, column=0, sticky=NSEW)
existing_frame.columnconfigure(0,weight=1)
existing_frame.rowconfigure(0,weight=1)

open_file_button = ttk.Button(existing_frame, text="Open", command=open_file, takefocus=False)
open_file_button.grid(row=0, column=1, sticky=NSEW)
existing_frame.columnconfigure(1,weight=1)
existing_frame.rowconfigure(0,weight=1)

enable_auto_save = ttk.Button(existing_frame, text="Auto save On", command=toggle_auto_save, takefocus=False)
enable_auto_save.grid(row=0, column=2, sticky=NSEW)
existing_frame.columnconfigure(2,weight=1)
existing_frame.rowconfigure(0,weight=1)

force_save = ttk.Button(existing_frame, text="Save", command=lambda: save_file(True, False), takefocus=False)
force_save.grid(row=0, column=3, sticky=NSEW)
existing_frame.columnconfigure(3,weight=1)
existing_frame.rowconfigure(0,weight=1)

# name
name_frame = ttk.Frame(mainframe, padding=padding)
name_frame.grid(row=row, column=0, sticky=NSEW)
mainframe.rowconfigure(row,weight=1)
mainframe.columnconfigure(0,weight=1)
row += 1

card_name = ttk.Label(name_frame, text="Card name:", borderwidth=borderwidth)
card_name.grid(row=0, column=0, sticky=NSEW)
name_frame.columnconfigure(0,weight=1)
name_frame.rowconfigure(0,weight=1)

name_var = StringVar()
name_entry = ttk.Entry(name_frame, textvariable=name_var, takefocus=False)
name_entry.grid(row=0, column=1, sticky=NSEW)
name_frame.columnconfigure(1,weight=4)
name_frame.rowconfigure(0,weight=1)
name_var.trace_add('write', lambda *args: save_file(False, False, *args))


# hp
hp_label = ttk.Label(name_frame, text="HP:", borderwidth=borderwidth)
hp_label.grid(row=0, column=2, sticky=NSEW)
name_frame.columnconfigure(2,weight=2)
name_frame.rowconfigure(0,weight=1)

hp_var = StringVar()
spin = ttk.Entry(name_frame, textvariable=hp_var, width=3, takefocus=False)
spin.grid(row=0, column=3, sticky=NSEW)
name_frame.columnconfigure(3, weight=1)
hp_var.trace_add('write', lambda *args: character_limit(hp_var, 1, 500))

hp_entry = classes.Limiter(name_frame,
                          variable=hp_var,
                          orient=HORIZONTAL,
                          takefocus=False,
                          from_=0,
                          to=500,
                          precision=1)

hp_entry.grid(row=0, column=4, sticky=NSEW)
name_frame.columnconfigure(4,weight=2)

# evolution
evo_frame = ttk.Frame(mainframe, padding=padding)
evo_frame.grid(row=row, column=0, sticky=NSEW)
mainframe.rowconfigure(row,weight=1)
mainframe.columnconfigure(0,weight=1)
row += 1

evo_name = ttk.Label(evo_frame, text="Previous stage name:", borderwidth=borderwidth)
evo_name.grid(row=0, column=0, sticky=NSEW)
evo_frame.columnconfigure(0,weight=1)
evo_frame.rowconfigure(0,weight=1)

evo_var = StringVar()
evo_entry = ttk.Entry(evo_frame, textvariable=evo_var, takefocus=False)
evo_entry.grid(row=0, column=1, sticky=NSEW)
evo_frame.columnconfigure(1,weight=4)
evo_frame.rowconfigure(0,weight=1)
evo_var.trace_add('write', lambda *args: save_file(False, False, *args))

# rarity

tiers = ["Common", "Uncommon", "Rare", "Unique"]
x = IntVar()

rarity_frame = ttk.Frame(mainframe, padding=padding)
rarity_frame.grid(row=row, column=0, sticky=NSEW)
mainframe.rowconfigure(row,weight=1)
mainframe.columnconfigure(0,weight=1)
row += 1

ttk.Label(rarity_frame, text="Rarity:", borderwidth=borderwidth).grid(column=0, row=0, sticky=NSEW)
rarity_frame.columnconfigure(0,weight=1)
rarity_frame.rowconfigure(0,weight=1)

rarity_var = StringVar()
rarity_var.set(tiers[0])

for index in range(len(tiers)):
    rarity_select = ttk.Radiobutton(rarity_frame,
                              text=tiers[index],
                              variable=rarity_var,
                              value=tiers[index]
                              )
    rarity_select.grid(row=0, column=index+1, sticky=NSEW)
    rarity_frame.columnconfigure(index+1,weight=1)
    rarity_frame.rowconfigure(0,weight=1)
rarity_var.trace_add('write', lambda *args: save_file(False, False, *args))

# type 1
type_frame = ttk.Frame(mainframe, padding=padding)
type_frame.grid(row=row, column=0, sticky=NSEW)
mainframe.rowconfigure(row,weight=1)
mainframe.columnconfigure(0,weight=1)
row +=1

ttk.Label(type_frame, text="Type 1:", borderwidth=borderwidth).grid(column=0, row=0, sticky=NSEW)
type_frame.columnconfigure(0,weight=1)
type_frame.rowconfigure(0,weight=1)

moods = ['neutral', 'gamer', 'smurt', 'homie', 'enginir', 'sporty', 'weeb', 'memer', 'imposter',
              'chad', 'musey', 'none']
types_dict = {}
initial_icon_size = 30
type_var = StringVar()
type_var.set(moods[0])

type_images = []
resized_images = []
type_icons = []
type_select = []
for index in range(len(moods)):
    if index != len(moods)-1:
        type_images.append(Image.open(assets_path+"Energy "+ moods[index] + ".png"))
    else:
        type_images.append(Image.open(assets_path+"none.png"))
    resized_images.append(type_images[index].resize((initial_icon_size,initial_icon_size), resample=0))
    types_dict[moods[index]] = ImageTk.PhotoImage(resized_images[index])

    type_select.append(Radiobutton(type_frame,
                              variable=type_var,
                              value=moods[index],
                              image=types_dict[moods[index]],
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
type_var.trace_add('write', lambda *args: save_file(False, False, *args))


# type 2
ttk.Label(type_frame, text="Type 2:", borderwidth=borderwidth).grid(column=0, row=1, sticky=NSEW)
type_frame.columnconfigure(0,weight=1)
type_frame.rowconfigure(1,weight=1)

type2_select = []
type_var2 = StringVar()
type_var2.set(moods[-1])
for index in range(len(moods)):
    type2_select.append(Radiobutton(type_frame,
                              variable=type_var2,
                              value=moods[index],
                              image=types_dict[moods[index]],
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
type_var2.trace_add('write', lambda *args: save_file(False, False, *args))

# moves
add_subtract_frame = ttk.Frame(mainframe, padding=padding)
add_subtract_frame.grid(row=row, column=0, sticky=NSEW)
mainframe.rowconfigure(row,weight=1)
mainframe.columnconfigure(0,weight=1)
row += 1

ttk.Button(add_subtract_frame, text="+", command=add_move, takefocus=False).grid(row=0, column=0, sticky=NSEW)
add_subtract_frame.columnconfigure(0,weight=1)
add_subtract_frame.rowconfigure(0,weight=1)

ttk.Button(add_subtract_frame, text="-", command=subtract_move, takefocus=False).grid(row=0, column=1, sticky=NSEW)
add_subtract_frame.columnconfigure(1,weight=1)

move_var = []
damage_var = []
damage_type_var = []
move_desc_var = []
move_costs = []
moods_dict = {}
for index in range(len(moods)):
    moods_dict[moods[index]] = 0
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

move_frame = ttk.Frame(mainframe, padding=padding*3)
move_frame.grid(row=row, column=0, sticky=NSEW)
mainframe.rowconfigure(row,weight=1)
mainframe.columnconfigure(0,weight=1)
row += 1

for i in range(0, limit):
    ind_move_frame.append(ttk.Frame(move_frame, padding=padding*2))
    ind_move_frame[i].pack(expand=True, fill=BOTH)

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
    move_name_entry.append(ttk.Entry(move_name_frame[i], textvariable=move_var[i], takefocus=False))
    move_var[i].trace_add('write', save_file)
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
    damage_var[i].trace_add('write', lambda *args, a=i: character_limit(damage_var[a], 1, 300))

    damage_entry.append(classes.Limiter(move_damage_frame[i],
                            variable=damage_var[i],
                            orient=HORIZONTAL,
                            takefocus=False,
                            from_=0,
                            to=300,
                            precision=1))

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
    damage_type_var[i].set(moods[0])
    for index in range(len(moods)-1):
        damage_type_entry[i].append(Radiobutton(move_type_frame[i],
                                variable=damage_type_var[i],
                                value=moods[index],
                                image=types_dict[moods[index]],
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
    damage_type_var[i].trace_add('write', save_file)
    
    # description
    move_description_label.append(ttk.Label(move_description_frame[i], text="Move " + str(i + 1) + " description:", borderwidth=borderwidth))
    move_description_label[i].grid(row=0, column=0, sticky=NSEW)
    move_description_frame[i].columnconfigure(0, weight=1)
    move_description_frame[i].rowconfigure(0, weight=1)

    move_desc_var.append(StringVar())
    move_description_entry.append(ttk.Entry(move_description_frame[i], textvariable=move_desc_var[i], takefocus=False))
    move_desc_var[i].trace_add('write', save_file)
    move_description_entry[i].grid(row=0, column=1, sticky=NSEW)
    move_description_frame[i].columnconfigure(1, weight=1)
    move_description_frame[i].rowconfigure(0, weight=1)

    # cost
    ttk.Label(move_cost_frame[i], text="Add cost:", borderwidth=borderwidth).grid(row=0, column=0, sticky=NSEW)
    move_cost_frame[i].columnconfigure(0,weight=1)
    move_cost_frame[i].rowconfigure(0,weight=1)

    move_costs.append(moods_dict.copy())
    total_cost.append(0)
    for index in range(len(moods)-1):
        cost_button = ttk.Button(move_cost_frame[i], takefocus=False, image=types_dict[moods[index]], command=lambda a=i, b=index: move_cost_update(a, b))
                                 
        cost_button.grid(row=0, column=index+1, sticky=NSEW)
        move_cost_frame[i].columnconfigure(index+1, weight=1)
        move_cost_frame[i].rowconfigure(1,weight=1)

    move_cost_label.append(ttk.Label(selected_cost_frame[i], text="Move " + str(i + 1) + " cost:", borderwidth=borderwidth))
    move_cost_label[i].pack(side=LEFT)

    if i != 0:
        ind_move_frame[i].pack_forget()

# retreat cost
retreat_frame = ttk.Frame(mainframe, padding=padding)
retreat_frame.grid(row=row, column=0, sticky=NSEW)
mainframe.rowconfigure(row,weight=1)
mainframe.columnconfigure(0,weight=1)
row += 1        

ttk.Label(retreat_frame, text="Retreat cost:", borderwidth=borderwidth).grid(row=0, column=0, sticky=NSEW)
retreat_frame.columnconfigure(0,weight=1)
retreat_frame.rowconfigure(0,weight=1)

retreat_var = StringVar()
spin = ttk.Entry(retreat_frame, textvariable=retreat_var, width=1, takefocus=False)
spin.grid(row=0, column=1, sticky=NSEW)
retreat_frame.columnconfigure(1, weight=1)
retreat_var.trace_add('write', lambda *args: character_limit(retreat_var, 0, 7))

hp_entry.grid(row=0, column=4, sticky=NSEW)
retreat_frame.columnconfigure(4,weight=2)

retreat_entry = classes.Limiter(retreat_frame,
                          variable=retreat_var,
                          orient=HORIZONTAL,
                          from_=0,
                          to=7,
                          precision=0,
                          takefocus=False)
retreat_entry.grid(row=0, column=2, sticky=NSEW)
retreat_frame.columnconfigure(2,weight=1)
retreat_frame.rowconfigure(0,weight=1)
retreat_var.trace_add('write', lambda *args: save_file(False, False, *args))


# description
description_frame = ttk.Frame(mainframe, padding=padding)
description_frame.grid(row=row, column=0, sticky=NSEW)
mainframe.rowconfigure(row,weight=1)
mainframe.columnconfigure(0,weight=1)
row += 1

ttk.Label(description_frame, text="Card description:", borderwidth=borderwidth).grid(row=0, column=0, sticky=NSEW)
description_frame.columnconfigure(0,weight=1)
description_frame.rowconfigure(0,weight=1)

desc_var = StringVar()
description_entry = ttk.Entry(description_frame, textvariable=desc_var)
description_entry.grid(row=0, column=1, sticky=NSEW)
description_frame.columnconfigure(1,weight=1)
description_frame.rowconfigure(0,weight=1)
desc_var.trace_add('write', lambda *args: save_file(False, False, *args))

# Illustration
illustrator_frame = ttk.Frame(mainframe, padding=padding)
illustrator_frame.grid(row=row, column=0, sticky=NSEW)
mainframe.rowconfigure(row,weight=1)
mainframe.columnconfigure(0,weight=1)
row += 1

ttk.Label(illustrator_frame, text="Card illustrator:", borderwidth=borderwidth).grid(row=0, column=0, sticky=NSEW)
illustrator_frame.columnconfigure(0,weight=1)
illustrator_frame.rowconfigure(0,weight=1)

illustrator_var = StringVar()
illustrator_entry = ttk.Entry(illustrator_frame, textvariable=illustrator_var)
illustrator_entry.grid(row=0, column=1, sticky=NSEW)
illustrator_frame.columnconfigure(1,weight=1)
illustrator_frame.rowconfigure(0,weight=1)
illustrator_var.trace_add('write', lambda *args: save_file(False, False, *args))

index_frame = ttk.Frame(mainframe, padding=padding)
index_frame.grid(row=row, column=0, sticky=NSEW)
mainframe.rowconfigure(row,weight=1)
mainframe.columnconfigure(0,weight=1)
row += 1

# Index
ttk.Label(index_frame, text="Card index:", borderwidth=borderwidth).grid(row=0, column=0, sticky=NSEW)
index_frame.columnconfigure(0,weight=1)
index_frame.rowconfigure(0,weight=1)

index_var = StringVar()
index_entry = ttk.Entry(index_frame, textvariable=index_var)
index_entry.grid(row=0, column=1, sticky=NSEW)
index_frame.columnconfigure(1,weight=1)
index_frame.rowconfigure(0,weight=1)
index_var.trace_add('write', lambda *args: character_limit(index_var, 0))

# crop image
crop_frame = ttk.Frame(mainframe, padding=padding)
crop_frame.grid(row=row, column=0, sticky=NSEW)
mainframe.rowconfigure(row,weight=1)
mainframe.columnconfigure(0,weight=1)
row += 1

def import_image():   
    global values
    global image
    global rect
    global card_image

    use_this_path = filedialog.askopenfilename(initialdir=f"{os.getcwd()}\\{file_path}", title="Select file", filetypes=(("png files", "*.png"), ("all files", "*.*")))
    if use_this_path == '': return

    card_image = Image.open(use_this_path)
    
    # add to canvas
    scale = card_image.width/mainframe.winfo_width()
    card_image = card_image.resize((int(card_image.width/scale), int(card_image.height/scale)), resample=0)
    canvas.config(width=card_image.width, height=card_image.height)
    localphoto = ImageTk.PhotoImage(card_image)
    canvas.itemconfig(image, image=localphoto)
    canvas.image = localphoto


    # add rectangle to canvas to show where the image will be cropped
    unique_size = (727, 1013)
    normal_size = (607, 375)

    if 'rarity' in values and values['rarity'] == 'Unique':
        aspect_ratio = unique_size[1]/unique_size[0]
    else:
        aspect_ratio = normal_size[1]/normal_size[0]

    canvas.coords(rect, 0, 0, 100, 100*aspect_ratio)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<B3-Motion>", on_move_drag)
    canvas.bind("<ButtonRelease-1>", lambda event: save_file(False, False, event))
    canvas.bind("<ButtonRelease-3>", lambda event: save_file(False, False, event))

    values['image'] = card_image

    save_file()



# import image
import_button = ttk.Button(crop_frame, text="Import image", command=import_image, takefocus=False)
import_button.grid(row=0, column=0, sticky=NSEW)
crop_frame.columnconfigure(0,weight=1)
crop_frame.rowconfigure(0,weight=1)

# image canvas
canvas = Canvas(crop_frame, width=100, height=400, background=background_color)
canvas.grid(row=1, column=0, sticky=NSEW)
crop_frame.columnconfigure(0,weight=1)
crop_frame.rowconfigure(1,weight=1)

card_image = Image.open(assets_path + "nameless.jpg")
image = canvas.create_image(0, 0, anchor=NW, tag='photo')
rect = canvas.create_rectangle(0, 0, 0, 0, outline='black', width=2)


# make rectangle draggable
def on_move_drag(event):
    global values
    global rect
    global image
    global card_image

    x, y = event.x, event.y

    rectx = canvas.coords(rect)[0]
    recty = canvas.coords(rect)[1]
    rectx2 = canvas.coords(rect)[2]
    recty2 = canvas.coords(rect)[3]

    rectwidth = rectx2-rectx
    rectheight = recty2-recty

    x = max(1, min(x, canvas.winfo_width()-rectwidth-1))
    y = max(1, min(y, canvas.winfo_height()-rectheight-1))

    canvas.coords(rect, x, y, x+rectwidth, y+rectheight)

    # crop image
    cropped_image = card_image.crop((int(x), int(y), int(x+rectwidth), int(y+rectheight)))

    values['image'] = cropped_image

def on_drag(event):
    global values
    global rect
    global image
    
    x, y = event.x, event.y
    rectx = canvas.coords(rect)[0]
    recty = canvas.coords(rect)[1]
    rectx2 = canvas.coords(rect)[2]
    recty2 = canvas.coords(rect)[3]
    
    unique_size = (727, 1013)
    normal_size = (607, 375)

    if 'rarity' in values and values['rarity'] == 'Unique':
        aspect_ratio = unique_size[1]/unique_size[0]
    else:
        aspect_ratio = normal_size[1]/normal_size[0]

    rectx2 = min(x, canvas.winfo_width())

    width = max(rectx2-rectx, 50)
    height = width*aspect_ratio

    rectx2 = rectx+width
    recty2 = recty+height

    if recty2 > canvas.winfo_height():
        recty2 = canvas.winfo_height()
        height = recty2-recty
        rectx2 = rectx+height/aspect_ratio

    canvas.coords(rect, rectx, recty, rectx2, recty2)

    cropped_image = card_image.crop((int(rectx), int(recty), int(rectx2), int(recty2)))

    values['image'] = cropped_image


window.protocol("WM_DELETE_WINDOW", on_closing)

window.update()

# start the canvas at the top
scroll_canvas.yview_moveto(0)
scroll_canvas.xview_moveto(0)

# initialise width of window to be the same as the frame
width = mainframe.winfo_width()+scrollbar.winfo_width()+picture_frame.winfo_width()
height = min(mainframe.winfo_height(), 600)
scroll_canvas.configure(width=mainframe.winfo_width(), height=height)
scroll_canvas.configure(scrollregion=(0, 0, mainframe.winfo_width(), height))
window.geometry(f"{width}x{height}")

window.bind("<Configure>", update_size())

window.mainloop()