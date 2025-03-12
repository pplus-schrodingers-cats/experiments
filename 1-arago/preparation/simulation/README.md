The Files `arago-3d.ipynb` and `arago-library.ipynb` are not of interest and just kept around so we can see the approach we took if we do something similar in the future.

The interesting file is `arago-interactive.ipynb`. You can open it anywhere you can run a Juypter Notebook and just run all cells (usually there's a botton, or press Ctrl + Alt + Shift + Enter)
Then you will see an interactive widget in which you can quicly adjust the parametersto change the simulations. Whenver you change a parameter, click outside the box or press enter so the value is updated. 

### Plots 
- On the top you see an image of the "Mask" so the shape at which we're simulating diffraction. 
- In the middle you can see the image like one that would apear on a sensor `screen_dis (the color scale is always red-ish no matter the wavelength [not my setting])
- The last plot shows the intensity profile across the center horizontal line of the middle plot

### Disclaimers
- Some weird artifacts start to show up if the screen distance is very low, but most of these go away if you increase the resolution
- For some reason the text doesn't display properly next to the sliders, but they work just fine 