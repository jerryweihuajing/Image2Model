# -*- coding: utf-8 -*-
"""
Created on Wed Dec 19 10:08:14 2018

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：Image2Model Based on YADE module
"""

import os
import random
import copy as cp
import numpy as np
import matplotlib.pyplot as plt

import get_color_map as Color

#============================================================================== 
#输入路径path，读取图片，生成图片的rgb和灰度矩阵函数
#参数show表示图片预览参数：默认为None，rgb表示开启rgb预览，gray表示灰度预览
def LoadImage(load_path,show=False):
    
    img_rgb=plt.imread(load_path) 
    
    if show: 
        
        #显示rgb图像
        fig=plt.figure()
        plt.imshow(img_rgb) 
#        plt.axis('off')
        
        #修改图名并保存
        fig.savefig('model.png',dpi=300,bbox_inches='tight')
        
    return img_rgb

#============================================================================== 
#灰度级插值
"""近邻插值法：可能引起失真"""
def ResizeGrayNearby(img_gray,size):
    
    new_img_gray=np.zeros(size)
    
    for i in range(np.shape(new_img_gray)[0]):
        
        for j in range(np.shape(new_img_gray)[1]):
            
            #新的坐标索引
            new_i=int(np.round(i*np.shape(img_gray)[0]/np.shape(new_img_gray)[0]))
            new_j=int(np.round(j*np.shape(img_gray)[1]/np.shape(new_img_gray)[1]))
            
            new_img_gray[i,j]=img_gray[new_i,new_j]
            
    return new_img_gray

#============================================================================== 
#灰度级插值
"""双线性插值：计算比较繁琐"""
def ResizeGrayInterpolation(img_gray,size):  
    
    #新的灰度矩阵
    new_img_gray=np.full(size,0.0)
    
    for i in range(size[0]):
        
        for j in range(size[1]):
            
            #new_img_gray[i,j]的值需要用img_gray[new_i,new_j]的上下整经线性插值得到
            #网格由new_i,new_j对应的floor和ceil组成
            #new_i,new_j都是浮点数,新的坐标在原矩阵中的索引
            new_i=i*np.shape(img_gray)[0]/np.shape(new_img_gray)[0]
            new_j=j*np.shape(img_gray)[1]/np.shape(new_img_gray)[1]
    
            """不使用ceil是因为在网格点上floor和ceil的值相等，无法区分啊哥"""
            #拆行符‘\’
            #特殊点作处理，四个端点
            
            #[-1,-1]
            if i==np.shape(new_img_gray)[0]-1 and j==np.shape(new_img_gray)[1]-1:
                
                new_img_gray[i,j]=img_gray[-1,-1].astype(float)
                
                continue
            
            #[0,-1]
            if i==0 and j==np.shape(new_img_gray)[1]-1:
                
                new_img_gray[i,j]=img_gray[0,-1].astype(float)
                
                continue
            
            #[-1,0]
            if i==np.shape(new_img_gray)[0]-1 and j==0:
                
                new_img_gray[i,j]=img_gray[-1,0].astype(float)
                
                continue
            
            #[0,0]
            if i==0 and j==0:
                
                new_img_gray[i,j]=img_gray[0,0].astype(float)
                
                continue
            
            #特殊行作处理:四行
            #第一行和最后一行
            if (i==0 or i==np.shape(new_img_gray)[0]-1)\
            and (j!=0 or j!=np.shape(new_img_gray)[1]-1):
                
                k=img_gray[int(np.floor(new_i)),int(np.floor(new_j)+1)].astype(float)\
                 -img_gray[int(np.floor(new_i)),int(np.floor(new_j))].astype(float)
                new_img_gray[i,j]=k*(new_j-np.floor(new_j))\
                +img_gray[int(np.floor(new_i)),int(np.floor(new_j))].astype(float)
                
                continue
            
            #第一列和最后一列
            if (j==0 or j==np.shape(new_img_gray)[1]-1)\
            and (i!=0 or i!=np.shape(new_img_gray)[1]-1):
                
                k=img_gray[int(np.floor(new_i)+1),int(np.floor(new_j))].astype(float)\
                 -img_gray[int(np.floor(new_i)),int(np.floor(new_j))].astype(float)
                new_img_gray[i,j]=k*(new_i-np.floor(new_i))\
                +img_gray[int(np.floor(new_i)),int(np.floor(new_j))].astype(float)
                
                continue
            
            #先作单线性插值，建立网格ABCD
            #AB为右
            A=img_gray[int(np.floor(new_i)),int(np.floor(new_j))].astype(float)
            B=img_gray[int(np.floor(new_i)+1),int(np.floor(new_j))].astype(float)  
           
            #CD为左
            C=img_gray[int(np.floor(new_i)),int(np.floor(new_j)+1)].astype(float)
            D=img_gray[int(np.floor(new_i)+1),int(np.floor(new_j)+1)].astype(float)       
            
            #左值AB
            kAB=(B-A)
            AB=(new_j-np.floor(new_j))*kAB+A   
            
            #右值CD
            kCD=(D-C)
            CD=(new_j-np.floor(new_j))*kCD+C   
            
            #AB和CD进行内插，双线性插值
            k=(CD-AB)
            new_img_gray[i,j]=(new_i-np.floor(new_i))*k+AB
                       
    return new_img_gray

