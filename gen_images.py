import config as cf
import random
import os
from collections import namedtuple
import numpy as np
import radius_of_circles as roc
from shapely.geometry import Polygon
from PIL import Image, ImageDraw
import contur_mask as cm
import cv2
from decimal import Decimal, getcontext



krug= Image.open(os.path.join("krug.png")) # маска кружка 
lineyka= Image.open(os.path.join("lineyka.png")) # маска линейки

#кортеж для cropp
cropp_tuple=(640,80,1920,1360)

# словарь для определения цвета фона и папки с соответсвующими каплями
dict_rgb_circles_path={1:((190,134, 109),'./circles/orange'), 
      0:((150,150, 150),'./circles/grey')}


# переменные для хранения данных о каплях
contur_mask_coords=[]
result_list_of_coords_orange=[]
result_list_of_coords_grey=[]
grey_data={}
orange_data={}

#для слипшихся капель
rnd_list=[1,2]

#вызов методов для получения данных 
def help():
    cm.parse_contur_coords(cm.file,contur_mask_coords)
    roc.parse_coords(roc.grey_folder,roc.grey_number,roc.grey_txt,roc.grey)
    roc.parse_coords(roc.orange_folder,roc.orange_number,roc.orange_txt,roc.orange)
    roc.calculate_circle_radius(roc.orange_folder,roc.orange_number,roc.orange,orange_data,result_list_of_coords_orange)
    roc.calculate_circle_radius(roc.grey_folder,roc.grey_number,roc.grey,grey_data,result_list_of_coords_grey)

    roc.parse_coords(roc.grey_folder,roc.grey_number_new,roc.grey_txt,roc.grey,".png",".jpg")
    roc.parse_coords(roc.orange_folder,roc.orange_number_new,roc.orange_txt,roc.orange,".png",".jpg")
    roc.calculate_circle_radius(roc.orange_folder,roc.orange_number_new,roc.orange,orange_data,result_list_of_coords_orange,".png")
    roc.calculate_circle_radius(roc.grey_folder,roc.grey_number_new,roc.grey,grey_data,result_list_of_coords_grey,".png")


#генерируем список слипшихся окружностей вида 'x y r w'
def make_neighbourhood_circles(rnd_num,rnd_list,list_of_coords,radius_difference,fresh,copied_circles):
    Circle = namedtuple('Circle', 'x y r w')
    x1,y1,r,w=fresh
    getcontext().prec = 30 #точность вычислений 28 значащих цифр
    if rnd_num in rnd_list:
            random.shuffle(list_of_coords)
            for  each in list_of_coords:
                new_circle_r= each[0]
                if r>new_circle_r*Decimal(radius_difference):
                    rnd_x=random.choice([-Decimal(r),Decimal(r)])
                    rnd_y=random.choice([-Decimal(r),Decimal(r)])
                    new_fresh=Circle(x1+rnd_x, y1+rnd_y, new_circle_r, w)
                    new_flag=False
                    fail_flag = False  
                    if not fail_flag and not new_flag:
                        copied_circles.append(new_fresh)
                        break


#генерируем список окружностей вида 'x y r w'
def make_circles(cf,list_of_coords,radius_difference):
    getcontext().prec = 30 #точность вычислений 28 значащих цифр
    Circle = namedtuple('Circle', 'x y r w')
    N_circles = np.random.randint(cf.N_circles_min, cf.N_circles_max)  # сколько сделать окружностей
    circles = []
    copied_circles=[]
    for i in range(N_circles):

        rnd_num=random.randint(1,20)#(cf.N_circles_min+cf.N_circles_min)//90)

        # случайные параметры для новой окружности
        x1, y1 = np.random.randint([0, 0], [cf.size_x, cf.size_y])
        cirle=random.choice(list_of_coords)
        r=cirle[0]
        w = 1 # ширина линии обводки
        fresh = Circle(x1, y1, r, w)
        new_flag=False
        fail_flag = False  # флаг что точка фатально не удалась

        # проверяем радиус на предмет возможных пересечений с существующими окружностями
        for oldy in circles:
            dist = np.linalg.norm([(fresh.x - oldy.x), (fresh.y - oldy.y)])
                
            if dist < (fresh.r + oldy.r):  # если R слишком велико - скипаем
                new_flag=True

            fail_flag = (dist == 0)

        # добавим новую окружность в общий список (если она уживается с остальными)
        if not fail_flag and not new_flag:
            circles.append(fresh)

        #делаем слипшиеся капли
        make_neighbourhood_circles(rnd_num,rnd_list,list_of_coords,radius_difference,fresh,copied_circles)
                   
    return (circles+copied_circles)


