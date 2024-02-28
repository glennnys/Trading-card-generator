from PIL import Image, ImageOps
from PIL import ImageFont
from PIL import ImageDraw
import os
import re
import math
import textwrap

# set to change card shape and size, most things move with it. sort of
card_shape = (747, 1038)
show_steps = False
do_prints = True

# important paths
assets_path = "assets/"
inputs_path = "card files/"
storage_path = "generated cards/"
biggest_font = 'Roboto-boldItalic.ttf'
big_font = 'Roboto-bold.ttf'
normal_font = 'Roboto-Medium.ttf'
small_font = 'Roboto-Regular.ttf'
description_font = 'papyrus.ttf'

# arrays to make writing the info about a card easier
name_array = ['name', 'title']
type_array = ['type']
evolution_array = ['evo', 'stage', 'prev']
ability_array = ['abilit', 'speci']
move_array = ['mov']
move_damage_array = ['dam', 'att', 'typ']
move_energy_array = ['cost', 'energ']
description_array = ['text', 'desc', 'detail']
hp_array = ['hit', 'points', 'hp', 'health']
retreat_array = ['retreat', 'fallback']
id_array = ['number', 'id', 'entry', 'ind']
rarity_array = ['rar', 'tier']
volatile_array = ['vol', 'lat', 'expl']
illus_array = ['llus', 'draw']

rarity = ['unc', 'norm', 'com', 'rare', 'leg', 'uni']
real_rarity = ['uncommon', 'common', 'common', 'rare', 'rare', 'unique']

types = ['gam', 'nerd', 'nurd', 'sm', 'hom', 'eng', 'spo', 'wee', 'meme', 'imp', 'chad', 'mus', 'neutral', 'norm', '']
real_types = ['gamer', 'smurt', 'smurt', 'smurt', 'homie', 'enginir', 'sporty', 'weeb', 'memer', 'imposter',
              'chad', 'musey', 'neutral', 'neutral', 'None']

# unused damage types
damage_types = ['phys', 'fys', 'mag', 'sup', 'heal', 'hel', 'rang', 'gun', 'bow', '']
real_damage_types = ['physical', 'physical', 'magic', 'support', 'support', 'support', 'ranged', 'ranged', 'ranged',
                     'None']
weakness_array = ['weak', 'soft', 'hurt', 'more']
resist_array = ['strong', 'res', 'less']


# used to calculate resistance and weakness
real_types_index = (0, 8, 8, 8, 6, 4, 1, 3, 2, 5, 7, 9, 10) # mapping from types to indexes in the array
type_colors = ((0,0,0),(242,247,255),(0,228,23),(239,0,214),(242,151,21),(227,7,0),(123,0,199),(242,236,21),(4,124,215),(99,46,10), (128,128,128))
Effectiveness_array = [[2, 1, 2, 2, 1, 1, 2, 0, 2, 2, 2],
                       [2, 2, 2, 2, 2, 2, 3, 1, 3, 1, 2],
                       [2, 2, 3, 2, 2, 3, 2, 3, 1, 2, 2],
                       [1, 1, 1, 2, 1, 2, 1, 2, 2, 3, 2],
                       [2, 2, 2, 2, 4, 2, 2, 2, 3, 2, 2],
                       [3, 2, 2, 2, 3, 0, 2, 2, 1, 3, 2],
                       [2, 2, 1, 2, 2, 3, 2, 2, 2, 2, 2],
                       [0, 2, 2, 2, 2, 2, 2, 0, 3, 2, 2],
                       [2, 3, 2, 1, 3, 3, 2, 1, 1, 2, 2],
                       [2, 2, 3, 2, 1, 2, 2, 2, 2, 2, 2],
                       [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]]

# global variables
image = Image.new('RGBA', card_shape)
values = {}


# base function used by other functions, code that add text in a certain spot and makes sure the text folds over
# when the maximum width is achieved
def set_text(text, font, color, corner, width, stroke=2):
    global image
    draw = ImageDraw.Draw(image)
    size = draw.textlength(text, font=font)
    pixels_per_letter = size / len(text)
    lines = textwrap.wrap(text, width=math.ceil(width / pixels_per_letter))
    new_text = ""
    for line in lines:
        new_text += line + '\n'

    if stroke:
        draw.text(corner, new_text, color, font=font, stroke_width=stroke, stroke_fill='white')
    else:
        draw.text(corner, new_text, color, font=font)

    if show_steps: image.show()


