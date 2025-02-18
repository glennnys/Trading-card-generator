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
import io

values = {}
background_color = "#424549"
text_color = "#99aab5"
second_background_color = "#36393e"

# functions
move_count = 1
limit = 3

def update_canvas():
    global move_count
    global limit
    global ind_move_frame

    #get mainframe height
    window.update()
    width = mainframe.winfo_width()
    height = mainframe.winfo_height()
    scroll_canvas.configure(scrollregion=(0, 0, width, height)) 

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

    update_preview()

def resize_font(incr):
    '''Change the size of SunValley fonts by the incr factor '''
    for font_name in (
        "Caption", "Body", "BodyStrong", "BodyLarge",
        "Subtitle", "Title", "TitleLarge", "Display"
    ):
        font = nametofont(f"SunValley{font_name}Font")
        size = font.cget("size")
        font.configure(size=size-incr)


update_prev = True
def update_preview():
    global values
    global picture_frame
    global photo
    global preview_label
    global update_prev
    
    if not update_prev: return

    height = window.winfo_height()

    image = main.preview_card(values, editor_mode=True)
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


######### Window #########
window = Tk()
style = ttk.Style()
sv_ttk.set_theme("dark")

window_id = "card.generator.window"  # will only work once compiled I think
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(window_id)

small_font = Font(family='Roboto', size=10, weight='bold')
mid_font = Font(family='Roboto', size=15, weight='bold')
big_font = Font(family='Roboto', size=20, weight='bold')

window.title("Card generator")

icon = PhotoImage(main.get_asset("Energy neutral.png"))
window.iconphoto(True, icon)
window.config(background=background_color)


########## Initiate values ##########
values['name'] = 'nameless'
values['hp'] = '0'
values['rarity'] = 'Common'
values['type'] = ['neutral']
values['move 1 name'] = 'moveless'
values['move 1 desc'] = 'no description'
values['move 1 cost'] = ['0 none']
values['retreat'] = '0'
values['entry'] = '0'
values['description'] = 'bitch lasagne'
values['illustrator'] = 'no illustrator'
values['image'] = Image.open(io.BytesIO(main.get_asset('nameless.jpg')))

################ GUI starts here ################
outer_frame = Frame(window, background=background_color)
outer_frame.pack(fill=BOTH, expand=True)

resize_font(2)
borderwidth = 5
padding = 2
row = 0


########## Scrollable canvas ##########
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


########## Preview frame ##########
picture_frame = ttk.Frame(outer_frame)
picture_frame.grid(row=0, column=2, sticky=NSEW)

preview_label = ttk.Label(picture_frame, borderwidth=borderwidth)
preview_label.pack(expand=True, fill=BOTH)


########## Title ##########
# sets width of the entire frame
filler_frame = ttk.Frame(mainframe, padding=padding)
filler_frame.grid(row=row, column=0, sticky=NSEW)
mainframe.rowconfigure(row,weight=1)
mainframe.columnconfigure(0,weight=1)
row += 1

filler_label = ttk.Label(filler_frame, text="Card generator", font=big_font,
                        borderwidth=borderwidth, anchor=CENTER, width=50).pack(expand=True, fill=BOTH, side='left')


########## Open existing file ##########
existing_frame = ttk.Frame(mainframe, padding=padding)
existing_frame.grid(row=row, column=0, sticky=NSEW)
mainframe.rowconfigure(row,weight=1)
mainframe.columnconfigure(0,weight=1)
row += 1

# open existing file text
# ttk.Label(existing_frame, text="Open existing file:", borderwidth=borderwidth).pack(expand=True, fill=BOTH, side='left')

# open existing file button
# def open_file():
#     global allow_save
#     global move_count
#     global values
#     global update_prev

#     toggle_auto_save(False)
#     update_prev = False

