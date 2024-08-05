import matplotlib.pyplot as plt
from matplotlib.widgets import Slider


class Splice:
    def __init__(self):
        self.layer_num = 1
        self.last_plotted_layer = 1
        self.holes = []
        self.hole_offset = np.array([0, 0])
        self.layers = []
        self.min_path_coords = np.array([np.inf, np.inf, np.inf])
        self.max_path_coords = np.array([-np.inf, -np.inf, -np.inf])
        self.layer_plots = []
        self.fig = None
        self.ax = None

    def set_layers(self, layers):
        self.layers = layers
        self.calculate_path_lims()
        
    
    def calculate_path_lims(self):
        for layer in self.layers:
            for path in layer:
                for point in path:
                    self.min_path_coords = np.minimum(self.min_path_coords, point)
                    self.max_path_coords = np.maximum(self.max_path_coords, point)
        self.path_midpoint = (self.min_path_coords + self.max_path_coords) / 2


    def plot(self):
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        self.fig.subplots_adjust(left=0.25, bottom=0.25)
        self.ax.set_aspect('equal', adjustable='box')
        plt.title('Slice Viewer')
        plt.xlabel('X (mm)')
        plt.ylabel('Y (mm)')

        # Set the plot area to be +-5 of the min and max path coordinates
        min_x = self.min_path_coords[0] - 5
        max_x = self.max_path_coords[0] + 5
        min_y = self.min_path_coords[1] - 5
        max_y = self.max_path_coords[1] + 5
        self.ax.set_xlim(min_x, max_x)
        self.ax.set_ylim(min_y, max_y)

        ## Pre-plot all the paths, just set them to be invisible
        for layer in layers:
            layer_plot = []
            for path in layer:
                if len(path) > 0:
                    path = np.array(path)
                    plot_lines = self.ax.plot(path[:,0], path[:,1], color='blue', linewidth=0.5, visible=False)
                layer_plot.append(plot_lines)
            self.layer_plots.append(layer_plot)

        # Make a vertically oriented slider
        axlayer = self.fig.add_axes([0.1, 0.25, 0.0225, 0.63])
        layer_slider = Slider(
            ax=axlayer,
            label="Layer",
            valmin=1,
            valmax=len(self.layers),
            valinit=self.layer_num,
            valstep=1,  # Set the step size to 1 for discrete integer intervals
            orientation="vertical",
        )

        layer_slider.on_changed(self.update_plot_layer)
        self.update_plot_layer(self.layer_num)
        plt.show()

    # The function to be called anytime a slider's value changes
    def update_plot_layer(self, val):
        # last_layer_plot = self.layer_plots[self.last_plotted_layer-1]
        # for line in last_layer_plot:
        #     for l in line:
        #         l.set_visible(False)
        # layer_plot = self.layer_plots[val-1]
        # for line in layer_plot:
        #     for l in line:
        #         l.set_visible(True)
        # self.last_plotted_layer = val
        # self.fig.canvas.draw_idle()
        pass


    
    


hole_offset = path_midpoint[:2] - hole_midpoint

splice = Splice()
splice.set_layers(layers)
splice.plot()