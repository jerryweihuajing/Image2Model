# -*- coding: utf-8 -*-
"""
Created on Tue Oct 16 19:50:03 2018

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：离散元前后处理函数库
"""

import numpy as np
import matplotlib.pyplot as plt
import object_pre_post as o

#============================================================================== 
#输入路径path，读取图片，生成图片的rgb和灰度矩阵函数
#参数show表示图片预览参数：默认为None，rgb表示开启rgb预览，gray表示灰度预览
def LoadImage(load_path,show=False):
    
    img_rgb=plt.imread(load_path) 
    
    if show: 
        
        #显示rgb图像
        plt.figure()
        plt.imshow(img_rgb) 
#        plt.axis('off')
        
    return img_rgb

#生成字典的初始化函数
def InitDict(img_rgb):
    
    rgb_list=[]
    
    for i in range(np.shape(img_rgb)[0]):
        
        for j in range(np.shape(img_rgb)[1]):
            
            if list(img_rgb[i,j].astype(int)) not in rgb_list:
                
                rgb_list.append(list(img_rgb[i,j].astype(int)))
                
    rgb_list.remove([255,255,255])    
         
    #各种颜色像素点数量的字典
    rgb_number_dict={}
    
    for k in range(len(rgb_list)):
        
        rgb_number_dict[k]=np.sum(img_rgb==rgb_list[k])
        
    #比较像素点数量的多少    
    key=list(rgb_number_dict.keys())
    value=list(rgb_number_dict.values())
    
    #得到断层的rgb值
    fault_rgb=rgb_list[key[value.index(min(value))]]
    
    #只有layer的rgb
    import copy
    
    layer_rgb_list=copy.deepcopy(rgb_list)
    
    #删除fault的rgb
    layer_rgb_list.remove(fault_rgb)
    
    #生成rgb_dict,包括layer和fault
    rgb_dict={}
    
    for i in range(len(layer_rgb_list)):
        
        rgb_dict[i+1]=layer_rgb_list[i]
        
    #索引-1代表断层fault
    rgb_dict[-1]=fault_rgb
    
    #0代表背景色
    rgb_dict[0]=[255,255,255]
    
    #转化为img_tag
    img_tag=RGB2Tag(img_rgb,rgb_dict)
    
    #基底tag
    base_tag=GetBaseTag(img_tag)
    
    #基底egb
    base_rgb=rgb_dict[base_tag]
    
    #删除并重命名
    del rgb_dict[base_tag]
    
    #base_tag的索引定义为-2
    rgb_dict[-2]=base_rgb
    
    return rgb_dict

#============================================================================== 
#字典按value搜索key
def DictKeyOfValue(dictionary,value):
    
    keys=list(dictionary.keys())
    values=list(dictionary.values())
    
    #要查询的值为value
    key=keys[values.index(value)]
    
    return key

#============================================================================== 
#由img_rgb生成img_tag
def RGB2Tag(img_rgb,rgb_dict,show=False):
    
    img_tag=np.zeros((np.shape(img_rgb)[0],np.shape(img_rgb)[1]))
    
    #给img_tag矩阵赋值
    for i in range(np.shape(img_tag)[0]):
        
        for j in range(np.shape(img_tag)[1]):
            
            img_tag[i,j]=DictKeyOfValue(rgb_dict,list(img_rgb[i,j].astype(int)))
    
    #显示
    if show:
        plt.figure()
        plt.imshow(img_tag,cmap='gray')
         
    return img_tag

#由img_tag生成img_rgb
def Tag2RGB(img_tag,rgb_dict,show=False):
    
    img_rgb=np.zeros((np.shape(img_tag)[0],np.shape(img_tag)[1],3))

    #给img_rgb矩阵赋值
    for i in range(np.shape(img_rgb)[0]):
        
        for j in range(np.shape(img_rgb)[1]):
            
#            print(img_tag[i,j])
#            print(rgb_dict[int(img_tag[i,j])])

            #注意dtype，必须是uint8才能正常显示RGB
            img_rgb[i,j]=np.array(rgb_dict[img_tag[i,j]])
    
    #转化为正确输出格式      
    img_rgb=np.array(img_rgb,dtype=np.uint8)  
      
    #显示
    if show:
        plt.figure()
        plt.imshow(img_rgb)
        
    return img_rgb