#     use_this_path = filedialog.askopenfilename(initialdir=f"{os.getcwd()}\\{file_path}", title="Select file", filetypes=(("text files", "*.txt"), ("all files", "*.*")))
#     if use_this_path == '': return
#     existing = open(use_this_path, "r")
#     old_values = main.generate_dict(existing)
#     existing.close()

#     if 'name' in old_values and old_values['name'] != '':
#         name_var.set(old_values['name'])
#         if f'{name_var.get()}.png' in os.listdir(file_path):
#             import_image(f'{file_path}{name_var.get()}.png')
#         elif f'{name_var.get()}.jpg' in os.listdir(file_path):
#             import_image(f'{file_path}{name_var.get()}.jpg')
#         else:
#             import_image(f'{assets_path}nameless.jpg')

#         if 'crop' in old_values and old_values['crop'] != '':
#             canvas.coords(rect, old_values['crop'][0], old_values['crop'][1], old_values['crop'][2], old_values['crop'][3])

#     if 'prev stage' in old_values and old_values['prev stage'] != '':
#         evo_var.set(old_values['prev stage'])
#     if 'rarity' in old_values and old_values['rarity'] != '':
#         rarity_var.set(old_values['rarity'])
#     if 'type' in old_values and len(old_values['type']) != 0:
#         type_var.set(old_values['type'][0])
#         if len(old_values['type']) != 1:
#             type_var2.set(old_values['type'][1])
#     if 'description' in old_values and old_values['description'] != '':
#         desc_var.set(old_values['description'])
#     if 'illustrator' in old_values and old_values['illustrator'] != '':
#         illustrator_var.set(old_values['illustrator'])
#     if 'entry' in old_values and old_values['entry'] != '':
#         index_var.set(old_values['entry'])
#     if 'retreat' in old_values and old_values['retreat'] != '':
#         retreat_var.set(old_values['retreat'])
#     if 'hp' in old_values and old_values['hp'] != '':
#         hp_var.set(old_values['hp'])
    
#     old_move_count = 0
#     for nr in range(0, limit):
#         if f"ability {nr+1} name" in old_values and old_values[f"ability {nr+1} name"] != '':
#             old_move_count = nr+1
#             if old_move_count > move_count:
#                 add_move(False)
#             if toggle_move_type_button[old_move_count-1]['text'] == 'Move':
#                 toggle_button_type(old_move_count-1, False)
#             move_var[old_move_count-1].set(old_values[f"ability {nr+1} name"])
#         if f"ability {nr+1} desc" in old_values and old_values[f"ability {nr+1} desc"] != '':
#             old_move_count = nr+1
#             if old_move_count > move_count:
#                 add_move(False)
#             if toggle_move_type_button[old_move_count-1]['text'] == 'Move':
#                 toggle_button_type(old_move_count-1, False)
#             move_desc_var[old_move_count-1].set(old_values[f"ability {nr+1} desc"])

#     for nr in range(0, limit):
#         i = old_move_count
#         if f"move {nr+1} name" in old_values and old_values[f"move {nr+1} name"] != '':
#             old_move_count = i+1
#             if old_move_count > move_count:
#                 add_move(False)
#             if toggle_move_type_button[old_move_count-1]['text'] == 'Ability':
#                 toggle_button_type(old_move_count-1, False)
#             move_var[old_move_count-1].set(old_values[f"move {nr+1} name"])
#         if f"move{nr+1} damage" in old_values and old_values[f"move {nr+1} damage"] != '':
#             old_move_count = i+1
#             if old_move_count > move_count:
#                 add_move(False)
#             if toggle_move_type_button[old_move_count-1]['text'] == 'Ability':
#                 toggle_button_type(old_move_count-1, False)
#             damage_var[old_move_count-1].set(old_values[f"move {nr+1} damage"].split()[0])
#             damage_type_var[old_move_count-1].set(old_values[f"move {nr+1} damage"].split()[1])
#         if f"move {nr+1} desc" in old_values and old_values[f"move {nr+1} desc"] != '':
#             old_move_count = i+1
#             if old_move_count > move_count:
#                 add_move(False)
#             if toggle_move_type_button[old_move_count-1]['text'] == 'Ability':
#                 toggle_button_type(old_move_count-1, False)
#             move_desc_var[old_move_count-1].set(old_values[f"move {nr+1} desc"])
#         if f"move {nr+1} cost" in old_values and old_values[f"move {nr+1} cost"] != '':
#             old_move_count = i+1
#             if old_move_count > move_count:
#                 add_move(False)
#             if toggle_move_type_button[old_move_count-1]['text'] == 'Ability':
#                 toggle_button_type(old_move_count-1, False)
#             costs = old_values[f"move {nr+1} cost"]
#             for cost in costs:
#                 count = int(cost.split()[0])
#                 type = cost.split()[1]
#                 for index in range(len(moods)-1):
#                     if type == moods[index]:
#                         for j in range(count):
#                             move_cost_update(old_move_count-1, index, False)
    
