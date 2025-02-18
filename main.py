from operator import le
from tarfile import data_filter
from webbrowser import get
from PIL import Image, ImageOps
from PIL import ImageFont
from PIL import ImageDraw
import io
import re
import math
import textwrap
import sqlite3
import threading

import matplotlib.pyplot as plt

# set to change card shape and size, most things move with it. sort of
card_shape = (747, 1038)
show_steps = False
do_prints = True
conn = sqlite3.connect('cards.db')
c = conn.cursor()

# important paths
biggest_font = 'Roboto-BoldItalic'
big_font = 'Roboto-Bold'
normal_font = 'Roboto-Medium'
small_font = 'Roboto-Regular'
description_font = 'papyrus'
consumed_energy = 'volatile' #name for energy cost that disappears after use

# global variables
image = Image.new('RGBA', card_shape)
values = {}

def process_string(input_string, replacement_string, wrap_width):
    items = []  # List to store replaced items
    line_of_items = []
    positions_of_items = []  # List to store positions of replaced items
    substrings = []  # List to store substrings before replaced items
    replacement_width = len(replacement_string)
    
    # This pattern finds parts like :text:
    pattern = r':(\w+):'
    
    last_pos = 0
    result_string = ""
    parallel_string = ""
    parallel_replacement = "x" * replacement_width

    prev_parallel_len = 0
    
    # wraps two parallel strings to the same width, one with xxxx and the other with the real replacement string. this is to get propper wrapping if the replacement string is made from spaces
    for match in re.finditer(pattern, input_string):
        item = match.group(1)  # Capture text inside :text:
        
        parallel_string += input_string[last_pos:match.start()]  # Keep full text before match in result
        parallel_string += parallel_replacement  # Perform replacement
        parallel_string = textwrap.fill(parallel_string, wrap_width)

        n_location = parallel_string.rfind('\n') + 1
        before_part = n_location - (len(parallel_string) - replacement_width)

        if before_part > 0:
            result_string += parallel_string[prev_parallel_len:n_location-before_part-1] + '\n' + replacement_string  # Append to result string
        else:
            result_string += parallel_string[prev_parallel_len:-replacement_width] + replacement_string  # Append to result string

        prev_parallel_len = len(parallel_string)

        line_start = result_string.rfind('\n') + 1
        before_match = result_string[line_start:-replacement_width]

        substrings.append(before_match)  # Save string before replacement within the same line
        items.append(item)
        line = len(re.findall('\n', result_string))
        line_of_items.append(line)
        
        last_pos = match.end()  # Update last_pos

    # Append remaining part of the string
    parallel_string += input_string[last_pos:]
    parallel_string = textwrap.fill(parallel_string, wrap_width)

    result_string += parallel_string[prev_parallel_len:]  # Append to result string

    return result_string, items, substrings, line_of_items


# base function used by other functions, code that add text in a certain spot and makes sure the text folds over
# when the maximum width is achieved
def get_asset(name, c = c):
    name = name.lower()
    c.execute('''SELECT asset from Assets where assetName = ?''', (name,))
    data = c.fetchone()
    if data:
        return data[0]
    else:
        c.execute('''SELECT asset from Assets where assetName = ?''', ("placeholder",))
        data = c.fetchone()
        return data[0]

def get_font(name, size, c = c):
    name = name.lower()
    c.execute('''SELECT asset from Assets where assetName = ?''', (name,))
    data = c.fetchone()
    font = ImageFont.truetype(io.BytesIO(data[0]), size)
    return font

def set_text(text, font, color, corner, width, stroke=2, c=c):
    global image
    draw = ImageDraw.Draw(image)
    
    # Calculate the size of the text
    size = draw.textlength(text, font=font)
    pixels_per_letter =0.95 * size / len(text)
   
    height = font.size #the total height of the font from lower letters like p q and y to highest letters like t l and d
    offset = font.font.height #supposedly the actual height including the distance between two lines
    ascent, descent = font.getmetrics() 

    
    # Wrap text according to the available width
    new_text, replaced_items, before_items, lines = process_string(text, '    ', math.ceil(width / pixels_per_letter))
    
    positions = []  # To store the positions of the items in the text
    starting_pos = [corner[0], corner[1]]

    for item, before_item_text, line in zip(replaced_items, before_items, lines):
        width = int(draw.textlength(before_item_text, font=font))
        positions.append((starting_pos[0] + width, starting_pos[1] + int(offset*line*1.1) + descent))



    # Now we know the positions for each item, we can place images at those positions
    if stroke:
        draw.text(corner, new_text, color, font=font, stroke_width=stroke, stroke_fill='white')
    else:
        draw.text(corner, new_text, color, font=font)

    #place images
    for item, position in zip(replaced_items, positions):
        item = item.replace("_", " ")
        img=get_asset(item, c)
        set_image(img, (position[0], position[1], position[0]+height, position[1]+height))

    if show_steps: image.show()