#============================================================================== 
#RGB插值
"""近邻插值改变图像大小"""
def ResizeRGBNearby(img_rgb,size):
    
    img_r,img_g,img_b=img_rgb[:,:,0],img_rgb[:,:,1],img_rgb[:,:,2]
    
    #新的rgb矩阵
    new_img_rgb=np.full((size[0],size[1],3),(0.0,0.0,0.0))
    
    for i in range(size[0]):
       
        for j in range(size[1]):
            
            #新的坐标索引
            new_i=int(np.round(i*np.shape(img_rgb)[0]/np.shape(new_img_rgb)[0]))
            new_j=int(np.round(j*np.shape(img_rgb)[1]/np.shape(new_img_rgb)[0]))
           
            #RGB三个通道的新值
            new_img_rgb[i,j,:]=(img_r[new_i,new_j],img_g[new_i,new_j],img_b[new_i,new_j])
    
    #改变矩阵类型
    new_img_rgb=new_img_rgb.astype(img_rgb.dtype)

    return new_img_rgb

#============================================================================== 
#RGB插值
"""双线性插值改变图像大小"""
def ResizeRGBInterpolation(img_rgb,size):
    
    img_r,img_g,img_b=img_rgb[:,:,0],img_rgb[:,:,1],img_rgb[:,:,2]
    
    #新的rgb矩阵
    new_img_rgb=np.full((size[0],size[1],3),(0.0,0.0,0.0))
    
    #处理后的三通道矩阵
    new_img_r=ResizeGrayInterpolation(img_r,size)
    new_img_g=ResizeGrayInterpolation(img_g,size)
    new_img_b=ResizeGrayInterpolation(img_b,size)
    
    for i in range(size[0]):
        
        for j in range(size[1]):
            
            new_img_rgb[i,j,:]=(new_img_r[i,j],new_img_g[i,j],new_img_b[i,j])
    
    #改变矩阵类型
    new_img_rgb=new_img_rgb.astype(img_rgb.dtype)
    
    return new_img_rgb

#============================================================================== 
#生成字典的初始化函数
#base_adjust表示是否需要用特殊符号来表示base的rgb值
#fault_exit表示输入图像当中是否存在断层对象
def InitDict(img_rgb,
             base_adjust=False,
             fault_exist=False):
    
    #临时变量
    rgb_list_temp=[]
    
    for i in range(np.shape(img_rgb)[0]):
        
        for j in range(np.shape(img_rgb)[1]):
            
            if list(img_rgb[i,j].astype(int)) not in rgb_list_temp:
                
                rgb_list_temp.append(list(img_rgb[i,j].astype(int)))
    
    #判断背景色
    if [255,255,255] in rgb_list_temp:
   
        rgb_list_temp.remove([255,255,255])    
    
    #只有layer的rgb
    layer_rgb_list=cp.deepcopy(rgb_list_temp)
    
#    print(layer_rgb_list)
        
    #fault
    #有断层的情况哦
    if fault_exist:
        
        #各种颜色像素点数量的字典
        rgb_number_dict={}
        
        for k in range(len(rgb_list_temp)):
            
            rgb_number_dict[k]=np.sum(img_rgb==rgb_list_temp[k])
            
        #比较像素点数量的多少    
        key=list(rgb_number_dict.keys())
        value=list(rgb_number_dict.values())
        
        #得到断层的rgb值
        fault_rgb=rgb_list_temp[key[value.index(min(value))]]
    
#        print(fault_rgb)
        
        #删除fault的rgb
        layer_rgb_list.remove(fault_rgb)
        
#        print(layer_rgb_list)
        
        #生成rgb_dict,包括layer和fault
        rgb_dict={}
        
        for i in range(len(layer_rgb_list)):
            
            rgb_dict[i+1]=layer_rgb_list[i]
                    
#    print(layer_rgb_list)
    
    #但是列表不可以作为索引，因此先转化为临时tag列表
    tag_list=[index+1 for index in range(len(layer_rgb_list))]
    
    #临时的tag_color索引
    rgb_dict_temp=dict(zip(tag_list,layer_rgb_list))
    