# base function used by other functions, code that adds images to the existing card within specified region
def set_image(image_path, corners, mask=None, transparent=False, image_file=None):  # use mask to specify a certain shape
    global image
    if image_file is not None:
        if image_file.mode != 'RGBA':
            overlay = image_file.convert('RGBA')
        else:
            overlay = image_file
    else: 
        overlay = Image.open(image_path).convert('RGBA')

    if mask is not None:
        overlay = ImageOps.fit(overlay, mask.size, centering=(0.5, 0.5))
        overlay.putalpha(mask)
    overlay = overlay.resize((corners[2] - corners[0], corners[3] - corners[1]))
    if transparent:
        image.alpha_composite(overlay, (corners[0], corners[1]))
    else:
        image.paste(overlay, corners, overlay)
    
    if show_steps: image.show()


# puts the picture of the squaddy on the card
def set_picture():
    if real_rarity[contains_data(values['rarity'], rarity)] == 'unique':
        width = card_shape[0] - 20
        height = card_shape[1] - 25
        corners = (10, 10, width + 10, height + 10)
    else:
        wall_thickness_xy = (int(card_shape[0]*0.094), int(card_shape[1]*0.082))
        width = card_shape[0] - wall_thickness_xy[0] * 2
        height = int(card_shape[1] / 2.77)
        corners = (
            wall_thickness_xy[0], wall_thickness_xy[1], wall_thickness_xy[0] + width, wall_thickness_xy[1] + height)

    set_image('', corners, image_file=values['image'])


# sets the background of the card
def set_background():
    rare = real_rarity[contains_data(values['rarity'], rarity)]
    background_type = real_types[contains_data(values['type'][0], types)]
    if rare != 'unique':
        set_image(assets_path + 'background ' + background_type + ' ' + rare + ".png", (0, 0, card_shape[0], card_shape[1]))
    
    set_picture()

    if len(values['type']) > 1:
        frame_type = real_types[contains_data(values['type'][1], types)]
        set_image(assets_path + 'Edge ' + frame_type + ".png", (0, 0, card_shape[0], card_shape[1]))
    else:
        set_image(assets_path + 'Edge ' + background_type + ".png", (0, 0, card_shape[0], card_shape[1]))

    corners = (0, 0, card_shape[0], card_shape[1])
    if rare != 'unique':
        set_image(assets_path + 'Frame common' + ".png", corners)
        if rare != 'common':
            set_image(assets_path + 'Frame uncommon' + ".png", corners)
            if rare != 'uncommon':
                set_image(assets_path + 'Frame rare' + ".png", corners)


# puts all data for moves on the card
def set_moves():
    draw = ImageDraw.Draw(image)
    start = [50, math.ceil(card_shape[1] / 2) - 30]
    move_size = 36
    energy_size = move_size + 8
    move_max = 300
    description_size = 24
    spot = start.copy()

    # ability
    for i in range(1, 4):
        if f'ability {i} name' not in values:
            break
        ability_shape = (340, 90)
        icon_height = 40
        width = int(ability_shape[0]*(icon_height/ability_shape[1]))
        corners = (spot[0]-5, spot[1], spot[0]-5+width, spot[1]+icon_height)
        set_image(assets_path + "Ability icon.png", corners)
        spot[0] += width + 5

        font = ImageFont.truetype(assets_path + normal_font, move_size)
        set_text(values[f'ability {i} name'], font, (160, 0, 0), spot, move_max)
        spot[0] = start[0] + 30
        spot[1] += move_size + 10
        font = ImageFont.truetype(assets_path + normal_font, description_size)
        text = values[f'ability {i} desc']
        set_text(text, font, (0, 0, 0), spot, card_shape[0] - spot[0] - 60)

        size = textbox_shape(text, font, card_shape[0] - spot[0] - 60)
        height = size[1]
        spot[0] = start[0]
        spot[1] += height + 30
    
    for val in range(1, 4):
        if f'move {val} name' not in values:
            break
        # title of a move
        font = ImageFont.truetype(assets_path + big_font, move_size)
        set_text(values[f'move {str(val)} name'], font, (0, 0, 0), spot, move_max)

        # energy cost of move, first energy is put after the move name
        spot[0] += int(draw.textlength(values[f'move {str(val)} name'], font=font)) + 15
        for mood in values['move ' + str(val) + ' cost']:
            real_mood = real_types[contains_data(mood, types)]
            volatile = contains_data(mood, volatile_array) >= 0
            
            for number in range(int(mood[0])):
                if volatile:
                    name = assets_path + 'Energy ' + real_mood + ' volatile' + ".png"
                else:
                    name = assets_path + 'Energy ' + real_mood + ".png"
                set_image(name, (spot[0], spot[1], spot[0] + energy_size, spot[1] + energy_size))
                spot[0] += energy_size - 1

        #move damage type and stuff
        spot[0] = card_shape[0] - 25 - energy_size
        if 'move ' + str(val) + ' damage' in values and values['move ' + str(val) + ' damage'] != '0':
            file = filter(str.isdecimal, values['move ' + str(val) + ' damage'])
            damage = "".join(file)
            damage_type = real_damage_types[contains_data(values['move ' + str(val) + ' damage'], damage_types)]

            # move type icon (unused)
            if damage_type != 'None':
                set_image(assets_path + 'Type ' + damage_type + '.png',
                          (spot[0], spot[1], spot[0] + energy_size, spot[1] + energy_size))
            else:
                #damage type icon
                damage_color = type_colors[real_types_index[contains_data(values['move ' + str(val) + ' damage'], types)]]
                damage_color = (int(damage_color[0]*0.6),int(damage_color[1]*0.6),int(damage_color[2]*0.6))
                damage_type = real_types[contains_data(values['move ' + str(val) + ' damage'], types)]
                if damage_type != 'None':
                    set_image(assets_path + 'Energy ' + damage_type + '.png',
                              (spot[0], spot[1], spot[0] + energy_size, spot[1] + energy_size))
                else:
                    spot[0] = card_shape[0] - 25

            #damage value 
            if damage != '':
                spot[0] -= int(5 + draw.textlength(damage, font=font))
                set_text(damage, font, damage_color, spot, move_max)
            else:
                spot[0] -= int(5 + draw.textlength(damage, font=font))

        # description of move
        spot[0] = start[0] + 30
        spot[1] += 50
        font = ImageFont.truetype(assets_path + normal_font, description_size)
        text = values['move ' + str(val) + ' desc']
        set_text(text, font, (0, 0, 0), spot, card_shape[0] - spot[0] - 60)

        size = textbox_shape(text, font, card_shape[0] - spot[0] - 60)
        height = size[1]
        spot[0] = start[0]
        spot[1] += height + 30
    