# base function used by other functions, code that adds images to the existing card within specified region
def set_image(image_file, corners, mask=None, transparent=False):  # use mask to specify a certain shape
    global image
    image_file = io.BytesIO(image_file)
    image_file = Image.open(image_file)
    if image_file.mode != 'RGBA':

        overlay = image_file.convert('RGBA')
    else:
        overlay = image_file

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
    # check if rarity is the same as the highest rarity
    if values['rarity'] == values['existing rarities'][-1]:
        width = card_shape[0] - 21
        height = card_shape[1] - 26
        corners = (10, 10, width + 10, height + 10)
    else:
        wall_thickness_xy = (int(card_shape[0]*0.095), int(card_shape[1]*0.083))
        width = card_shape[0] - wall_thickness_xy[0] * 2
        height = int(card_shape[1] / 2.77)
        corners = (
            wall_thickness_xy[0], wall_thickness_xy[1], wall_thickness_xy[0] + width, wall_thickness_xy[1] + height)
        
    if 'crop' in values and values['crop'] != '':
        cropped_image = Image.open(io.BytesIO(values['image'])).crop(values['crop'])
        byte_image = io.BytesIO()
        cropped_image.save(byte_image, format='PNG')
        byte_image = byte_image.getvalue()
        set_image(byte_image, corners)
    else:
        set_image(values['image'], corners)


# sets the background of the card
def set_background(c = c):
    background_type = values['type'][0]
    rarity = values['rarity']

    if rarity == values['existing rarities'][-1]:
        # for highest rarity, set full size image only
        set_picture()
    else:
        set_image(get_asset(f'background {background_type} {rarity}', c), (0, 0, card_shape[0], card_shape[1]))
        set_picture()

        # upgrade the border for each rarity tier below the highest
        corners = (0, 0, card_shape[0], card_shape[1])
        rarity_index = values['existing rarities'].index(rarity)
        for i in range(rarity_index+1):
            set_image(get_asset(f'Frame {values["existing rarities"][i]}', c), corners)

    # set the edge of the card
    if len(values['type']) > 1:
        frame_type = values['type'][1]
        set_image(get_asset('edge ' + frame_type, c), (0, 0, card_shape[0], card_shape[1]))
    else:
        set_image(get_asset('edge ' + background_type, c), (0, 0, card_shape[0], card_shape[1]))


