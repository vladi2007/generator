import matplotlib.pyplot as plt
import config as cf
import csv
from decimal import Decimal, getcontext
from PIL import Image, ImageDraw
from datetime import datetime
getcontext().prec = 30 #точность вычислений 28 значащих цифр

file_name="_result_mask_circles_0000.txt"
image = Image.open('./targets_with_mask/circles_0000.png')
with open(cf.path_to_mask+file_name,"r") as file:
    getcontext().prec = 30 #точность вычислений 28 значащих цифр
    background = Image.new('RGB', (2560, 1440), (190, 134, 109))
    fig, ax = plt.subplots()
    ax.imshow(image)
    for row in file:
        
        # Преобразуем строку координат в массив чисел
        coordinates = list(map(Decimal, row.split()))
    
        # Разделяем координаты на пары (x, y)
        coordinates.append(Decimal(coordinates[1]))
        coordinates.append(Decimal(coordinates[2]))
        x_coords = [i * 1280 for i in coordinates[1::2]]
        y_coords = [i * 1280 for i in coordinates[2::2]]
        
        # Рисуем линии по координатам
        ax.plot(x_coords, y_coords, color="red", linewidth=2)
    plt.show()