# puts a bunch of smaller simple data in different places
def set_small_data():
    global values
    # card types
    spot = [card_shape[0] - 85, 26]
    energy_size = 55
    for mood in values['type']:  # also sets symbols in top right corner
        real_mood = real_types[contains_data(mood, types)]
        set_image(assets_path + 'Energy ' + real_mood + ".png", (spot[0], spot[1], spot[0] + energy_size
                                                                 , spot[1] + energy_size))
        spot[0] -= energy_size

    # HP
    font = ImageFont.truetype(assets_path + normal_font, 16)
    set_text('HP', font, (0, 0, 0), (40, 50), 1000, 1)
    font = ImageFont.truetype(assets_path + normal_font, 46)
    set_text(values['hp'], font, (0, 0, 0), (65, 24), 1000)
    # number
    font = ImageFont.truetype(assets_path + big_font, 28)
    set_text(values['entry'], font, (0, 0, 0), (30, card_shape[1] - 73), 1000, 1)

    # name and bar behind name
    top = 27
    title_size = 46
    font = ImageFont.truetype(assets_path + biggest_font, title_size)
    text = values['name']
    size = font.getlength(values['name'])
    rare = real_rarity[contains_data(values['rarity'], rarity)]
    if rare != 'unique':
        buffer_side = 7
        reduction_top = 2
        set_image(assets_path + 'Title end left.png', (int(card_shape[0] / 2 - size / 2)-buffer_side-title_size, top + reduction_top, int(card_shape[0] / 2 - size / 2)-buffer_side, top + reduction_top*2 +title_size+11))
        set_image(assets_path + 'Title end right.png', (int(card_shape[0] / 2 + size / 2)+buffer_side, top+reduction_top, int(card_shape[0] / 2 + size / 2)+buffer_side+title_size, top+reduction_top*2+title_size+11))
        set_image(assets_path + 'Title name.png', (int(card_shape[0] / 2 - size / 2)-buffer_side, top+reduction_top, int(card_shape[0] / 2 + size / 2)+buffer_side, top+ reduction_top*2+title_size+11))
    set_text(text, font, (0, 0, 0), (int(card_shape[0] / 2 - size / 2), top), 1000)

    # bottom bar with retreat and illustrator
    set_image(assets_path + 'Bottom line.png', (0, 0, card_shape[0], card_shape[1]), transparent=True)
    location_line = [40, 913]
    location_line2 = [420, 913]
    line_height = 30
    font = ImageFont.truetype(assets_path + normal_font, line_height+1)
    text = 'retreat'
    size = int(font.getlength(text))
    set_text(text, font, (0,0,0), (location_line[0], location_line[1]-1), 1000, 0)
    location_line[0] += size+10
    location_line[1] += 2
    for cost in range(0,int(values['retreat'])):
        set_image(assets_path + 'Energy neutral.png', (location_line[0], location_line[1], location_line[0]+line_height, location_line[1]+line_height))
        location_line[0] += line_height+2

    font = ImageFont.truetype(assets_path + biggest_font, line_height-2)
    set_text('Illus. '+ values['illustrator'], font, (0,0,0), location_line2, 1000, 0)

    # description
    font = ImageFont.truetype(assets_path + small_font, 17)
    text = values['description']
    size = textbox_shape(text, font, card_shape[0] - 150)
    set_text(text, font, (0, 0, 0), (110, card_shape[1] - size[1]-33), card_shape[0] - 150, 0)

    # passive
    passive_type = real_types[contains_data(values['type'][0], types)]
    passives = open(assets_path + 'passives.txt', 'r')
    text = 'Something went wrong if you are seeing this'
    for line in passives:
        data = line.split(': ')
        data = [value for value in data if value != '']
        if data[0] in passive_type.lower():
            text = data[1]
            text = text.replace('\n', '')
            break
    text = 'Passive: ' + text
    font = ImageFont.truetype(assets_path + normal_font, 24)
    size = textbox_shape(text, font, 600)
    spot = (int(card_shape[0]/2-(size[0]/2)), location_line[1]-size[1]-20)
    set_text(text, font, (0, 0, 0), spot, 600)