# puts all data for moves on the card
def set_moves(c = c):
    draw = ImageDraw.Draw(image)
    startx = 50
    starty = int(math.ceil(card_shape[1] / 2) - 30)
    move_size = 36
    energy_size = move_size + 8
    move_max = 300
    description_size = 24
    spot = [startx, starty]

    # ability
    for i in range(1, 4):
        if f'ability {i} name' not in values:
            break
        ability_shape = (340, 90)
        icon_height = 40
        width = int(ability_shape[0]*(icon_height/ability_shape[1]))
        corners = (spot[0]-5, spot[1], spot[0]-5+width, spot[1]+icon_height)
        set_image(get_asset("Ability icon", c), corners)
        spot[0] += width + 5

        font = get_font(normal_font, move_size, c)
        set_text(values[f'ability {i} name'], font, (160, 0, 0), spot, move_max, c=c)
        spot[0] = startx + 30
        spot[1] += move_size + 10

        font = get_font(normal_font, description_size, c)
        text = values[f'ability {i} desc']
        set_text(text, font, (0, 0, 0), spot, card_shape[0] - spot[0] - 60, c=c)

        size = textbox_shape(text, font, card_shape[0] - spot[0] - 60)
        height = size[1]
        spot[0] = startx
        spot[1] += int(height + 30)
    
    for val in range(1, 4):
        if f'move {val} name' not in values:
            break
        # title of a move
        font = get_font(big_font, move_size, c)
        set_text(values[f'move {str(val)} name'], font, (0, 0, 0), spot, move_max, c=c)

        # energy cost of move, first energy is put after the move name
        spot[0] += int(draw.textlength(values[f'move {str(val)} name'], font=font)) + 15
        for cost in values['move ' + str(val) + ' cost']:
            # return the type of energy cost that is in values['existing types']
            cost_type = values['existing types'][contains_data(cost, values['existing types'])]
            volatile = consumed_energy in cost

            for number in range(int(cost[0])):
                if volatile:
                    name = get_asset(f'Energy {cost_type} {consumed_energy}', c)
                else:
                    name = get_asset(f'Energy {cost_type}', c)

                set_image(name, (spot[0], spot[1], spot[0] + energy_size, spot[1] + energy_size))
                spot[0] += energy_size - 1

        #move damage type and stuff
        spot[0] = card_shape[0] - 25 - energy_size
        if 'move ' + str(val) + ' damage' in values and values['move ' + str(val) + ' damage'] != '0':
            file = filter(str.isdecimal, values['move ' + str(val) + ' damage'])
            damage = "".join(file)
            damage_type = values['existing types'][contains_data(values['move ' + str(val) + ' damage'], values['existing types'])]
            
            #damage type icon
            damage_color = values['colors'][damage_type]
            damage_color = (int(damage_color[0]*0.6),int(damage_color[1]*0.6),int(damage_color[2]*0.6))
            if damage_type != 'None':
                set_image(get_asset('Energy ' + damage_type, c),
                            (spot[0], spot[1], spot[0] + energy_size, spot[1] + energy_size))
            else:
                spot[0] = card_shape[0] - 25

            #damage value 
            if damage != '':
                spot[0] -= int(5 + draw.textlength(damage, font=font))
                set_text(damage, font, damage_color, spot, move_max, c=c)
            else:
                spot[0] -= int(5 + draw.textlength(damage, font=font))

        # description of move
        spot[0] = startx + 30
        spot[1] += int(50)
        font = get_font(normal_font, description_size, c)
        text = values['move ' + str(val) + ' desc']
        set_text(text, font, (0, 0, 0), spot, card_shape[0] - spot[0] - 60, c=c)

        size = textbox_shape(text, font, card_shape[0] - spot[0] - 60)
        height = size[1]
        spot[0] = startx
        spot[1] += int(height + 30)
    