#     if old_move_count < move_count:
#         for nr in range(old_move_count, move_count):
#             subtract_move(False)

#     update_prev = True
#     update_canvas()
#     update_preview()


# open_file_button = ttk.Button(existing_frame, text="Open", command=open_file, takefocus=False)
# open_file_button.pack(expand=True, fill=BOTH, side='left')

# enable auto save button
allow_save = False
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
        save_file()

running = True
def auto_save():
    while running:
        if allow_save:
            save_file()
        sleep_event.wait(timeout=10)
        
enable_auto_save = ttk.Button(existing_frame, text="Auto save On", command=toggle_auto_save, takefocus=False)
enable_auto_save.pack(expand=True, fill=BOTH, side='left')

auto_save_thread = threading.Thread(target=auto_save)
sleep_event = threading.Event()
auto_save_thread.start()

# save button
previous_name = ''
def save_file(from_close=False):
    global previous_name
    global values

    update_preview()
    window.update()
    if values['name'] not in ('', ' '):
        card_image.save(f'{file_path}{values["name"]}.png')
        path = ''
        if from_close: path = file_path + 'recovered.txt'
        else: path = file_path + values['name'] + '.txt'
        try:
            f = open(path, "w+")
        except:
            # catch error for whatever reason
            return
        
        # save values to file
        for key in values:
            if key == 'image': continue
            if type(values[key]) == list:
                f.write(f'{key}: {values[key][0]}')
                for i in range(1, len(values[key])):
                    f.write(f', {values[key][i]}')
                f.write('\n')
            else: f.write(f'{key}: {values[key]}\n')
        f.close()

    # remove previous file if name changed
    if previous_name != '' and previous_name != values['name']:
        os.remove(file_path + previous_name + '.txt')
        os.remove(file_path + previous_name + '.png')
    previous_name = values["name"]

force_save = ttk.Button(existing_frame, text="Save", command=lambda: save_file(), takefocus=False)
force_save.pack(expand=True, fill=BOTH, side='left')


########## Name frame ##########
name_frame = ttk.Frame(mainframe, padding=padding)
name_frame.grid(row=row, column=0, sticky=NSEW)
mainframe.rowconfigure(row,weight=1)
row += 1

# name label
card_name = ttk.Label(name_frame, text="Card name:", borderwidth=borderwidth)
card_name.pack(expand=True, fill=BOTH, side='left')

# name change function
def change_name():
    values['name'] = name_var.get()
    values['name'] = "".join(c for c in values['name'] if c.isalpha())
    if values['name'] == '': values['name'] = 'nameless'  
    if values['name'] != 'nameless': name_var.set(values['name'])
    update_preview()

# name entry
name_var = StringVar()
name_entry = ttk.Entry(name_frame, textvariable=name_var, takefocus=False)
name_entry.pack(expand=True, fill=BOTH, side='left')
name_var.trace_add('write', lambda *args: change_name())


########## HP frame ##########   
hp_label = ttk.Label(name_frame, text="HP:", borderwidth=borderwidth)
hp_label.pack(expand=True, fill=BOTH, side='left')

