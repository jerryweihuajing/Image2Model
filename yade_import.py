# -*- coding: utf-8 -*-
"""
Created on Fri Dec 21 15:32:21 2018

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：YADE import
"""

"""
Import geometry from various formats ('import' is python keyword, hence the name 'ymport').
"""

from yade.wrapper import *
from yade import utils

from minieigen import * 

def textExt(fileName,format='x_y_z_r',shift=Vector3.Zero,scale=1.0,attrs=[],**kw):
   """Load sphere coordinates from file in specific format, returns a list of corresponding bodies; that may be inserted to the simulation with O.bodies.append().
   
   :param str filename: file name
   :param str format: the name of output format. Supported `x_y_z_r`(default), `x_y_z_r_matId`, 'x_y_z_r_attrs'
   :param [float,float,float] shift: [X,Y,Z] parameter moves the specimen.
   :param float scale: factor scales the given data.
   :param list attrs: attrs read from file if export.textExt(format='x_y_z_r_attrs') were used ('passed by refernece' style)
   :param \*\*kw: (unused keyword arguments) is passed to :yref:`yade.utils.sphere`
   :returns: list of spheres.

   Lines starting with # are skipped
   """
   infile = open(fileName,"r")
   lines = infile.readlines()
   infile.close()
   ret=[]
   for line in lines:
      data = line.split()
      if (data[0] == "#format"):
         format=data[1]
         continue
      elif (data[0][0] == "#"): continue
      
      if (format=='x_y_z_r'):
         pos = Vector3(float(data[0]),float(data[1]),float(data[2]))
         ret.append(utils.sphere(shift+scale*pos,scale*float(data[3]),**kw))
      elif (format=='x_y_z_r_matId'):
         pos = Vector3(float(data[0]),float(data[1]),float(data[2]))
         ret.append(utils.sphere(shift+scale*pos,scale*float(data[3]),material=int(data[4]),**kw))
      
      elif (format=='id_x_y_z_r_matId'):
         pos = Vector3(float(data[1]),float(data[2]),float(data[3]))
         ret.append(utils.sphere(shift+scale*pos,scale*float(data[4]),material=int(data[5]),**kw))

      elif (format=='x_y_z_r_attrs'):
         pos = Vector3(float(data[0]),float(data[1]),float(data[2]))
         s = utils.sphere(shift+scale*pos,scale*float(data[3]),**kw)
         ret.append(s)
         attrs.append(data[4:])
         
      else:
         raise RuntimeError("Please, specify a correct format output!");
         
   return ret

def FromText(file_name,shift=Vector3.Zero,scale=1.0):

    import sys
    sys.path.append(r'/home/weihuajing/Desktop/2D')

    import get_color_map as Color

    yade_rgb_list=Color.get_color_map('ColorRicebal.txt')[0]

    tag_list=[k-2 for k in range(10)]
          
    #add the length
    while len(tag_list)>len(yade_rgb_list):
        
        yade_rgb_list*=2

    import random     
    yade_rgb_dict=dict(zip(tag_list,yade_rgb_list[:len(tag_list)]))

    #output particles
    spheres=[]
    
    #import txt_file
    with open(file_name,'r') as file:
     
        lines=file.readlines()
        
        file.close()
        
    #attain the format of the sample
    for this_line in lines:
        
        this_data=this_line.split()
        
        if (this_data[0] == "#format"):
            
            this_format=this_data[1]
            
            #discuss the case where all attributes exist
            all_attributes=this_format.split('_')
            
            continue

        if (this_format=='x_y_z_r_tag'):
            
            that_pos=Vector3(float(this_data[0]),float(this_data[1]),float(this_data[2]))
            that_radius=scale*float(this_data[3])
            
            that_tag=float(this_data[4])
            that_rgb=yade_rgb_dict[that_tag]

	    that_color=Vector3(that_rgb[0],that_rgb[1],that_rgb[2])

            that_sphere=utils.sphere(that_pos,that_radius)
            that_sphere.shape.color=that_color
             
	    #define the fault
	    that_sphere.material.frictionAngle=0

            spheres.append(that_sphere)
     
    return spheres

