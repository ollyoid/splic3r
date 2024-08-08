import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider, Button
import splic3r.gcode
import splic3r.drl

drl = "../Characterisation/Characterisation_board_demo/Characterisation Board-PTH.drl"
in_gcode = "../Characterisation/4 Point/First/4point.gcode"
out_gcode = "../Characterisation/4 Point/First/out.gcode"


def plot():
    ## Parse various data from the gcode file
    gcode = splic3r.gcode.GCode.from_file(in_gcode)


    last_layer = 0

    ## We're going to generate a list printer moves so we can plot them
    max_layers = gcode.lines[-1].state.layer
    layers = []
    for layer in range(1, max_layers+1):
        # get all the lines where the layer number is right
        lines = [line for line in gcode.lines if line.state.layer == layer]
        paths = []
        extruding = False
        for i, line in enumerate(lines):
            if line.state.extruding:
                if not extruding:
                    paths.append(([lines[i-1].state.current_position]))
                paths[-1].append(line.state.current_position)
                extruding = True
            else:
                extruding = False
        layers.append(list(map(np.array, paths)))

    ## Calculate the bounding box of all the printer moves
    min_path_coords = np.array([np.inf, np.inf, np.inf])
    max_path_coords = np.array([-np.inf, -np.inf, -np.inf])

    for layer in layers:
        for path in layer:
            for point in path:
                    min_path_coords = np.minimum(min_path_coords, point)
                    max_path_coords = np.maximum(max_path_coords, point)

    path_midpoint = (min_path_coords + max_path_coords) / 2

    drill_file = splic3r.drl.DrillFile.from_file(drl)


    holes = drill_file.drills['T1']
    holes_array = np.array(holes)

    # Calculate the midpoint using NumPy
    min_holes_coords = holes_array.min(axis=0)
    max_holes_coords = holes_array.max(axis=0)
    hole_midpoint = (min_holes_coords + max_holes_coords) / 2

    ## A Class for the plot to keep track of the splice state

    class Splice:
        def __init__(self, layers):
            self.layer_num = 1
            self.layers = layers
            self.max_layer = len(layers)
            self.hole_offset = np.array([0,0])
            self.plot_offset = np.array([0,0])
            self.mirrored = False
        

    splice = Splice(layers)
    splice.hole_offset = path_midpoint[:2] - hole_midpoint




    last_layer = splice.layer_num

    fig, ax = plt.subplots(figsize=(10, 8))
    fig.subplots_adjust(left=0.25, bottom=0.25)
    ax.set_aspect('equal', adjustable='box')
    plt.title('Slice Viewer')
    plt.xlabel('X (mm)')
    plt.ylabel('Y (mm)')

    # Set the plot area to be +-5 of the min and max path coordinates
    min_x = min_path_coords[0] - 5
    max_x = max_path_coords[0] + 5
    min_y = min_path_coords[1] - 5
    max_y = max_path_coords[1] + 5
    ax.set_xlim(min_x, max_x)
    ax.set_ylim(min_y, max_y)

    ## Pre-plot all the paths, just set them to be invisible
    layer_plots = []
    for layer in splice.layers:
        layer_plot = []
        for path in layer:
            if len(path) > 0:
                path = np.array(path)
                plot_lines = ax.plot(path[:,0], path[:,1], color='blue', linewidth=0.5, visible=False)
            layer_plot.append(plot_lines)
        layer_plots.append(layer_plot)

    # Make a vertically oriented slider
    axlayer = fig.add_axes([0.1, 0.25, 0.0225, 0.63])
    layer_slider = Slider(
        ax=axlayer,
        label="Layer",
        valmin=1,
        valmax=splice.max_layer,
        valinit=splice.layer_num,
        valstep=1,  # Set the step size to 1 for discrete integer intervals
        orientation="vertical"
    )

    # The function to be called anytime a slider's value changes
    def update_layer(val):
        nonlocal last_layer
        splice.layer_num = int(val)
        last_layer_plot = layer_plots[last_layer-1]
        for line in last_layer_plot:
            for l in line:
                l.set_visible(False)
        layer_plot = layer_plots[val-1]
        for line in layer_plot:
            for l in line:
                l.set_visible(True)
        last_layer = val

    layer_slider.on_changed(update_layer)
    update_layer(splice.layer_num)

    holes_scatter = None

    def flip(points, midpoint):
        # only flip in x-axis
        return np.array([[point[0], midpoint[1] - (point[1] - midpoint[1])] for point in points])

    def scatter_holes():
        nonlocal holes_scatter
        if holes_scatter is not None:
            holes_scatter.remove()
        flipped = flip(holes_array, hole_midpoint) if splice.mirrored else holes_array
        transformed_holes = flipped + splice.hole_offset + splice.plot_offset
        holes_scatter = ax.scatter(transformed_holes[:,0], transformed_holes[:,1], color='red', s=5, zorder=1)

    scatter_holes()

    x_lims = ax.get_xlim()
    y_lims = ax.get_ylim()

    x_range = x_lims[1]-x_lims[0]
    y_range = y_lims[1]-y_lims[0]


    # Add a horizontally oriented slider for the X offset
    x_offset_ax = fig.add_axes([0.25, 0.1, 0.65, 0.03])
    x_offset_slider = None

    # Add a vertically oriented slider for the Y offset
    y_offset_ax = fig.add_axes([0.95, 0.25, 0.0225, 0.63])
    y_offset_slider = None

    # The function to be called anytime the slider's value changes
    def update_offset(val):
        splice.plot_offset = np.array([x_offset_slider.val, y_offset_slider.val])
        scatter_holes()
        fig.canvas.draw_idle()

    def draw_sliders():
        nonlocal x_offset_slider, x_offset_ax, y_offset_slider, y_offset_ax
        if x_offset_slider is not None:
            x_centre = x_offset_slider.val
        else:
            x_centre = 0
        
        if y_offset_slider is not None:
            y_centre = y_offset_slider.val
        else:
            y_centre = 0

        x_lims = ax.get_xlim()
        y_lims = ax.get_ylim()
        x_range = x_lims[1]-x_lims[0]
        y_range = y_lims[1]-y_lims[0]
        
        x_offset_ax.clear()
        x_offset_slider = Slider(
            ax=x_offset_ax,
            label="X-Offset",
            valmin=x_centre - x_range/2,
            valmax=x_centre + x_range/2,
            valinit=x_centre,
            valstep=0.05,
            orientation="horizontal"
        )
        x_offset_slider.on_changed(update_offset)

        y_offset_ax.clear()
        y_offset_slider = Slider(
            ax=y_offset_ax,
            label="Y-Offset",
            valmin=y_centre - y_range/2,
            valmax=y_centre + y_range/2,
            valinit=y_centre,
            valstep=0.05,
            orientation="vertical"
        )
        y_offset_slider.on_changed(update_offset)

    draw_sliders()

    def on_lim_changed(axes):
        draw_sliders()

    ax.callbacks.connect('xlim_changed', on_lim_changed)
    ax.callbacks.connect('ylim_changed', on_lim_changed)

    # Add a button to set the slider.mirrored to true
    mirrored_button_ax = fig.add_axes([0.25, 0.05, 0.1, 0.04])
    mirrored_button = Button(mirrored_button_ax, 'Mirrored', color='lightgray')

    def set_mirrored(event):
        splice.mirrored = not splice.mirrored
        scatter_holes()

    mirrored_button.on_clicked(set_mirrored)

    plt.show()

plot()