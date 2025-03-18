from diffractio import np, plt, um, mm, nm
from diffractio.scalar_masks_XY import Scalar_mask_XY
from diffractio.scalar_sources_XY import Scalar_source_XY
import numpy as np
import matplotlib.pyplot as plt
from ipywidgets import widgets, interact

def update_plot(
        diameter_mm, 
        screen_distance_cm, 
        resolution,
        wavelength_nm,
        shape,
        minor_diameter_mm, 
        n, 
        roughness_um,
    ):

    radius = 0.5 * diameter_mm * mm
    minor_radius = minor_diameter_mm * 0.5 * mm
    screen_distance = screen_distance_cm * 10 * mm
    roughness = roughness_um * um
    beam_radius = 1.5 * radius
    area_width = 2 * radius

    x0 = np.linspace(-area_width, area_width, resolution)
    y0 = np.linspace(-area_width, area_width, resolution)
    wavelength = wavelength_nm * nm

    u0 = Scalar_source_XY(x0, y0, wavelength)
    u0.gauss_beam(r0=(0 * um, 0 * um), w0=beam_radius, z0=0, A=1, theta=0.0)

    obstacle = Scalar_mask_XY(x0, y0, wavelength)

    # Shape selection
    match shape:
        case "Rough Circle":
            obstacle.circle_rough(r0=(0 * um, 0 * um), radius=radius, sigma=roughness, angle=0)
        case "Ellipse":
            obstacle.circle(r0=(0 * um, 0 * um), radius=(radius, minor_radius))
        case "ETH":  # ETH Zurich Logo-like shape
            obstacle.image("./eth logo.png")
        case "Star":
            obstacle.star(n, radii=[radius, minor_radius] * n)
        case "Regular n-gon":
            obstacle.regular_polygon(n,radius)
        case _:
            obstacle.circle(r0=(0 * um, 0 * um), radius=radius)

    obstacle.inverse_amplitude()
    obstacle.draw()
    u1 = u0 * obstacle
    arago_point = u1.RS(z=screen_distance)
    arago_point.draw()
    arago_point.draw_profile([-area_width, 0], [area_width, 0], npixels=resolution, order=3)
    plt.show()

diameter_box = widgets.BoundedFloatText(min=0, max=4.0, step=0.05, value=1.0, description='Diameter [mm]', continuous_update=False)
screen_distance_slider = widgets.FloatSlider(min=1, max=100, step=1, value=50, description='Screen Distance [cm]', continuous_update=False)
resolution_box = widgets.BoundedIntText(min=1, max=4096, step=1, value=128, description='Resolution', continuous_update=False)
shape_selector = widgets.Dropdown(options=['Circle', 'Rough Circle', 'Ellipse', 'Star', 'Regular n-gon', 'ETH'], description="Shape")
wavelength_box = widgets.BoundedFloatText(min=200, max=1000, value=632.8, description="Wavelength [nm]")
# Shape-specific parameter widgets
minor_diameter_box = widgets.BoundedFloatText(min=0, max=4.0, step=0.05, value=0.8, description="Minor Diameter [mm]", continuous_update=False)
roughness_box = widgets.BoundedFloatText(min=3, max=4000, step=1, value=5, description="Roughness [µm]", continuous_update=False)
n_box = widgets.BoundedIntText(min=1, value=5, description="n", continuous_update=False)

# Container for shape-specific widgets
shape_specific_widgets = widgets.VBox([])

# UI layout
ui = widgets.VBox([diameter_box, screen_distance_slider, wavelength_box, resolution_box, shape_selector, shape_specific_widgets])

def update_ui(*args):
    global shape_selector, shape_specific_widgets
    shape = shape_selector.value
    shape_specific_widgets.children = []
    
    match shape:
        case "Rough Circle":
            shape_specific_widgets.children = [roughness_box]
        case "Ellipse":
            shape_specific_widgets.children = [minor_diameter_box]
        case "Star":
            shape_specific_widgets.children = [n_box, minor_diameter_box]
        case "Regular n-gon":
            shape_specific_widgets.children = [n_box]

# Observe shape selection change
shape_selector.observe(update_ui, names='value')

output = widgets.interactive_output(update_plot, {
    'diameter_mm': diameter_box, 
    'screen_distance_cm': screen_distance_slider,
    'wavelength_nm': wavelength_box,
    'resolution': resolution_box,
    'shape': shape_selector,
    'minor_diameter_mm': minor_diameter_box,
    'n': n_box,
    'roughness_um': roughness_box,
})

# Display UI and output
ui.layout
output.layout.width= "300px"
display(ui, output)
