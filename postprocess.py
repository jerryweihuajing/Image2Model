# -*- coding: utf-8 -*-
"""
Created on Sat Oct  6 13:40:11 2018

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：离散元后处理

%particle to group
%INPUT  a particle file , format [x y r]
%       a gray bmp, gray value 1-256

输入颗粒信息[x y r]文件和灰度比色卡文件

%OUTPUT a file , format [x y r group (color)] 

输出建模结果（图像）

%把颗粒像素化
%投射到最近的像素点上，像素点的灰度值是多少，该颗粒就属于哪个组
%速度快，边界处颗粒不会被忽略

"""

import matplotlib.pyplot as plt
import numpy as np

#定义重力加速度
global g
g=-9.81

file1=open(r'C:\Users\whj\Desktop\DEM后处理\example_grouping_xyr.dat','r')
file2=open(r'C:\Users\whj\Desktop\DEM后处理\example_xyr.dat','r')
file3=open(r'C:\Users\whj\Desktop\DEM后处理\ini_xyr.dat','r')

#__init__只在建立这个对象时运行，如果要修改某个特征，需要另外定义一个函数

#==============================================================================  
#定义颗粒这个类
#x_pos,y_pos,radius表示颗粒的坐标和半径
#F为合外力（接触力为主）
#color表示颗粒的颜色
#density表示密度
#position表示小球的位置坐标
#velocity为速度
#acceleration为加速度:向上向右取正
#Kn为法向劲度系数
#Ks为切向弹性模量
#viscous为粘滞衰减系数
#damping为阻尼
#friction为摩擦系数
#fix为颗粒是否固定的bool
#is_box,is_pad判断是否为墙体或板的组成部分
#attribute表示岩体性质
#==============================================================================  
class particle:
    def __init__(self,id=None,
                 attribute=None,
                 radius=None,
                 density=None,
                 mass=None,
                 color=None,
                 viscous=0,
                 Kn=None,
                 Ks=None,
                 fix=False,
                 is_box=False,
                 is_pad=False,
                 friction=None,
                 position=np.array([None,None]),
                 force=np.array([None,None]),
                 acceleration=np.array([None,None]),
                 velocity=np.array([None,None])):
        
        self.id=id
        self.attribute=attribute
        self.mass=mass
        self.density=density
        self.position=position
        self.radius=radius
        self.color=color
        self.force=force
        self.velocity=velocity
        self.acceleration=acceleration
        self.fix=fix
        self.is_box=is_box
        self.is_pad=is_pad
        self.Kn=Kn
        self.Ks=Ks
        self.viscous=viscous
        self.friction=friction
        
    #颜色选择器
    #若字典为空则返回默认颜色'blue'
    #若字典非空则返回键值查询结果
    def Color(self):
        
        #判断键值对是否存在
        if map_attribute_color=={}:
            
            return 'blue'   
        
        else:   
            
            return map_attribute_color[self.attribute] 
        
    #在窗口win中画上自己
    def DrawAt(self,win):
        
        from matplotlib.patches import Circle
             
        new_circle=Circle(xy=(self.position[0],self.position[1]),
                                       radius=self.radius,
                                       color=self.Color(),
                                       fill=True)
        
        win.add_patch(new_circle)
        
    #初始化力：单个球  
    def InitForce(self):
        
        self.force=np.array([0.0,0.0])
        
    #更新小球位置
    def UpdatePosition(self,dt):
        
        #当没有质量时，通过密度和半径计算质量
        if self.mass is None:  
            
            self.mass=np.pi*self.density*self.radius**2
            
        #判断小球是否固定且是否为box,pad的组成元素 
        if (self.fix is False) and (self.is_box is False) and (self.is_pad is False):
            
            #先更新加速度
            self.acceleration=self.force/self.mass
            
            #重力加速度
            self.acceleration[1]+=g 
            
            #更新速度，dt为时间步长
            self.velocity+=self.acceleration*dt
            
            #x=(v0+vt)*t/2
            self.position+=self.velocity*dt-0.5*self.acceleration*dt**2
            
        #判断小球是否为Pad的组成元素，它的速度和加速度初始给定
        if self.is_pad is True:
            
            self.position+=self.velocity*dt
            #给定初始加速度时：加上0.5*a*t**2
                       
#            if self.acceleration is not None:
#                #x=v0t*t+0.5*a**2
#                self.position+=0.5*self.acceleration*dt**2
             
