#!/usr/bin/env python

import numpy as np
import scipy as sp
import os
from PIL import Image, ExifTags
from PIL import ImageOps, ImageEnhance
from PIL.ExifTags import TAGS
from datetime import datetime
import matplotlib.pyplot as plt
from uncertainties import ufloat, umath

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

def perform_measurement(measurement):
  '''Performs all necessary file operations and calculations, returns 2*n array containing times and meter coordinates'''
  # Arguments needed for pixel to meter conversion:
    # Folder name
    # Laser height in pixel
    # Reference pixel coordinates
    # Respective reference meter coordinates (at least three pairs of pixel-meter reference points are required, but the more the better)
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

  filename = f'measurement{measurement}'
  if os.path.isfile(f'{filename}.npy'):
    t, x = np.load(f'{filename}.npy')
  else:
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
    np.save(filename, np.array([t, x]))
  return measurement, t, x

def fit_model(measurement, t, x, plot=False):
  '''Return angular frequency and equilibrium position of sine wave fitted to t, x'''
  def model(t, A, omega, phase, offset):
    '''Expected sine wave model'''
    return A * np.sin(omega * t + phase) + offset
  # Fit sine wave
  guess = [0.6, 2*np.pi/500, 3*np.pi/2, 1.97]
  (A_fit, omega_fit, phase_fit, offset_fit), pcov = sp.optimize.curve_fit(model, t, x, sigma=0.004,p0=guess, absolute_sigma=True)
  # Uncertainties
  _, omega_fit_std, _, offset_fit_std = np.sqrt(np.diag(pcov))
  omega, offset = [ufloat(omega_fit, omega_fit_std), ufloat(offset_fit, offset_fit_std)]
  print(f'Measurement {measurement}: omega: {omega}/s, equilibrium: {offset}m')
  if plot:
    plt.plot(t, x, label='Measured')
    plt.plot(t, model(t, A_fit, omega_fit, phase_fit, offset_fit), label='Fitted')
    plt.title(f'Measurement {measurement}')
    plt.xlabel('Time [s]')
    plt.ylabel('X [m]')
    plt.legend()
    plt.show()
    # Plot Fourier transform of the measurement
    # plt.semilogy(np.fft.rfftfreq(len(t), d=(t[-1] - t[0])/len(t)), np.abs(np.fft.rfft(x)))
    # plt.xlim(-0.003, 0.003)
    # plt.show()
  return omega, offset

def calculate_G(omega, eq1, eq2):
  '''Return a ufloat for the calculated value for the gravitational constant from omega and the two equilibrium positions'''
  # Necessary measurements and values with errors
  mirror = ufloat(2.04, 0.005) # Absolute position of the mirror
  mirror_wall = ufloat(1.885, 0.005) # Distance between mirror and wall
  x = y = ufloat(0.1, 0.0005) # x and y lengths of masses
  z = ufloat(0.102, 0.0005) # z length of masses
  rho = ufloat(11348, 0.5) # Density of lead
  M = x*y*z * rho
  L = ufloat(1.1, 0.0005) # Distance between the two pendulum masses
  r = ufloat(0.121, 0.0005) # Distance pendulum mass to secondary mass: 3 oscillations measured, (0.8+-0.05)cm at closest and (3.4+-0.05)cm at farthest point
  # Calculate the deflection angle
  theta_1 = 1/2 * umath.atan(umath.fabs(eq1 - mirror) / mirror_wall)
  theta_2 = 1/2 * umath.atan(umath.fabs(eq2 - mirror) / mirror_wall)
  theta = umath.fabs(theta_1 - theta_2)
  # Gravitational constant
  G = omega**2 * L * r**2 * theta / (2 * M)
  return G

# Use the images from here: https://drive.google.com/drive/folders/1Izo4OTF3CGaBjcfKXcR-0cL6bZGwFbdK and unpack them into a folder with the same name as the zip

w1, e1 = fit_model(*perform_measurement('3a'))
w2, e2 = fit_model(*perform_measurement('3b'))
G = calculate_G(w1, e1, e2)
print(f'G = {G} m^3 / kg s^2')