#поворачиваем отдельный пиксель капельки на угол и преобразуем его координаты
def rotate_point(point, angle,centr): 

    # Преобразуем угол в радианы
    theta = np.radians(angle)

    getcontext().prec = 30 #точность вычислений 28 значащих цифр

    # Смещение точки относительно центра
    translated_x = (Decimal(point[0]))  - Decimal(centr[0])
    translated_y = (Decimal(point[1])) - Decimal(centr[1])
    
    # Матрица вращения
    rotation_matrix = np.array([[Decimal(np.cos(theta)), -Decimal(np.sin(theta))],
                                 [Decimal(np.sin(theta)),  Decimal(np.cos(theta))]])
    
    # Применяем матрицу к точке
    rotated_translated_point = rotation_matrix @ np.array([translated_x, translated_y])
    
    # Возвращаем точку к оригинальному положению
    rotated_point = (Decimal(rotated_translated_point[0] +  Decimal(centr[0]) ), Decimal(rotated_translated_point[1] +  Decimal(centr[1])))
    
    return rotated_point


#вставляем картинку капли на фон
def paste_image(cir,list_of_masks,image_folder,data,background,result_list_of_masks,result_count): 
        


        # берем инфу о капле
        radius=cir[2]
        img_data = data[radius] 
        img_name=img_data[0]
        mask_image=list_of_masks[image_folder+img_name[1:]]#маска картинки
        new_mask_image=[]
        img = cv2.imread(os.path.join(image_folder, img_name),cv2.IMREAD_UNCHANGED)


        # поворот капли
        rotateAngleSmallPicture=random.randrange(0,360,1) # угол поворота картинки капельки отдельно
        rotation_matrix = cv2.getRotationMatrix2D((img_data[1],img_data[2]), -rotateAngleSmallPicture, 1.0)
        new_img = cv2.warpAffine(img, rotation_matrix, (100, 100))
        cv2.imwrite(image_folder+'/rotated_images/rotated_image.png', new_img)
        rotate=Image.open(os.path.join(image_folder,'./rotated_images/rotated_image.png'))


        #сохраняем координаты новой маски повернутой капли и #сохраняем маску в формат
        list=["0 "]
        point=(int(cir[0]),int(cir[1]))
        for x in range(0,len(mask_image)):
            rotated_point=rotate_point(mask_image[x],rotateAngleSmallPicture,(img_data[1],img_data[2]))
            new_mask_image.append((int(point[0]+rotated_point[0]),int(point[1]+rotated_point[1])))
            list.append(str((point[0]+rotated_point[0]-640)/1280))
            list.append(str((point[1]+rotated_point[1]-80)/1280))
        result_str=" ".join(list)


        # считаем влезает ли капля в обьектив     
        mask_contur_polygon=Polygon(contur_mask_coords)
        mask_image_polygon2 = Polygon(new_mask_image)    
        intersection = mask_image_polygon2.intersection(mask_contur_polygon)    
        intersection_percentage = (intersection.area / mask_image_polygon2.area) * 100
        flag_to_paste=False
        if (intersection_percentage>75):
            flag_to_paste=True
            #вставляем если прошло проверки все     
            background.paste(rotate,point,rotate) #вставляем на фон каплю   
            result_list_of_masks.append(result_str) 
            result_count+=1   

              
        return (img_name,point,radius,flag_to_paste)


