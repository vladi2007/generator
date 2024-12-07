import numpy as np
from decimal import Decimal, getcontext
# (640,80,1920,1360)
file = "./contur_mask/mask.txt"
contur_mask_coords = []


def parse_contur_coords(path, result_list):
    context = getcontext()
    context.prec = 30
    with open(path, 'r', encoding='utf-8') as file:
        for line in file:
            coords_list = line.split()
            for i in range(1, len(coords_list)-1, 2):
                x = Decimal(coords_list[i])*2560
                y = Decimal(coords_list[i+1])*1440
                # бывает что все равно вылезает за границы картинки - плюсую epsilon
                if (640+20 < x < 1920-15) and (80+14 < y < 1360-6):
                    result_list.append((x, y))


parse_contur_coords(file, contur_mask_coords)