# hp change function
def change_hp():
    character_limit(hp_var, 1, 500)
    values['hp'] = hp_var.get()
    if values['hp'] == '': values['hp'] = '0'
    update_preview()

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


########## Evolution frame ##########
evo_frame = ttk.Frame(mainframe, padding=padding)
evo_frame.grid(row=row, column=0, sticky=NSEW)
mainframe.rowconfigure(row,weight=1)
row += 1

# evo label
evo_name = ttk.Label(evo_frame, text="Previous stage name:", borderwidth=borderwidth)
evo_name.pack(expand=True, fill=BOTH, side='left')

# evo change function
def change_evo():
    values['prev stage'] = evo_var.get()
    if values['prev stage'] == '': values.pop('prev stage', None)
    update_preview()

# evo entry
evo_var = StringVar()
evo_entry = ttk.Entry(evo_frame, textvariable=evo_var, takefocus=False)
evo_entry.pack(expand=True, fill=BOTH, side='left')
evo_var.trace_add('write', lambda *args: change_evo())


########## Rarity frame ##########
rarity_frame = ttk.Frame(mainframe, padding=padding)
rarity_frame.grid(row=row, column=0, sticky=NSEW)
mainframe.rowconfigure(row,weight=1)
row += 1

tiers = ["Common", "Uncommon", "Rare", "Unique"]
x = IntVar()

# rarity label
ttk.Label(rarity_frame, text="Rarity:", borderwidth=borderwidth).pack(expand=True, fill=BOTH, side='left')

# rarity change function
def change_rarity():
    values["rarity"] = rarity_var.get()
    update_preview()

# rarity buttons
rarity_var = StringVar()
rarity_var.set(tiers[0])
for index in range(len(tiers)):
    rarity_select = ttk.Radiobutton(rarity_frame,
                              text=tiers[index],
                              variable=rarity_var,
                              value=tiers[index]
                              )
    rarity_select.pack(expand=True, fill=BOTH, side='left')
rarity_var.trace_add('write', lambda *args: change_rarity())


########## Card type frame ##########
type_frame = ttk.Frame(mainframe, padding=padding)
type_frame.grid(row=row, column=0, sticky=NSEW)
mainframe.rowconfigure(row,weight=1)
row +=1

moods = ['neutral', 'gamer', 'smurt', 'homie', 'enginir', 'sporty', 'weeb', 'memer', 'imposter',
              'chad', 'musey', 'none']
types_dict = {}
initial_icon_size = 30
type_var = StringVar()
type_var.set(moods[0])

type_images = []
resized_images = []

def change_type():
    if (type_var.get() == type_var2.get() and type_var.get() != 'none') or (type_var2.get() == 'none'):
        values['type'] = [type_var.get()]
    elif type_var.get() == 'none' and type_var2.get() != 'none':
        values['type'] = [type_var2.get()]
    else:
        values['type'] = [type_var.get(), type_var2.get()]
    update_preview()

# type 1 label
ttk.Label(type_frame, text="Type 1:", borderwidth=borderwidth).grid(column=0, row=0, sticky=NSEW)
type_frame.columnconfigure(0,weight=1)

# type 1 buttons
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
type_var.trace_add('write', lambda *args: change_type())

# type 2 label
ttk.Label(type_frame, text="Type 2:", borderwidth=borderwidth).grid(column=0, row=1, sticky=NSEW)

# type 2 buttons
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
type_var2.trace_add('write', lambda *args: change_type())


############### Moves frame ###############
add_subtract_frame = ttk.Frame(mainframe, padding=padding)
add_subtract_frame.grid(row=row, column=0, sticky=NSEW)
mainframe.rowconfigure(row,weight=1)
row += 1

def add_move(update=True):
    global move_count
    global limit
    global ind_move_frame
    
    if move_count < limit:
        move_count += 1
        mainframe.rowconfigure(3,weight=move_count*3)
        ind_move_frame[move_count - 1].pack(expand=True, fill=BOTH)

    change_moves()
    if update: update_canvas()