#    print(rgb_dict_temp)
    
    #比较他们的深度度
    depth_list=[]
    
    for this_rgb in list(rgb_dict_temp.values()):
          
#        print(np.mean(list(np.where(img_rgb==list(this_rgb))[0])))

        depth_list.append(np.mean(list(np.where(img_rgb==list(this_rgb))[0])))
        
#    建立颜色何深度的索引
    map_tag_depth_temp=dict(zip(tag_list,depth_list))
    
#    print(map_tag_depth_temp)
    
    #对depth进行排序
    depth_list.sort()
    
#    print(depth_list)
    
    #老的tag要修改
    tag_list_temp=[]
    
    #索引每一个深度值
    for this_depth in depth_list:
        
        tag_list_temp.append(DictKeyOfValue(map_tag_depth_temp,this_depth))
        
#    print(depth_list)
#    print(tag_list_temp)
    
    #再按照它找rgb
    rgb_list=[]
    
    for this_tag in tag_list_temp:
        
        rgb_list.append(rgb_dict_temp[this_tag])
        
    #最终结果
    rgb_dict=dict(zip(tag_list,rgb_list))

    if fault_exist:
        
        #索引-1代表断层fault
        rgb_dict[-1]=fault_rgb
    
    #重新排序
    rgb_dict=DictSortByIndex(rgb_dict,sorted(list(rgb_dict.keys())))
    
    #base
    #调整基底哦babe
    if base_adjust:
        
        base_tag=list(rgb_dict.keys())[-1]
        
#        print(base_tag)
        
        base_rgb=rgb_dict[base_tag]
        
        #删除并重命名
        del rgb_dict[base_tag]
        
        #base_tag的索引定义为-2
        rgb_dict[-2]=base_rgb
    
    #blank
    if np.array([255,255,255]) in img_rgb:
        
        #0代表背景色
        rgb_dict[0]=[255,255,255]
    
    #排序
    rgb_dict=DictSortByIndex(rgb_dict,sorted(list(rgb_dict.keys())))
    
#    print(rgb_dict)
    
    return rgb_dict

#==============================================================================    
#由img_rgb生成img_tag
def RGB2Tag(img_rgb,rgb_dict,show=False,axis=False):
    
    img_tag=np.zeros((np.shape(img_rgb)[0],np.shape(img_rgb)[1]))
    
    #给img_tag矩阵赋值
    for i in range(np.shape(img_tag)[0]):
        
        for j in range(np.shape(img_tag)[1]):
            
            img_tag[i,j]=DictKeyOfValue(rgb_dict,list(img_rgb[i,j].astype(int)))
    
    #显示
    if show:
        
        plt.figure()
        plt.imshow(img_tag,cmap='gray')
        
        #显示坐标轴吗
        if axis:
            
            plt.axis('off')
            
    return img_tag

#==============================================================================    
#由img_tag生成img_rgb
def Tag2RGB(img_tag,rgb_dict,show=False,axis=False):
    
    #初始化这个rgb矩阵
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
        
        #显示坐标轴吗
        if axis:
            
            plt.axis('off')
            
    return img_rgb

#============================================================================== 
#字典按value搜索key
def DictKeyOfValue(dictionary,value):
    
    #键列表
    keys=list(dictionary.keys())
    
    #值列表
    values=list(dictionary.values())
    
    #要查询的值为value
    key=keys[values.index(value)]
    
    return key

#============================================================================== 
#让字典索引以某列表的顺序排列
def DictSortByIndex(which_dict,which_keys):
    
    #结果
    that_dict={}
    
    #遍历新列表，并填充字典
    for this_key in which_keys:
        
        that_dict[this_key]=which_dict[this_key]
        
    return that_dict

#============================================================================== 
#打开颗粒文件并导入数据
def ImportFile(input_file):
    
    #打开颗粒文件
    with open(input_file,"r") as file:
        
        file_lines=file.readlines()
    
    particle_data=[]
    
    for this_item in file_lines:
        
        particle_data.append(this_item.split())
        
    #去掉抬头   
    file_head=particle_data[0]
    particle_data.remove(file_head)
    
    return particle_data,file_head

#==============================================================================       
#建立YADE能识别的rgb索引
def InitYadeRgbDict(rgb_dict):
    
    #导入yade颜色索引
    color_map=Color.get_color_map('ColorRicebal.txt')
    
    #建立和yade直接相关的rgb索引
    tag_list=list(rgb_dict.keys())
    yade_rgb_list=color_map[0]
    
    while len(tag_list)>len(yade_rgb_list):
        
        yade_rgb_list*=2
          
    yade_rgb_dict=dict(zip(tag_list,random.sample(yade_rgb_list,len(tag_list))))

    return yade_rgb_dict