# puts a bunch of smaller simple data in different places
def set_small_data(c = c):
    global values
    # card types
    spot = [card_shape[0] - 85, 26]
    energy_size = 55
    for card_type in values['type']:  # also sets symbols in top right corner
        set_image(get_asset('Energy ' + card_type, c), (spot[0], spot[1], spot[0] + energy_size
                                                                 , spot[1] + energy_size))
        spot[0] -= energy_size

    # HP
    font = get_font(normal_font, 16, c)
    set_text('HP', font, (0, 0, 0), (60, 50), 1000, 1, c=c)
    font = get_font(normal_font, 46, c)
    set_text(values['hp'], font, (0, 0, 0), (85, 24), 1000, c=c)
    # number
    font = get_font(big_font, 28, c)
    set_text(values['entry'], font, (0, 0, 0), (30, card_shape[1] - 73), 1000, 1, c=c)

    # name and bar behind name
    top = 27
    title_size = 46
    font = get_font(biggest_font, title_size, c)
    text = values['name']
    size = font.getlength(values['name'])

    if values['rarity'] != values['existing rarities'][-1]:
        buffer_side = 7
        reduction_top = 2
        set_image(get_asset('Title end left', c), (int(card_shape[0] / 2 - size / 2)-buffer_side-title_size, top + reduction_top, int(card_shape[0] / 2 - size / 2)-buffer_side, top + reduction_top*2 +title_size+11))
        set_image(get_asset('Title end right', c), (int(card_shape[0] / 2 + size / 2)+buffer_side, top+reduction_top, int(card_shape[0] / 2 + size / 2)+buffer_side+title_size, top+reduction_top*2+title_size+11))
        set_image(get_asset('Title name', c), (int(card_shape[0] / 2 - size / 2)-buffer_side, top+reduction_top, int(card_shape[0] / 2 + size / 2)+buffer_side, top+ reduction_top*2+title_size+11))
    set_text(text, font, (0, 0, 0), (int(card_shape[0] / 2 - size / 2), top), 1000, c=c)

    # bottom bar with retreat and illustrator
    set_image(get_asset('Bottom line', c), (0, 0, card_shape[0], card_shape[1]), transparent=True)
    location_line = [40, 913]
    location_line2 = [420, 913]
    line_height = 30
    font = get_font(normal_font, line_height+1, c)
    text = 'retreat'
    size = int(font.getlength(text))
    set_text(text, font, (0,0,0), (location_line[0], location_line[1]-1), 1000, 0, c=c)
    location_line[0] += size+10
    location_line[1] += 2
    for cost in range(0,int(values['retreat'])):
        set_image(get_asset('Energy neutral', c), (location_line[0], location_line[1], location_line[0]+line_height, location_line[1]+line_height))
        location_line[0] += line_height+2

    font = get_font(biggest_font, line_height-2, c)
    set_text('Illus. '+ values['illustrator'], font, (0,0,0), location_line2, 1000, 0, c=c)

    # description
    font = get_font(small_font, 17, c)
    text = values['description']
    size = textbox_shape(text, font, card_shape[0] - 150)
    set_text(text, font, (0, 0, 0), (110, card_shape[1] - size[1]-33), card_shape[0] - 150, 0, c=c)

    # passive
    text = 'Passive: ' + values['passive']
    font = get_font(normal_font, 24, c)
    size = textbox_shape(text, font, 600)
    spot = (int(card_shape[0]/2-(size[0]/2)), location_line[1]-size[1]-20)
    set_text(text, font, (0, 0, 0), spot, 600, c=c)



# puts a picture of the previous evolution and text next to it
def set_evolution(c = c):
    location = (40, 85)  # where the image will be
    diameter = 100
    size = (diameter, diameter)  # image cropped size
    ring_size = int(diameter * 0.1)
    ring_width = 2 * ring_size + size[0]


    if ('prevolve' in values):
        value = values['prevolve']
        c.execute('''SELECT name, prevolve, image, crop1, crop2, crop3, crop4 FROM get_cards_infos
                    WHERE name = ?''', (values['prevolve'],))
        data = c.fetchone()

        if data is not None:
            stage = 0
            if data[1] is not None:
                stage = 2
            else:
                stage = 1

            mask = Image.new('L', size, 0)  # mask is for making it a circle
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + size, fill=255)

            if data[2] is not None:
                prevolve_image = Image.open(io.BytesIO(data[2]))
            else:
                prevolve_image = get_asset('nameless', c)
            

            if data[3] is not None:
                corners = (data[3], data[4], data[5], data[6])
                cropped_image = Image.open(io.BytesIO(values['image'])).crop(corners)
                prevolve_image = io.BytesIO()
                cropped_image.save(prevolve_image, format='PNG')
                prevolve_image = prevolve_image.getvalue()

            set_image(prevolve_image, (location[0], location[1]
                                     , location[0] + size[0], location[1] + size[1]),  mask)

            font1 = get_font(normal_font, 14, c)
            length1 = int(draw.textlength('Evolves from ', font=font1))
            font2 = get_font(big_font, 28, c)
            length2 = int(draw.textlength(value, font=font2))
            length = length1 + length2

            set_image(get_asset('Evolution ring', c), (
            location[0] - ring_size, location[1] - ring_size, location[0] + size[0] + ring_size,
            location[1] + size[1] + ring_size))
            set_image(get_asset('Evolution name', c), (
            location[0] + size[0] + ring_size, location[1] - ring_size, location[0] + size[0] + ring_size + length,
            location[1] + size[1] + ring_size))
            set_image(get_asset('Evolution name end', c), (
            location[0] + size[0] + ring_size + length, location[1] - ring_size,
            location[0] + size[0] + ring_size + length + size[1] + 2 * ring_size, location[1] + size[1] + ring_size))
            set_image(get_asset('Evolution stage ' + str(stage), c), (
            location[0] - ring_size + int(ring_width / 2), location[1] - ring_size,
            location[0] - ring_size + int(ring_width * 2.5), location[1] + size[1] + ring_size))

            set_text('Evolves from ', font1, (0, 0, 0),
                    (location[0] + size[0] + ring_size, location[1] - ring_size + int(ring_width / 5.2)), 1000, 0, c=c)
            set_text(value, font2, (0, 0, 0),
                    (location[0] + size[0] + ring_size + length1 + 5, location[1] - ring_size + int(ring_width / 13)),
                    1000, 1, c=c)
    else:
        if values['rarity'] == values['existing rarities'][-1]:
            set_image(get_asset('Evolution basic', c),
                (-7, 18, -7 + ring_width, 18 + ring_width))
        else:
            set_image(get_asset('Evolution basic', c),
                (location[0] + 10, location[1] + 5, location[0] + 10 + ring_width, location[1] + ring_width + 5))
                  