#накладываем фильтр на итоговую картинку
def color_image(background,hsv_const):

    #конвертируем в hsv формат
    img_hsv = background.convert('HSV')

    # Преобразуем изображение в массив NumPy
    np_img = np.array(img_hsv)

    # Увеличим или уменьшим значение канала оттенка (H)
    # например, изменим на +50 единиц
    np_img[..., 0] = (np_img[..., 0].astype(int) + hsv_const) % 256

    # Преобразуем массив обратно в изображение
    img_hsv_modified = Image.fromarray(np_img.astype('uint8'), 'HSV')

    # Конвертируем обратно в RGB
    img_rgb = img_hsv_modified.convert('RGB')

    return img_rgb


#вставляем обьектив и линейку на фон .png
def paste_mask(img_rgb):
    lineyka_rotate_angle=random.randint(0,360)
    lineyka_rotate=lineyka.rotate(lineyka_rotate_angle,expand=False,resample=Image.BICUBIC)
    img_rgb.paste(krug,krug)
    img_rgb.paste(lineyka_rotate,lineyka_rotate)


# режем картинку итоговую и сохраняем
def cropp_save_res_img(img_rgb,file_name):

    #кортеж прямоугольника: (меньший-x,меньший-y,больший-x,больший-y) 
    img_rgb = img_rgb.crop(cropp_tuple)

    img_rgb.save(cf.path_to_cirled_image_with_mask + file_name , format="PNG")


#сохраняем список масок в файл .txt
def save_coords(file_name,result_list_of_masks): 
    with open(cf.path_to_mask+f'{file_name[0:len(file_name)-4]}.txt', 'w') as file:
        for i in result_list_of_masks:
            print(i, file=file, sep="\n")


#получаем итоговую размеченную(сохраняем маски капель) картинку с каплями
def make_image_circles(circles, file_name,data,list_of_masks,rand_background_color=0):

    hsv_const=random.randint(-8,4)  # -8,4 это отенки оранжевого    фильтр на фон 

    background=Image.new('RGB', (2560, 1440), dict_rgb_circles_path[rand_background_color][0]) #цвет фона

    image_folder=dict_rgb_circles_path[rand_background_color][1] #путь до папки с каплями

    result_count=0 #счетчик

    result_list_of_masks=[] #список масок

    for cir in circles: #вставляем капли
        paste_image(cir,list_of_masks,image_folder,data,background,result_list_of_masks,result_count)

    save_coords(file_name,result_list_of_masks) # сохраняем в файл маски капель

    img_rgb = color_image(background,hsv_const) # красим фотку

    paste_mask(img_rgb) #пастим маску круга и линейки

    cropp_save_res_img(img_rgb,file_name) #режем и сохраняем

    print("got it") #вывод в терминал


#генерируем нужное кол-во картинок
def main(cf):  
    for num_image in range(cf.N_images):
        rand_background_color=random.randint(0,2)
        if rand_background_color==1:
            circles = make_circles(cf,rand_background_color,result_list_of_coords_orange,2)
            make_image_circles(cf, circles, f"circles_{num_image:04}.png",rand_background_color,orange_data,roc.orange,num_image,
                               )
        else:
            circles = make_circles(cf,rand_background_color,result_list_of_coords_grey,3)
            make_image_circles(cf, circles, f"circles_{num_image:04}.png",rand_background_color,grey_data,roc.grey,num_image)

#генерируем нужное кол-во картинок оранжевых отдельно
def generate_orange(cf):
    for num_image in range(cf.N_images):
        circles = make_circles(cf,result_list_of_coords_orange,2)
        make_image_circles(circles, f"circles_{num_image:04}.png",orange_data,roc.orange,rand_background_color=1)

#генерируем нужное кол-во картинок серых отдельно
def generate_grey(cf):
    for num_image in range(cf.N_images):
        circles = make_circles(cf,result_list_of_coords_grey,2)
        make_image_circles(circles, f"circles_{num_image:04}.png",grey_data,roc.grey)

help()    
generate_grey(cf)