#==============================================================================  
#建立box类：假设box是一个矩形
#left_right,bottom_top表示上下左右的界限数组
#position表示box中心的坐标
#width和height表示矩形的宽度和高度
#==============================================================================          
class box:
    def __init__(self,id=None,
                 color=None,
                 left_right=None,
                 bottom_top=None,
                 top=None,
                 position=None,
                 width=None,
                 height=None):
        
        self.id=id
        #默认颜色为黑色
        self.color='black'
        self.left_right=left_right
        self.bottom_top=bottom_top
        self.position=position
        self.width=width
        self.height=height
    
    #Init函数：实现left,right,bottom,top与position,width,height在缺省时的互相转化
    def Init(self):
        
        #left_right,bottom_top缺省
        if self.left_right==None:          
            self.left=[self.position[0]-self.width/2,self.position[0]+self.width/2]
                  
        if self.bottom_top==None:
            self.top=[self.position[1]-self.height/2,self.position[1]+self.height/2]
                    
        #position,width,height缺省
        if self.position==None:
            self.position=np.array([np.mean(self.left_right),np.mean(self.bottom_top)])/2
            
        if self.width==None:
            self.width=max(self.left_right)-min(self.left_right)
            
        if self.height==None:
            self.height=max(self.bottom_top)-min(self.bottom_top)
            
    #在窗口win中画上自己
    def DrawAt(self,win):
        
        from matplotlib.patches import Rectangle
        
        new_rectangle=Rectangle(xy=(min(self.left_right),min(self.bottom_top)),
                                       width=self.width,
                                       height=self.height,
                                       color=self.color,
                                       fill=False)
        
        win.add_patch(new_rectangle)
        
#==============================================================================  
#建立网格类
#left_right,bottom_top网格的上下左右界限
#particles表示位于网格内的particle对象
#==============================================================================  
class grid:
    def __init__(self,id=None,
                 left_right=None,
                 bottom_top=None,
                 particles=None):
        
        self.id=id
        self.left_right=left_right
        self.bottom_top=bottom_top
        self.particles=particles
        
#    在窗口win中画上自己
#    def DrawAt(self,win):
#        
#        from matplotlib.patches import Rectangle
#        
#        new_rectangle=Rectangle(xy=(min(self.left_right),min(self.bottom_top)),
#                                       width=self.width,
#                                       height=self.height,
#                                       color=self.color,
#                                       fill=False)
#        
#        win.add_patch(new_rectangle)
        
        
win=plt.gca()

#new_particle=particle()
#new_particle.position=[0,0]
#new_particle.radius=1
#new_particle.color='black'

#new_particle.DrawAt(win)

particle_information=file3.readlines()

#a2=file2.readlines()
#a3=file3.readlines()

#删除空行
for k in range(len(particle_information)):
    
    if particle_information[k]=='\n':
        
        particle_information.remove(particle_information[k])
    
#颗粒列表
Particle=[]

count=0

#建立attribute
color=['black','blue','red','green','gray','brown']

#建立color的列表
attribute=[]

for item in particle_information:
    
    if len(item.split())>3:
        
        if item.split()[3] not in attribute:
            
            attribute.append(item.split()[3])
        
#设置为全局变量比较牛逼
global map_attribute_color     
   
#建立属性和颜色的键值对
map_attribute_color=dict(zip(attribute,color[:len(attribute)]))
    
#对输入文件进行定义
for item in particle_information:
     
    #计数
    count+=1
  
    #定义新的particle
    new_particle=particle()
    
    new_particle.id=count
    new_particle.position=np.array([float(item.split()[0]),float(item.split()[1])])
    new_particle.radius=float(item.split()[2])
    
    #行内容较多时
    if len(item.split())>3:
        
        new_particle.attribute=item.split()[3]
        
    new_particle.DrawAt(win)
    
    Particle.append(new_particle)
    
x_Particle=[this_particle.position[0] for this_particle in Particle]
y_Particle=[this_particle.position[1] for this_particle in Particle]
r_Particle=[this_particle.radius for this_particle in Particle]

xx=[min(x_Particle)-max(r_Particle),max(x_Particle)+max(r_Particle)]
yy=[min(y_Particle)-max(r_Particle),max(y_Particle)+max(r_Particle)]

new_box=box()
new_box.left_right,new_box.bottom_top=xx,yy
new_box.color='black'

new_box.Init()

new_box.DrawAt(win)

#比例优良
plt.axis('equal')

#然后转化位img