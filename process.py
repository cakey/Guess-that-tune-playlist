# -*- coding: utf-8 -*-
lines = []

with open("raw_24_dec_2015_backup.txt", 'r') as f:
    for line in f:
        line = line.translate(None, '\n')
        split_line = line.split(' – ')
        if len(split_line) > 2:
            print line
        switched_line = split_line[-1] + " – " + " – ".join(split_line[:-1])
        lines.append(switched_line)

lines = sorted(lines)
for line in lines:
    print line