# puts a picture of the previous evolution and text next to it
def set_evolution():
    location = (40, 85)  # where the image will be
    diameter = 100
    size = (diameter, diameter)  # image cropped size
    ring_size = int(diameter * 0.1)
    ring_width = 2 * ring_size + size[0]


    if ('prev stage' in values) and (values['prev stage'] + '.png' in os.listdir(inputs_path)) and (values['prev stage'] + '.txt' in os.listdir(inputs_path)):
        value = values['prev stage']
            
        lines = open(inputs_path + value + '.txt', 'r')
        stage = 0
        for line in lines:
            if contains_data(line, evolution_array) >= 0:
                stage = 2
                break
            else:
                stage = 1

        mask = Image.new('L', size, 0)  # mask is for making it a circle
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)

        set_image(inputs_path + value + '.png', (location[0], location[1]
                                                 , location[0] + size[0], location[1] + size[1]), mask)

        font1 = ImageFont.truetype(assets_path + normal_font, 14)
        length1 = int(draw.textlength('Evolves from ', font=font1))
        font2 = ImageFont.truetype(assets_path + big_font, 28)
        length2 = int(draw.textlength(value, font=font2))
        length = length1 + length2

        set_image(assets_path + 'Evolution ring.png', (
        location[0] - ring_size, location[1] - ring_size, location[0] + size[0] + ring_size,
        location[1] + size[1] + ring_size))
        set_image(assets_path + 'Evolution name.png', (
        location[0] + size[0] + ring_size, location[1] - ring_size, location[0] + size[0] + ring_size + length,
        location[1] + size[1] + ring_size))
        set_image(assets_path + 'Evolution name end.png', (
        location[0] + size[0] + ring_size + length, location[1] - ring_size,
        location[0] + size[0] + ring_size + length + size[1] + 2 * ring_size, location[1] + size[1] + ring_size))
        set_image(assets_path + 'Evolution stage ' + str(stage) + '.png', (
        location[0] - ring_size + int(ring_width / 2), location[1] - ring_size,
        location[0] - ring_size + int(ring_width * 2.5), location[1] + size[1] + ring_size))

        set_text('Evolves from ', font1, (0, 0, 0),
                 (location[0] + size[0] + ring_size, location[1] - ring_size + int(ring_width / 5.2)), 1000, 0)
        set_text(value, font2, (0, 0, 0),
                 (location[0] + size[0] + ring_size + length1 + 5, location[1] - ring_size + int(ring_width / 13)),
                 1000, 1)
    else:
        set_image(assets_path + 'Evolution basic.png',
                  (location[0] + 2, location[1] - 3, location[0] + 2 + ring_width, location[1] + ring_width - 3))
                  


