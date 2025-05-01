#!/usr/bin/env python

import numpy as np
import scipy as sp
import os
from PIL import Image, ExifTags
from PIL import ImageOps, ImageEnhance
from PIL.ExifTags import TAGS
from datetime import datetime
import matplotlib.pyplot as plt

def load_band(filename, laser_height, band_width):
  '''Return the important part of the image: a slice at laser_height +- band_width, only green channel'''
  img = Image.open(filename)
  img = ImageOps.exif_transpose(img)  # rotate image according to metadata
  # only take green channel to better isolate the laser
  img = img.getchannel('G')
  img = img.crop((0, laser_height - band_width, img.width, laser_height + band_width))
  return img

def get_x_pixel(filename, laser_height=1350, band_width=50):
  '''Return the pixel value of the brightest spot in the image'''
  # TODO: somehow incorporate uncertainties (maybe)
  img = np.array(load_band(filename, laser_height, band_width))
  averaged = img.mean(axis=0)
  return np.argmax(averaged)

def get_timestamp(filepath):
  '''Return the time at which the image was taken'''
  try:
    img = Image.open(filepath)
    exif = img._getexif()
    if exif:
      for tag, value in exif.items():
        if TAGS.get(tag) == 'DateTimeOriginal':
          return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
  except Exception as e:
    print(f'Error reading {filepath}: {e}')
  return None

def load_and_sort_images(directory):
  '''Return n*2 array of all images with timestamps in the directory and sort them by time'''
  files = [os.path.join(directory, f) for f in os.listdir(directory) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff'))]
  data = [(f, get_timestamp(f)) for f in files]
  data.sort(key=lambda x: x[1])
  return np.array(data)

def create_time_series(directory, laser_height=1350, band_width=50):
  '''Return n*2 array of all measurements: time and pixel value'''
  images = load_and_sort_images(directory)
  first_time = images[0][1]
  return np.array([[(time - first_time).total_seconds(), get_x_pixel(image_path, laser_height, band_width)] for image_path, time in images])

def calculate_x_coordinates(series, pixel_coords=np.array([56, 2307, 4056]), meter_coords=np.array([1.2, 2, 2.49])):
  '''Return n*2 array of all measurements, converted to meters using a tilt adjustment from pixel_coords with meter_coords'''
  def model(x, a, b, c):
    '''Linear perspective model (1D projective transformation):
    f(x) = (a*x + b)/(c*x + 1)
    '''
    return (a*x + b)/(c*x + 1)

  initial_guess = [0.0001, meter_coords[0], 0.0001] # Just some values I think work for measurement 3
  (a_opt, b_opt, c_opt), _ = sp.optimize.curve_fit(model, pixel_coords, meter_coords, p0=initial_guess)

  series_meters = np.copy(series)
  series_meters[:, 1] = model(series_meters[:, 1], a_opt, b_opt, c_opt)
  return series_meters

def model(t, A, omega, phase, offset):
  '''Expected sine wave model'''
  return A * np.sin(omega * t + phase) + offset

# The tracker works by sorting all the images in a folder, then taking a thin slice (containing the laserpointer) of each image and looking for the brightest spot (in the green channel)

# Tutorial for a new measurement:
# - pick directory of the measurement and write that into the 'directory' keyword below
# - determine the y-position of the laser and write the value into the keyword argument 'laser_height' in 'create_time_series' below
#   (if needed adjust the width of the band around which it cuts but ±50 pixels should be fine)
# - determine some values on the measuring tape with fitting horizontal pixel values and use them for 'pixel_coords' and 'meter_coords' (more is better, but at least three are required)

# Use the images from here: https://drive.google.com/drive/folders/1Izo4OTF3CGaBjcfKXcR-0cL6bZGwFbdK and unpack them into a folder named according to the measurement
args = {
  # '1': ['./measurement1', 1350, 1.18, 2.5],
  # '2a': ['./measurement2a', 1200, 0.965, 2.16],
  # '2b': ['./measurement2b', 1220, 0.975, 2.16],
  '3a': ['./measurement3a', 760,
    [60, 568, 1089, 1573, 2019, 2435, 2828, 3193, 3536, 3862, 4080],
    [1.51, 1.6, 1.7, 1.8, 1.9, 2, 2.1, 2.2, 2.3, 2.4, 2.47],
  ],
  '3b': ['./measurement3b', 910,
    [40, 396, 947, 1451, 1913, 2339, 2735, 3102, 3444, 3765, 4066],
    [1.54, 1.6, 1.7, 1.8, 1.9, 2, 2.1, 2.2, 2.3, 2.4, 2.5],
  ],
}

# Choose your measurement here and execute
measurement = '3a'

series = create_time_series(
  directory=args[measurement][0],
  laser_height=args[measurement][1],
  band_width=50,
)
# WARNING: this might take a few minutes every time it's executed

t, x = calculate_x_coordinates(
  series,
  pixel_coords=args[measurement][2],
  meter_coords=args[measurement][3],
).T

# Fit sine wave
guess = [0.6, 2*np.pi/500, 3*np.pi/2, 1.97]
(A_fit, omega_fit, phase_fit, offset_fit), _ = sp.optimize.curve_fit(model, t, x, p0=guess)
print(f'Measurement {measurement}: omega: {omega_fit}/s, equilibrium: {offset_fit}m')

# Plot measurement and fit
plt.plot(t, x, label='Measured')
plt.plot(t, model(t, A_fit, omega_fit, phase_fit, offset_fit), label='Fitted')
plt.xlabel('Time [s]')
plt.ylabel('X [m]')
plt.legend()
plt.show()

# Plot Fourier transform of the measurement
# plt.semilogy(np.fft.rfftfreq(len(t), d=(t[-1] - t[0])/len(t)), np.abs(np.fft.rfft(x)))
# plt.xlim(-0.003, 0.003)
# plt.show()