#计算出基底base tag的函数 设计一个
#计算base_tag的方法
def GetBaseTag(img_tag):
    
    """从图像末尾进行扫描，获取到的非背景色的tag或rgb就是"""
    for i in range(np.shape(img_tag)[0]-1,0,-1):
        
        #只要不是全空白那就一定是它咯
        if list(img_tag[i])!=list(img_tag[-1]):  
            
            break
    
    #取中间值
    return img_tag[i,int(np.shape(img_tag)[1]/2)]

#============================================================================== 
#将字典转化为频率统计字典   
def List2FrequencyDict(which_list):
    
    #建立集合列表
    element_list=list(set(which_list))
    
    #初始化频率列表
    frequency_list=[]
    
    #统计频率
    for this_element in element_list:
        
        that_frequency=0
        
        for element in which_list:
            
            if this_element==element:
                
                that_frequency+=1
        
        #将所有频数组合成列表
        frequency_list.append(that_frequency)
    
    #返回一个出现元素及其对应频率的列表
    return dict(zip(element_list,frequency_list))
             
#定义一个列表中某值出现的函数
def CalculateFrequency(which_list,which_value):
    
    if which_value not in which_list:
        
        print('ERROR:the value not in this list')
        
        return
    
    if which_value in which_list:
        
        map_element_frequency=List2FrequencyDict(which_list)
    
        return map_element_frequency[which_value]
    
#计算出列表中出现频率最高的元素的函数
def MostFrequentElement(which_list):
    
    #频率统计字典
    map_element_frequency=List2FrequencyDict(which_list)
    
    #最大频率
    the_frequency=max(list(map_element_frequency.values()))
    
    return DictKeyOfValue(List2FrequencyDict(which_list),the_frequency)
    
#计算出列表中出现频率最低的元素的函数
def LeastFrequentElement(which_list):
    
    #频率统计字典
    map_element_frequency=List2FrequencyDict(which_list)
    
    #最小频率
    the_frequency=min(list(map_element_frequency.values()))
    
    return DictKeyOfValue(List2FrequencyDict(which_list),the_frequency)  
    
#============================================================================== 
#把img_tag转化成Particle集合
def Img2Particle(img_tag,color_dict,size_of_window):
    
    #生成颗粒方法：确定一个大小位nXn的window，每个window生成一个颗粒
    #颜色取决于像素点最多的那种颜色
    
    #定义新的矩阵
    new_img_tag=np.zeros((int(np.floor(np.shape(img_tag)[0]/size_of_window)),
                         int(np.floor(np.shape(img_tag)[1]/size_of_window))))
    
    #新的窗口
    win=plt.gca()
    
    #颗粒列表
    Particle=[]
    
    #取窗口的中点哦
    #窗口的值位窗口中像素点较多的那个tag
    for i in range(np.shape(new_img_tag)[0]):
        
        for j in range(np.shape(new_img_tag)[1]):
            
            neighbor=[]
            
            #领域核
            neighbordict=[(p,q) for p in list(range(size_of_window)) for q in list(range(size_of_window))]
            
            #计算邻域中某种tag最多
            for item in neighbordict:
                
                #新索引
                new_i,new_j=size_of_window*i+item[0],size_of_window*j+item[1]
                
                #增加进来
                neighbor.append(img_tag[new_i,new_j])
                
            new_img_tag[i,j]=MostFrequentElement(neighbor)
         
            #如果位0，就别玩了继续
            if new_img_tag[i,j]:
                
                #定义新的particle
                new_particle=o.particle()
                
                new_particle.id=[i,j]
                
                new_particle.radius=(size_of_window)/2
                
                new_particle.position=np.array([size_of_window*j+new_particle.radius,
                                                np.shape(img_tag)[0]-(size_of_window*i+new_particle.radius)])
                
                new_particle.color=color_dict[new_img_tag[i,j]]
                
                new_particle.DrawAt(win)
                
                Particle.append(new_particle)
    
    #定义新盒子
    new_box=o.box()
    
    new_box.left_right=[0,size_of_window*np.shape(new_img_tag)[1]]
    new_box.bottom_top=[0,size_of_window*np.shape(new_img_tag)[0]]   
    
    new_box.Init()
    
    new_box.DrawAt(win)
    
    plt.axis([min(new_box.left_right)-size_of_window,
              max(new_box.left_right)+size_of_window,
              min(new_box.bottom_top)-size_of_window,
              max(new_box.bottom_top)+size_of_window])
    
    return Particle

