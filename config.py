import os
import config

# параметры окружности
R_min =  0
R_max = 75
w_min = 1 # мин.ширина обводки
k_w_max = 0.2  # макс. ширина обводки k_w_max * R

# параметры изображения
size_x = 2560
size_y = 1440
N_circles_min = 2520  # мин. число окружностей-капель на картинку
N_circles_max = 2521  # макс. число окружностей-капель на картинку

# параметры датасета
# пути сохраения входных и целевых изображений
path_to_cirled_image = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + 'targets' + os.path.sep
path_to_target_image = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + 'targets' + os.path.sep
path_to_cirled_image_with_mask=os.path.dirname(os.path.abspath(__file__)) + os.path.sep + 'targets_with_mask' + os.path.sep
path_to_mask=os.path.dirname(os.path.abspath(__file__)) + os.path.sep + 'result_masks' + os.path.sep
N_images = 10 # общее количество изображений в датасете