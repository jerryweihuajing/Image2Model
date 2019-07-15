# -*- coding: utf-8 -*-
"""
Created on Fri Dec 21 14:53:09 2018

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：Image2Model Based on YADE script

%INPUT  a particle file, format [x y z r]
        a 2D model image, format [np.array]
        
%OUTPUT a particle file, format [x y z r color]
"""

import module as whj

#模型图片
model_image=r'C:\Users\whj\Desktop\Spyder\例\for YADE.bmp'
#model_image=r'C:\Users\whj\Desktop\Spyder\例\YADE_1.bmp'
#model_image=r'C:\Users\whj\Desktop\Spyder\例\YADE_2.bmp'

#导入图片
img_rgb=whj.LoadImage(model_image,True) 

#生成rgb查询字典
rgb_dict=whj.InitDict(img_rgb,True,True)

#生成标签矩阵
img_tag=whj.RGB2Tag(img_rgb,rgb_dict)

#打开颗粒文件并导入数据
particle_data,file_head=whj.ImportFile('sample.txt')

#建立模型
new_data=whj.GnerateModel(img_tag,rgb_dict,particle_data,True)

#导出结果
whj.ExportFile(file_head,new_data,'result.txt')
