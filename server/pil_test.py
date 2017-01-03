from __future__ import print_function
import os
import sys
import math
import numpy as np
from decimal import *

from PIL import Image

def shuffle(input_data, output_data, size):
	width, height = size
	pix=[0, 0]
	delta_x = 40     #lower delta for high distortion
	delta_y = 40     #higher delta for low distortion

	for x in range(width):
		for y in range(height):
			x_shift, y_shift =  ( int(abs(math.sin(x)*width/delta_x)) ,
					int(abs(math.tan(math.sin(y)))*height/delta_y))

			if x + x_shift < width:
				pix[0] = x + x_shift
			else:
				pix[0] = x

			if y + y_shift < height :
				pix[1] = y + y_shift
			else:
				pix[1] = y

			output_data[x,y] = input_data[tuple(pix)]

def wave(input_data, output_data, size):
	width, height = size
	print(width, height)
	wavelength = (Decimal(1)/Decimal((width/2)))*Decimal(math.pi)
	amplitude = (height/6)
	print(wavelength, amplitude)

	for x in range(width):
		for y in range(height):
			shift = math.sin(wavelength*x)*amplitude
			new_y = y + shift
			if new_y < height and new_y > 0:
				output_data[x,y] = input_data[x, new_y]
			else:
				output_data[x,y] = input_data[x, y]

infile = sys.argv[1]
name, ending = os.path.splitext(infile)
outfile = name + "_new" + ending

input_img = Image.open(infile)
input_data = input_img.load()

output_img = Image.new("RGB", input_img.size, "black")
output_data = output_img.load()

if sys.argv[2] == "w":
	wave(input_data, output_data, input_img.size)
if sys.argv[2] == "s":
	shuffle(input_data, output_data, input_img.size)
if sys.argv[2] == "b":
	wave(input_data, output_data, input_img.size)
	shuffle(output_data, output_data, input_img.size)

output_img.save(outfile)
input_img.show()
output_img.show()
