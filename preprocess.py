# -*- coding: utf-8 -*-
"""
Created on Sat Oct 13 13:33:29 2018

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：离散元后处理

INPUT：地层建模（图像）

OUTPUT：模型颗粒信息[x y r]文件和灰度比色卡文件

"""

import numpy as np
import matplotlib.pyplot as plt
import module_pre_post as whj
import object_pre_post as o

path=r'C:\Users\whj\Desktop\Spyder\例\拉张.bmp'

#导入图片，生成rgb数组
img_rgb=whj.LoadImage(path)

#生成键值对？
rgb_dict=whj.InitDict(img_rgb)

color=['gray','red','orange','blue']

tag=[-2,-1,1,2]

color_dict=dict(zip(tag,color))

win=plt.gca()

#转化成tag？
img_tag=whj.RGB2Tag(img_rgb,rgb_dict)

Particle=whj.Img2Particle(img_tag,color_dict,5)

#还要进行适当地放缩
model_height=np.shape(img_tag)[0]/3
model_width=np.shape(img_tag)[1]/3

yade_height=30
yade_width=100

rate_height=yade_height/model_height
rate_width=yade_width/model_width

#取较小的
rate=min(rate_height,rate_width)

#将计算结果写入result.txt文件
with open("./result.txt",'w') as file:
    
    for this_particle in Particle:
        
        file.write(str(0))
        file.write(' ')
        
        file.write(str(this_particle.position[0]*rate))
        file.write(' ')
        
        file.write(str(this_particle.position[1]*rate))
        file.write(' ')
        
        file.write(str(this_particle.radius*rate))
        
        file.write('\n')
     
        
        