def set_weakness():
    weaknesses = {}
    fake_index = 0
    total = 0
    for type in real_types:
        if type not in weaknesses:
            no_damage = 'regular'
            damage = 0
            index = real_types_index[fake_index]
            for card_type in values['type']:
                card_type_index = real_types_index[contains_data(card_type, types)]
                effectiveness = Effectiveness_array[index][card_type_index]
                if effectiveness == 0:
                    no_damage = "No effect"
                elif effectiveness == 1:
                    damage -= 20
                    total -= 20
                elif effectiveness == 2:
                    damage = damage
                elif effectiveness == 3:
                    damage += 20
                    total += 20
                elif effectiveness == 4:
                    damage = damage
                    no_damage = 'Figure it out'

            if no_damage != 'regular':
                weaknesses[type] = no_damage
            else:
                weaknesses[type] = damage
            
        
        fake_index+=1
        if fake_index == len(real_types_index):
            break

    weaknesses['total'] = total

    if do_prints:
        print('Type effectiveness of ' + values['name'] + ': ' + str(weaknesses))
    return


def textbox_shape(text, font, width):
    draw = ImageDraw.Draw(image)
    size = draw.textlength(text, font=font)
    pixels_per_letter = size / len(text)
    lines = textwrap.wrap(text, width=math.ceil(width / pixels_per_letter))
    new_text = ""
    for line in lines:
        new_text += line + '\n'

    size = draw.multiline_textbbox((0, 0), new_text, font=font)
    height = size[3] - size[1]
    width = size[2] - size[0]
    return (width, height)

def restructure_text(text):
    if type(text) is not list:
        return text
    else:
        new_text = text[0]
        for value in text[1:]:
            new_text += ', ' + value          
        return new_text


# different steps for the image generation in order
def procedural_card():
    set_background()
    set_moves()
    set_small_data()
    set_evolution()
    set_weakness()
    return


# finds a substring in a given array and tells you where it was
def contains_data(array, possible_values):
    index = 0
    for value in possible_values:
        if value in array.lower():
            return index
        index += 1
    return -1


# stores all data from text file in a dictionary for look up
def generate_dict(file):
    values = {}

    for line in file:
        line = line.replace('\n', '')
        line = re.sub(' +', ' ', line)
        data = line.split(': ')
        data = [value for value in data if value != '']

        datatype = data[0]
        # moves
        if contains_data(datatype, move_array) >= 0:
            val = re.sub(r'\D', '', data[0])
            if contains_data(datatype, description_array) >= 0:  # if description
                values['move ' + val +  ' desc'] = data[1]
            elif contains_data(datatype, move_energy_array) >= 0:  # if energy
                values['move ' + val + ' cost'] = data[1].split(', ')
            elif contains_data(datatype, move_damage_array) >= 0:  # if damage
                values['move ' + val + ' damage'] = data[1]
            elif contains_data(datatype, name_array) >= 0:  # name if not energy nor description
                values['move ' + val + ' name'] = data[1]

        # abilities
        elif contains_data(datatype, ability_array) >= 0:
            val = re.sub(r'\D', '', data[0])
            if contains_data(datatype, description_array) >= 0:  # if description
                values['ability ' + val + ' desc'] = data[1]
            elif contains_data(datatype, name_array) >= 0:  # name if not description
                values['ability ' + val + ' name'] = data[1]

        # others
        elif contains_data(datatype, name_array) >= 0:
            values['name'] = data[1]
        elif contains_data(datatype, type_array) >= 0:
            values['type'] = data[1].split(', ')
        elif contains_data(datatype, id_array) >= 0:      
            values['entry'] = data[1]
        elif contains_data(datatype, evolution_array) >= 0:
            values['prev stage'] = data[1]
        elif contains_data(datatype, description_array) >= 0:
            values['description'] = data[1]
        elif contains_data(datatype, hp_array) >= 0:
            values['hp'] = data[1]
        elif contains_data(datatype, retreat_array) >= 0:
            values['retreat'] = data[1]
        elif contains_data(datatype, rarity_array) >= 0:
            values['rarity'] = data[1]
        elif contains_data(datatype, illus_array) >= 0:
            values['illustrator'] = data[1]
    
    if values['name'] + '.png' in os.listdir(inputs_path):
        values['image'] = Image.open(inputs_path + values['name'] + '.png')
    elif values['name'] + '.jpg' in os.listdir(inputs_path):
        values['image'] = Image.open(inputs_path + values['name'] + '.jpg')
    else:
        values['image'] = Image.open(assets_path + 'nameless.png')

    return values

def generate_card_from_values(new_values, editor_mode=False):
    global image
    global storage_path
    global values
    global do_prints

    do_prints = not editor_mode
    values = new_values

    procedural_card()
    return image


# does the text processing and starts the different steps of generating a card
def generate_card_from_file(file):
    global image
    global values

    values = generate_dict(file)
    procedural_card()
    image.save(storage_path + values['entry'] + ' ' + values['name'] + ".png")
