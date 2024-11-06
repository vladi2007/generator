import numpy as np
from decimal import Decimal, getcontext

orange_folder = './circles/orange'
grey_folder = './circles/grey'
orange_txt="./orange_txt"
grey_txt="./grey_txt"
grey={}
grey_number=[2,3,4,5,7,8,9,10,11,12,13,14,15,16,17,22,23,25,27,29,31]
orange={}
orange_number=[1,6,18,19,24,26,28,30]
orange_number_new=range(36,56)
grey_number_new=range(1,36)
grey_pics_radius={
}
orange_pics_radis={}

def parse_coords(folder_name,list_numbers,folder_txt,dict,img_name="",img_txt=""):
    getcontext().prec = 28 
    for image_num in list_numbers:
        image_name=folder_name + f"/drop_{image_num}.png{img_name}"
        image_txt=folder_txt + f"/drop_{image_num}{img_txt}.txt"
        with open(image_txt , 'r', encoding='utf-8') as file:
            for line in file:
                coords_list=line.split()
                list_to_dict=[]
                for i in range(1,len(coords_list)-1,2):
                    x=Decimal(float(coords_list[i])*100)
                    y=Decimal(float((coords_list[i+1]))*100)
                    list_to_dict.append((x,y))
                dict.update({image_name:list_to_dict })

def calculate_circle_radius(folder_name,list_numbers,dict,result,list_of_coords,img_txt=""):
    getcontext().prec = 28 
    for image_num in list_numbers:
        points = np.array(dict[folder_name + f"/drop_{image_num}.png{img_txt}"])
        
        # Находим центр круга (среднее значение координат)
        center = np.mean(points, axis=0).astype(Decimal)
        
        # Вычисляем радиус как среднее расстояние от центра до каждой точки
        radius = np.mean(np.linalg.norm(points - center, axis=1))
        result_radius=(radius)
        result.update({result_radius:(f"./drop_{image_num}.png{img_txt}",int(float(center[0])),int(float(center[1])))})
        list_of_coords.append((result_radius,Decimal(float(center[0])),Decimal(float(center[1]))))