# def set_weakness():
#     weaknesses = {}
#     fake_index = 0
#     total = 0
#     for type in real_types:
#         if type not in weaknesses:
#             no_damage = 'regular'
#             damage = 0
#             index = real_types_index[fake_index]
#             for card_type in values['type']:
#                 card_type_index = real_types_index[contains_data(card_type, types)]
#                 effectiveness = Effectiveness_array[index][card_type_index]
#                 if effectiveness == 0:
#                     no_damage = "No effect"
#                 elif effectiveness == 1:
#                     damage -= 20
#                     total -= 20
#                 elif effectiveness == 2:
#                     damage = damage
#                 elif effectiveness == 3:
#                     damage += 20
#                     total += 20
#                 elif effectiveness == 4:
#                     damage = damage
#                     no_damage = 'Figure it out'

#             if no_damage != 'regular':
#                 weaknesses[type] = no_damage
#             else:
#                 weaknesses[type] = damage
            
        
#         fake_index+=1
#         if fake_index == len(real_types_index):
#             break

#     weaknesses['total'] = total

#     if do_prints:
#         print('Type effectiveness of ' + values['name'] + ': ' + str(weaknesses))
#     return


def set_effect_background():
    return


def set_description():
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
def procedural_card(c = c):
    set_background(c)
    set_moves(c)
    set_small_data(c)
    set_evolution(c)
    #set_weakness()
    return

def procedural_effect_card():
    set_effect_background()
    set_description()
    return

# finds a substring in a given array and tells you where it was
def contains_data(array, possible_values):
    index = 0
    for value in possible_values:
        if value in array.lower():
            return index
        index += 1
    return -1

def set_default(c = c):
    values = {}

    # get all types
    c.execute('''SELECT type, colorR, colorG, colorB from Types''')
    types = c.fetchall()
    values['existing types'] = [card_type[0] for card_type in types]
    values['colors'] = {card_type[0]: (card_type[1], card_type[2], card_type[3]) for card_type in types}

    # get uniqueness
    c.execute('''SELECT rarity from Rarities''')
    rarities = c.fetchall()
    values['existing rarities'] = [rarity[0] for rarity in rarities]

    # get other stuff

    values['name'] = 'nameless'
    values['hp'] = '0'
    values['rarity'] = 'common'
    values['type'] = ['neutral']
    values['passive'] = "None"
    values['move 1 name'] = 'moveless'
    values['move 1 desc'] = 'no description'
    values['move 1 damage'] = '0 neutral'
    values['move 1 cost'] = ['0 neutral']
    values['retreat'] = '0'
    values['entry'] = '0'
    values['description'] = 'bitch lasagne'
    values['illustrator'] = 'no illustrator'
    values['image'] = get_asset('nameless', c)

    return values