def subtract_move(update=True):
    global move_count
    global limit
    global ind_move_frame
    
    if move_count > 1:
        move_count -= 1
        mainframe.rowconfigure(3,weight=move_count*3)
        ind_move_frame[move_count].pack_forget()

    change_moves()
    if update: update_canvas()

# buttons to add and subtract moves
ttk.Button(add_subtract_frame, text="+", command=add_move, takefocus=False).pack(expand=True, fill=BOTH, side='left')
ttk.Button(add_subtract_frame, text="-", command=subtract_move, takefocus=False).pack(expand=True, fill=BOTH, side='left')

# move variables
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

# change moves function
def change_moves(): # save moves and abilities to values
    
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

    update_preview()

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
    
    change_moves()

def remove_button(button, nr, type, update=True):
    global move_costs
    global total_cost

    total_cost[nr] -= 1
    move_costs[nr][type] = int(move_costs[nr][type])-1
    button.destroy()

    if update: update_canvas()

    change_moves()

# move frame
move_frame = ttk.Frame(mainframe, padding=padding*3)
move_frame.grid(row=row, column=0, sticky=NSEW)
mainframe.rowconfigure(row,weight=1)
row += 1

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

########## End of moves ##########
        

########## Retreat frame ##########
retreat_frame = ttk.Frame(mainframe, padding=padding)
retreat_frame.grid(row=row, column=0, sticky=NSEW)
mainframe.rowconfigure(row,weight=1)
row += 1        

# retreat label
ttk.Label(retreat_frame, text="Retreat cost:", borderwidth=borderwidth).pack(expand=True, fill=BOTH, side='left')

# retreat change function
def change_retreat():
    character_limit(retreat_var, 0, 7)
    values["retreat"] = retreat_var.get()
    if values["retreat"] == '': values["retreat"] = '0'
    update_preview()

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
description_frame.grid(row=row, column=0, sticky=NSEW)
mainframe.rowconfigure(row,weight=1)
row += 1

# description label
ttk.Label(description_frame, text="Card description:", borderwidth=borderwidth).pack(expand=True, fill=BOTH, side='left')

# description change function
def change_desc():
    values["description"] = desc_var.get()
    if values["description"] == '': values["description"] = 'bitch lasagna'
    update_preview()

desc_var = StringVar()
description_entry = ttk.Entry(description_frame, textvariable=desc_var)
description_entry.pack(expand=True, fill=BOTH, side='left')
desc_var.trace_add('write', lambda *args: change_desc())

########## Illustrator frame ##########
illustrator_frame = ttk.Frame(mainframe, padding=padding)
illustrator_frame.grid(row=row, column=0, sticky=NSEW)
mainframe.rowconfigure(row,weight=1)
row += 1

# illustrator label
ttk.Label(illustrator_frame, text="Card illustrator:", borderwidth=borderwidth).pack(expand=True, fill=BOTH, side='left')

# illustrator change function
def change_illustrator():
    values["illustrator"] = illustrator_var.get()
    if values["illustrator"] == '': values["illustrator"] = 'no illustrator'
    update_preview()

# illustrator entry
illustrator_var = StringVar()
illustrator_entry = ttk.Entry(illustrator_frame, textvariable=illustrator_var).pack(expand=True, fill=BOTH, side='left')
illustrator_var.trace_add('write', lambda *args: change_illustrator())


########## Card index frame ##########
index_frame = ttk.Frame(mainframe, padding=padding)
index_frame.grid(row=row, column=0, sticky=NSEW)
mainframe.rowconfigure(row,weight=1)
row += 1

ttk.Label(index_frame, text="Card index:", borderwidth=borderwidth).pack(expand=True, fill=BOTH, side='left')

