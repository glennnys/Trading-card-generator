v = [1, 10, 3]

entry_options = [f'{i}' for i in range(20)]

for i in range(len(v)):
        if v[-i-1] != 1:
            entry_options.pop(int(v[-i-1]))

print(entry_options)