def store_card(c = c):

    crop = values['crop'] if 'crop' in values else [None, None, None, None]
    prevolve = values['prevolve'] if 'prevolve' in values else None

    ## remove old card types
    c.execute("""DELETE FROM cardsXtypes
                WHERE cardID = (SELECT cardID FROM Cards WHERE name = ?);""", (values['name'],))
        
    ## remove old card moves
    c.execute("""DELETE FROM cardsXMoves
                WHERE cardID = (SELECT cardID FROM Cards WHERE name = ?);""", (values['name'],))

    ## store card data
    c.execute("""INSERT INTO Cards (name, description, prevolve, hp, retreat, rarity, entry, illustrator, image, upperleftx, upperlefty, bottomrightx, bottomrighty, variantType)
                SELECT ?, ?, ?, ?, ?, r.rarityID, ?, ?, ?, ?, ?, ?, ?, 1
                FROM Rarities r WHERE r.rarity = ?
                ON CONFLICT (name) DO UPDATE SET
                description = excluded.description,
                hp = excluded.hp,
                prevolve = excluded.prevolve,
                retreat = excluded.retreat,
                rarity = excluded.rarity,
                entry = excluded.entry,
                illustrator = excluded.illustrator,
                image = excluded.image,
                upperleftx = excluded.upperleftx,
                upperlefty = excluded.upperlefty,
                bottomrightx = excluded.bottomrightx,
                bottomrighty = excluded.bottomrighty;""", (values['name'], values['description'],
                                                            prevolve, values['hp'], values['retreat'],
                                                            values['entry'], values['illustrator'], values['image'], crop[0], 
                                                            crop[1], crop[2], crop[3] , values['rarity']))
    
    ## store card types
    for value in values['type']:
        isPrimary = 1 if value == values['type'][0] else 0
        c.execute("""INSERT INTO CardsXTypes (cardID, typeID, isPrimary)
                    SELECT c.cardID, t.typeID, ?
                    FROM Types t
                    JOIN Cards c ON c.name = ?
                    WHERE t.type = ?;""", (isPrimary ,values['name'], value))
        
    ## store card moves
    print({k:v for k,v in values.items() if k not in ["image"]})
    num_moves = max([int(''.join(filter(str.isdigit, key))) for key in values.keys() if key.startswith('move')])
    for i in range(1, num_moves+1):
        c.execute("""INSERT INTO Moves (moveName, damage, description, isAbility, typeID) 
                    SELECT ?, ?, ?, 0, t.typeID
                    FROM Types t
                    WHERE t.type = ?
                    ON CONFLICT (moveName) DO UPDATE SET
                    moveName = excluded.moveName,
                    damage = excluded.damage,
                    description = excluded.description,
                    isAbility = excluded.isAbility,
                    typeID = excluded.typeID;""", (values[f'move {i} name'], values[f'move {i} damage'].split(' ')[0], values[f'move {i} desc'], values[f'move {i} damage'].split(' ')[1]))
        
        for cost in values[f'move {i} cost']:
            c.execute("""INSERT INTO MoveCosts (moveID, typeID, amount, volatile)
                        SELECT m.moveID, t.typeID, ?, ?
                        FROM Types t
                        JOIN Moves m ON m.moveName = ?
                        WHERE t.type = ?""", (cost.split(' ')[1], 1 if 'Volatile' in cost else 0, values[f'move {i} name'], cost.split(' ')[0]))
            
        ## link card to move
        c.execute("""INSERT INTO cardsXMoves (cardID, moveID)
                    SELECT c.cardID, m.moveID
                    FROM Moves m
                    JOIN Cards c ON c.name = ?
                    WHERE m.moveName = ?;""", (values['name'], values[f'move {i} name']))
                  
            
    ## store card abilities
    num_abilities = max([int(''.join(filter(str.isdigit, key))) for key in values.keys() if key.startswith('ability')] + [0])
    for i in range(1, num_abilities+1):
        c.execute("""INSERT INTO Moves (moveName, description, isAbility) 
                    VALUES (?, ?, 1)
                    ON CONFLICT (moveName) DO UPDATE SET
                    moveName = excluded.moveName,
                    description = excluded.description;""", (values[f'ability {i} name'], values[f'ability {i} desc']))
        
        ## link card to ability
        c.execute("""INSERT INTO cardsXMoves (cardID, moveID)
                    SELECT c.cardID, m.moveID, ?
                    FROM Moves m
                    JOIN Cards c ON c.name = ?
                    WHERE m.moveName = ?;""", (values['name'], values[f'ability {i} name']))

    conn.commit()


