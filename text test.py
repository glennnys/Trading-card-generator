import re
import textwrap

from matplotlib.pylab import f

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
    print(f"parallel_string:\n\"{parallel_string}\"")

    result_string += parallel_string[prev_parallel_len:]  # Append to result string

    return result_string, items, substrings, line_of_items

# Example usage
input_string = "a:none:b:none:a:none:a:none:a:none:a:none:a:none:a:none:d:none:a:none:a:none:a:none:fdasfdasfdsafdddddddddddddddddddddddddddd:i:ddddddddddddddddddddddddfjikdlsafjmdksla;f:D: :DJFKLDAS;FJDASKLF;DJAKSL: :FDASFDASFDSAFDSAF: FJDSKALFDJSAKLFDJKLjklgrhjterbnvfdlllGFD:GFDGFD:X"
replacement_string = "    "

replaced_string, replaced_items, before_items, lines = process_string(input_string, replacement_string, 18)

# Output
print("Replaced String:\n", replaced_string)
print("Replaced Items:", replaced_items)
print("Substrings before Items:", before_items)
print("Lines of items: ", lines)

stringk = "abcdefg"