index_var = StringVar()
index_entry = ttk.Entry(index_frame, textvariable=index_var)
index_entry.pack(expand=True, fill=BOTH, side='left')
def change_index():
    character_limit(index_var, 0)
    values["entry"] = index_var.get()
    if values["entry"] == '': values["entry"] = '0'
    update_preview()
index_var.trace_add('write', lambda *args: change_index())

########## Crop image ##########
crop_frame = ttk.Frame(mainframe, padding=padding)
crop_frame.grid(row=row, column=0, sticky=NSEW)
mainframe.rowconfigure(row,weight=1)
row += 1

scoped_image = None

def import_image(path=''):   
    global values
    global image
    global rect
    global card_image
    global scoped_image
    
    if path == '':
        use_this_path = filedialog.askopenfilename(initialdir=f"{os.getcwd()}\\{file_path}", title="Select file", filetypes=(("png files", "*.png"), ("all files", "*.*")))
    else:
        use_this_path = path
    if use_this_path == '': return

    card_image = Image.open(use_this_path)
    if card_image.mode != 'RGBA':
        card_image = card_image.convert('RGBA')
    
    # add to canvas
    scale = card_image.width/mainframe.winfo_width()
    card_image = card_image.resize((int(card_image.width/scale), int(card_image.height/scale)), resample=0)
    canvas.config(width=card_image.width, height=card_image.height)
    localphoto = ImageTk.PhotoImage(card_image)
    canvas.itemconfig(image, image=localphoto)
    scoped_image = localphoto


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
    canvas.bind("<ButtonRelease-1>", lambda event: update_preview())
    canvas.bind("<ButtonRelease-3>", lambda event: update_preview())

    values['image'] = card_image

    update_canvas()
    update_preview()


##### import image button #####
import_button = ttk.Button(crop_frame, text="Import image", command=import_image, takefocus=False)
import_button.pack(expand=True, fill=BOTH)

##### Image canvas #####
canvas = Canvas(crop_frame, width=100, height=400, background=background_color)
canvas.pack(expand=True, fill=BOTH)

card_image = Image.open(assets_path + "nameless.jpg")
image = canvas.create_image(0, 0, anchor=NW, tag='photo')
rect = canvas.create_rectangle(0, 0, 0, 0, outline='black', width=2)


# make rectangle draggable
def on_move_drag(event):
    global values
    global rect

    x, y = event.x, event.y

    rectx = canvas.coords(rect)[0]
    recty = canvas.coords(rect)[1]
    rectx2 = canvas.coords(rect)[2]
    recty2 = canvas.coords(rect)[3]

    rectwidth = rectx2-rectx
    rectheight = recty2-recty

    x = int(max(1, min(x, canvas.winfo_width()-rectwidth-1)))
    y = int(max(1, min(y, canvas.winfo_height()-rectheight-1)))


    canvas.coords(rect, x, y, x+rectwidth, y+rectheight)

    # crop image
    values['crop'] = (x, y, int(x+rectwidth), int(y+rectheight))

    update_preview()

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

    if 'rarity' in values and values['rarity'] == 'Unique':
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

    update_preview()

def on_closing():
    global running
    try: save_file(True)
    except: "error saving file"
    sleep_event.set()
    running = False
    auto_save_thread.join()
    window.destroy()
window.protocol("WM_DELETE_WINDOW", on_closing)

window.update()

########## End of GUI ##########

# start the canvas at the top
scroll_canvas.yview_moveto(0)
scroll_canvas.xview_moveto(0)

####### Initialise width of window to be the same as the frame #######
width = mainframe.winfo_width()+scrollbar.winfo_width()+picture_frame.winfo_width()
height = min(mainframe.winfo_height(), 600)
scroll_canvas.configure(width=mainframe.winfo_width(), height=height)
scroll_canvas.configure(scrollregion=(0, 0, mainframe.winfo_width(), height))
window.geometry(f"{width}x{height}")

allow_save = True

update_prev = True
window.update()
update_preview()

window.resizable(False, False)

window.mainloop()