# stores all data from text file in a dictionary for look up
def generate_dict(name, c):
    values = {}

    # get all types
    c.execute('''SELECT type, colorR, colorG, colorB from Types''')
    types = c.fetchall()
    values['existing types'] = [card_type[0] for card_type in types]
    values['colors'] = {card_type[0]: (card_type[1], card_type[2], card_type[3]) for card_type in types}

    # get uniqueness
    c.execute('''SELECT rarity from Rarities''')
    rarities = c.fetchall()
    values['existing rarities'] = [rarity[0] for rarity in rarities]

    try:
        c.execute('''SELECT * FROM get_cards_infos
                WHERE name = ?
                ''', (name,))
        data = c.fetchone()
        values['name'] = data[0]
        values['description'] = data[1]
        values['hp'] = str(data[2])
        if data[3] is not None:
            values['prevolve'] = data[3]
        values['retreat'] = data[4]
        values['rarity'] = data[5]
        if data[6] is not None:
            values['illustrator'] = data[6]
        else :
            values['illustrator'] = 'Unknown'	
        values['entry'] = str(data[7])
        if data[8] is not None:
            values['image'] = data[8]
        else:
            values['image'] = get_asset('nameless', c)

        crop = (data[9], data[10], data[11], data[12])
        if not None in crop:
            values['crop'] = (data[9], data[10], data[11], data[12])


        c.execute('''SELECT * FROM get_card_types
                    WHERE name = ?''', (name,))
        data = c.fetchall()

        if len(data) != 0:
            values['type'] = [value[0] for value in data if value[2]]
            values['type'].extend([value[0] for value in data if not value[2]])
            values['passive'] = next((value[1] for value in data if value[2]), data[0][1])
        else:
            values['type'] = ['neutral']
            values['passive'] = 'None'

        c.execute('''SELECT * FROM get_moves 
                    WHERE name = ?
                ''', (name,))         
        data = c.fetchall()

        abilitynr = 1
        movenr = 1
        for value in data:
            if value[4] == 1:
                values[f'ability {abilitynr} name'] = value[0]
                values[f'ability {abilitynr} desc'] = value[3]
                abilitynr += 1
            else:
                values[f'move {movenr} name'] = value[0]
                values[f'move {movenr} damage'] = f'{value[2]} {value[1]}'
                values[f'move {movenr} desc'] = value[3]
                costs = c.fetchall()

                values[f'move {movenr} cost'] = [f'{value[1]} {value[0]}{"" if value[2] == 0 else " Volatile"}' for value in costs]
                movenr += 1  
    except Exception as e:
        print('Card not found or error in database. Using default values. ', e)
        values = set_default()  
    return values


def generate_effect_dict(file):
    values = {}

    for line in file:
        line = line.replace('\n', '')
        line = re.sub(' +', ' ', line)
        data = line.split(': ')
        data = [value for value in data if value != '']

        datatype = data[0]

    return values

def generate_effect_card(new_values, editor_mode=False):
    global image
    global storage_path
    global values
    global do_prints

    do_prints = not editor_mode
    values = new_values

    procedural_effect_card()
    return image

def generate_all_cards():
    global image
    global values
    global c
    conn = sqlite3.connect('cards.db')
    c = conn.cursor()

    c.execute("SELECT * FROM get_cards")
    data = c.fetchall()

    for i in data:
        if i[1] == 'Regular':
            values = generate_dict(i[0], c)
            procedural_card()
            image.show()

    conn.close()

# does the text processing and starts the different steps of generating a card
def generate_card_from_db(name, c=c):
    global image
    global values

    c.execute("SELECT * FROM get_cards WHERE name = ?", (name,))
    data = c.fetchone()
    if data[1] == 'Regular':
        values = generate_dict(data[0], c)
        procedural_card()

        image_blob = io.BytesIO()
        image.save(image_blob, format='PNG')
        image_blob = image_blob.getvalue()
        try:
            c.execute('''
                INSERT INTO finishedCards (cardID, card)
                VALUES(?, ?)
                ON CONFLICT(cardID) 
                DO UPDATE SET card = excluded.card
            ''', (data[2], image_blob))

            conn.commit()

            print(f"Image '{name}' inserted successfully as a BLOB in the database.")

        except sqlite3.Error as error:
            print(f"Failed to insert image into sqlite table: {error}")


    conn.close()

def swap_db_connection(new_conn):
    global c
    c = new_conn.cursor()

def preview_card(card_values, c=c, editor_mode=False):
    global image
    global values
    global do_prints

    do_prints = not editor_mode

    values = card_values

    procedural_card(c)
    store_card(c)

    return image

#generate_card_from_db('Glenninja')