#============================================================================== 
#建立模型
def GnerateModel(img_tag,rgb_dict,particle_data,show=False):
    
    #model image
    model_dimensions=[np.shape(img_tag)[0],np.shape(img_tag)[1]]
    
    model_length=max(model_dimensions)
    model_height=min(model_dimensions)
    
    #print(model_length,model_height)
    
    #横纵比
    model_ratio=model_length/model_height
    
    #生成xyz列表
    x=[float(this_data[0]) for this_data in particle_data]
    y=[float(this_data[1]) for this_data in particle_data]
    z=[float(this_data[2]) for this_data in particle_data]
    r=[float(this_data[3]) for this_data in particle_data]
    
    #用于plt的颜色列表
    color_list=['red','green','blue','brown','purple','black','yellow','gray']
    
    #显示吗
    if show:
        
        #初始沉积模型
        fig=plt.figure()
        
        for k in range(len(particle_data)):
            
            that_color=random.sample(color_list,1)[0]
            
            plt.plot(y[k],z[k],'o',markersize=r[k],color=that_color)
        
        plt.axis('scaled')
    
        fig.savefig('original.png',dpi=300,bbox_inches='tight')
        
#    print(max(y),min(y))
    
    #particle file
    particle_dimensions=[max(y)-min(y),max(z)-min(z)]
    
    particle_length=max(particle_dimensions)
    particle_height=min(particle_dimensions)
    
#    print(particle_length,particle_height)
    
    particle_ratio=particle_length/particle_height
    
    #print(particle_ratio,model_ratio)
    
    if particle_ratio>model_ratio:
        
        print('ERROR:Increase the thickness of particle cloud')
        
    else:
        
        #比较length
#        print(particle_length,model_length)
        
        #缩放比率
        shrink_ratio=particle_length/model_length
        
        #缩放之后新的维度
        new_model_length=int(np.ceil(model_length*shrink_ratio))
        new_model_height=int(np.ceil(model_height*shrink_ratio))
        
        new_shape=(new_model_height,new_model_length)
        
        #让model_length去逼近particle_length
        new_img_tag=ResizeGrayNearby(img_tag,new_shape)
        
    #    plt.figure()
    #    plt.imshow(new_img_tag)
        
        #暴力检索所有颗粒，对他们赋予颜色tag
        tag=[]
        
        #重要的事情，将他们翻转，并改变索引
        for k in range(len(particle_data)):
            
            #新索引
            new_i=int(np.round(new_model_height-z[k]))
            new_j=int(np.round(y[k]))
            
            #正常情况，在矩阵内
            if 0<=new_i<new_model_height and 0<=new_j<new_model_length:
                
                tag.append(new_img_tag[new_i,new_j])
                
            #多出来的部分定义为None，随后消灭
            else:
                
                tag.append(None)
                
        #删除None列表
        new_data=[]
        
        for k in range(len(particle_data)):
            
            if tag[k] is not None:
                
                #为了输出整齐
                new_data.append([x[k],
                                 y[k],
                                 z[k],
                                 r[k],
                                 tag[k]])
    
        #显示吗
        if show:
                
            #验证一下new_data的准确性如何            
            valid_y=[this_data[1] for this_data in new_data]
            valid_z=[this_data[2] for this_data in new_data]
            valid_r=[this_data[3] for this_data in new_data]
            valid_tag=[this_data[4] for this_data in new_data]
            
            #用于plt的颜色索引
            tag_list=list(rgb_dict.keys())
            color_dict=dict(zip(tag_list,color_list[:len(tag_list)]))
            
            #画个有颜色的
            fig=plt.figure()
            
            for k in range(len(new_data)):
                
                plt.plot(valid_y[k],
                         valid_z[k],
                         marker='o',
                         markersize=valid_r[k],
                         color=color_dict[valid_tag[k]])
        
            plt.axis('scaled')
              
            fig.savefig('final.png',dpi=300,bbox_inches='tight')
            
        return new_data

#============================================================================== 
#输出颗粒文件
def ExportFile(file_head,new_data,output_file):
    
    #修改表头
    file_head[-1]+='_tag'
    
    #输出颗粒文件
    with open(output_file,"w") as file:
        
        #加入抬头
        for this_str in file_head:
            
            file.write(str(this_str))
            file.write(' ') 
            
        for this_line in new_data:
    
            file.write('\n')  
            
            for this_data in this_line:
                
                file.write(str(this_data))
                file.write(' '*(10-len(str(this_data))))  
                