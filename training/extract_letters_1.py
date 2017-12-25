# -*- coding: UTF-8 -*-

import os
from PIL import Image, ImageOps
import numpy as np
# from helper import random_name
from helper import filter_img, random_name, cut_image
import cv2

IMAGE_FOLDER = os.path.join("data", "labeled", "1", "test")
OUTPUT_FOLDER = os.path.join("single_letters", "1", "test")
IMAGE_SIZE = 50
MODEL_INPUT_SIZE = (28, 28)

def main():
    for i in range(10):
        dir_path = os.path.join(OUTPUT_FOLDER, str(i))
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    for img_file in os.listdir(IMAGE_FOLDER):
        if img_file.endswith('.jpg'):
            # print(img_file)
            im = Image.open(os.path.join(IMAGE_FOLDER, img_file))
            im = im.convert('L')

            step = "filter_img_"
            imgry = filter_img(im, get_number_color(im))
            # imgry = filter_img(im, 230)
            # imgry.save(os.path.join(OUTPUT_FOLDER, step + img_file), 'jpeg')
            imgs = cut_image(imgry)
            # for img in imgs:
            #     img.save(os.path.join(OUTPUT_FOLDER, random_name()))
            if len(imgs) != 4:
                print("cut image warning: {}".format(img_file))
                continue

            for i in range(4):
                # temp_img = resize_image(imgs[i])
                imgs[i].resize(MODEL_INPUT_SIZE).save(os.path.join(OUTPUT_FOLDER, img_file[i], random_name()))

# def filter_img(img, equal_threshold=False, threshold=170):
#     '对于黑白图像，将像素值大于某一个值的部分变成白色，小于这个值的部分变成黑色'
#     filtered = Image.new(img.mode, img.size)
#     for x in range(0, img.size[0]):
#         for y in range(0, img.size[1]):
#             if equal_threshold and img.getpixel((x, y)) == threshold:
#                 filtered.putpixel((x, y), 255)
#             elif (equal_threshold == False) and img.getpixel((x, y)) > threshold:
#                 filtered.putpixel((x, y), 255)
#             else:
#                 filtered.putpixel((x, y), 0)
#     return filtered

def get_number_color(img):
    colors = img.getcolors()
    # 数字的颜色像素点最多，所以按照像素点数量从大到小排序
    # 结果的第一个是数字像素点的个数以及对应的颜色
    # 排序结果类似于[(1331, 99), (653, 233), (631, 232), (626, 240)]
    return sorted(colors, key=lambda x: x[0], reverse=True)[1][1]

# def cut_image(imgry):
#     """
#     把图片切割成数字，图片必须是二值化之后的结果（像素值只有0或者255）
#     返回切割后的四张图片
#     """
#     results = []

#     img_copy = imgry.crop((1, 0, imgry.width-1, imgry.height))
#     masks = []
#     for x in range(img_copy.width):
#         for y in range(img_copy.height):
#             if img_copy.getpixel((x, y)) == 0:
#                 img_copy, mask = get_mask(img_copy, x, y)
#                 # 去除周围的空白，去除分割异常的情况
#                 mask = remove_blank(mask)
#                 if mask is not None:
#                     masks.extend(mask)
#     return masks

# from PIL.ImageDraw import Draw
# IMAGE_PADDING = 2
# def cut_image(imgry):
#     open_cv_image = np.array(imgry)
#     image, contours, hierarchy = cv2.findContours(open_cv_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
#     cnts = sorted([(c, cv2.boundingRect(c)[0]) for c in contours], key = lambda x:x[1])

#     images = []
#     lh = 0
#     rh = 0

#     # draw = Draw(imgry)
#     for (c,_) in cnts:
#         (x, y, w, h) = cv2.boundingRect(c)
#         # print(x, y, w, h)
#         if 10 < h < 70:
#             # 排除0这类的数字可能会捕捉到两个边界的情况
#             if x > lh and x + w < rh:
#                 continue
#             # draw.rectangle((x, y, x + w, y + h))
#             lh = x
#             rh = x + w
#             temp = imgry.crop((x-IMAGE_PADDING, y-IMAGE_PADDING, x + w + IMAGE_PADDING, y + h + IMAGE_PADDING))
#             temp = temp.resize((IMAGE_SIZE, IMAGE_SIZE))
#             temp = ImageOps.invert(temp)
#             # temp.show()
#             images.append(temp)
#     # print(len(ary))
#     return images

def resize_image(image):
    """
    把图片变成指定大小，不缩放图片
    将之前的图片直接贴在这个新图片上面
    """
    result = Image.new(image.mode, (IMAGE_SIZE, IMAGE_SIZE), color=255)
    padding_left = (IMAGE_SIZE - image.width) // 2
    padding_top = (IMAGE_SIZE - image.height) // 2
    result.paste(image, (padding_left, padding_top))
    return result

def remove_blank(image):
    img_arr = np.array(image)
    # 黑色点的位置
    dot_lists = np.argwhere(img_arr == 0)
    top = dot_lists[:, 0].min()
    bottom = dot_lists[:, 0].max()
    left = dot_lists[:, 1].min()
    right = dot_lists[:, 1].max()
    # 排除有噪点的情况，有些处理完之后会有一条黑线或者一个黑色的像素点
    # 1的宽度是15，所以设置为10应该没问题
    width = right - left
    height = bottom - top
    if width < 10 or height < 10:
        return None
    # 这种情况应该是两个数字连在一起了，从中间切开
    # TODO: 也有可能是三个数字连在一起了，这边暂时直接去掉，后面保存图片的时候会考虑 
    if width > height:
        return [image.crop((left, top, left + width // 2, bottom)), image.crop((left + width // 2, top, right, bottom))]
    return [image.crop((left, top, right, bottom))]

def get_mask(img, x, y):
    """
    找出img上与x, y相连的所有点的坐标
    并把原始图片对应处变为空白
    """
    mask = Image.new(img.mode, img.size, color=255)
    pix_img = img.load()
    pix_mask = mask.load()
    positions = get_mask_positions(img, x, y)
    for position in positions:
        i = position[0]
        j = position[1]
        pix_img[i, j] = 255
        pix_mask[i, j] = 0
    return img, mask

def get_mask_positions(img, x, y):
    positions = [(x, y)]
    # 这边算法没有完全优化，在图片比较大的情况下这个分割方式会有问题
    # TODO: 目前发现了一个图片有这个问题，暂时不处理 
    for _ in range(20):
        for i in range(x, img.width):
            for j in range(img.height):
                if (img.getpixel((i, j)) == 0 and
                (i, j) not in positions and 
                adjacent_to(positions, i, j)):
                    positions.append((i, j))
    return positions

# def get_mask_positions(img, x, y):
#     """
#     依次找这个点右边，右上和下边的三个点，如果是黑色，则递归下去
#     """
#     points = [
#         (x+1, y-1),
#         (x+1, y),
#         # (x+1, y+1),
#         (x, y+1)
#     ]
#     positions = []
#     for point in points:
#         if img.getpixel(point) == 0:
#             positions.append(point)
#             positions.extend(
#                 get_mask_positions(img, point[0], point[1]))
#     return positions

def adjacent_to(positions, x, y):
    adjacent_points = [
        (x-1, y-1),
        (x-1, y),
        (x-1, y+1),
        (x, y-1),
        (x, y+1),
        (x+1, y-1),
        (x+1, y),
        (x+1, y+1)
    ]
    for point in adjacent_points:
        if point in positions:
            return True
    return False

if __name__ == "__main__":
    main()
