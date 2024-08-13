import customtkinter
import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
import os
from CTkToolTip import *
from PIL import Image
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from filename import next_filename
from helpers import *

# colours from https://medium.com/@travall/procedural-2d-island-generation-noise-functions-13976bddeaf9
colors = {
    "grass": '#7b9c50',
    "water": '#0952c7',
    "deepocean": '#003eaf',
    "dirt": [114,98,49],
    "sand": '#c2b282',
    "wetsand": '#a49661',
    "darkforest": '#3c6216',
    "verydarkforest": [40,77,0],
    "forest": "#5A7F33",
    "mountain": "#8E907B",
    "highmountain": "#9EA18E",
    "snow": "white"
}


# frame where map is drawn
class CanvasFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # create a Matplotlib figure and embed in Tkinter based canvas
        self.fig = Figure(figsize=(7,7))
        self.axes = self.fig.add_subplot(111)
        self.axes.set_axis_off()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()

        self.canvas.get_tk_widget().grid(row=0, column=0)

# left frame containing all plot buttons, and different settings frames

# better to pass combobox_callback, slider_value and openimages when instantiating instead of using master.function (App class where the functions are maintained)
class MainFrame(customtkinter.CTkFrame):
    def __init__(self, master, combobox_callback, slider_value, openimages, plot, **kwargs):
        super().__init__(master, **kwargs)

        #take functions from main App class
        self.combobox_callback = combobox_callback
        self.slider_value = slider_value
        self.openimages = openimages
        self.plot = plot

        # open saved images/gifs directory
        self.icon = customtkinter.CTkImage(Image.open("icon.png"), size=(50,50))
        self.opendir_button = customtkinter.CTkButton(master=self, width=50, height=50, image=self.icon, text="", fg_color='transparent', hover_color="#2B2B2B", command=self.openimages)
        self.opendir_button.grid(row=0, column=0, sticky="w")
        
        # begin the drawing process
        self.plot_button = customtkinter.CTkButton(master=self, text="Plot", width=200, command=self.plot, height=50, border_color="aqua", border_width = 2)
        self.plot_button.grid(row=0, column=0, pady=5)

        # map dimensions setting
        self.dimensions_label = customtkinter.CTkLabel(master=self, text="Map dimensions", pady = 5, font=('Helvetica',13,'bold'))
        self.dimensions_label.grid(row=1, column=0)

        self.dimensions_slider = customtkinter.CTkSlider(master=self, from_=128, to=2048, number_of_steps=15, command=lambda val:self.slider_value(val, self.dimension_value))
        self.dimensions_slider.grid(row=2, column=0)
        self.dimensions_slider.set(256)

        self.dimension_value = customtkinter.CTkLabel(master=self, text="Value: 256")
        self.dimension_value.grid(row=3, column=0)

        # toggle method of drawing map, and whether to generate an island
        self.combobox_var = customtkinter.StringVar(value="Algorithm")
        self.combobox = customtkinter.CTkComboBox(self, values=["Basic cellular automaton", "OpenSimplex noise", "Perlin noise"],
                                            command=self.combobox_callback, variable=self.combobox_var, width=300, justify='center')
        self.combobox_var.set("Algorithm")
        self.combobox.grid(row=4, column=0,pady=40)

        self.islandchoice = customtkinter.CTkSwitch(self, text="Generate island")
        self.islandchoice.grid(row=6, column=0, columnspan=2, pady=10)

class CellularAutomatonSettings(customtkinter.CTkFrame):
    def __init__(self, master, iterations_settings, density_settings, slider_value, **kwargs):

        # type check and length check all arguments
        if not isinstance(iterations_settings, tuple) or len(iterations_settings) != 3:
            raise ValueError("iteration_settings must be a tuple of length 3: start, end, increment")
        if not isinstance(density_settings, tuple) or len(density_settings) != 3:
            raise ValueError("density_settings must be a tuple of length 3: start, end, increment")
        
        super().__init__(master, **kwargs)

        self.slider_value = slider_value

        # extract all values from ranges for each setting
        self.iter_start = iterations_settings[0]
        self.iter_end = iterations_settings[1]
        self.iter_increment = iterations_settings[2]
        self.iter_steps = (self.iter_end - self.iter_start) / self.iter_increment

        self.density_start = density_settings[0]
        self.density_end = density_settings[1]
        self.density_increment = density_settings[2]
        self.density_steps = (self.density_end - self.density_start) / self.density_increment

        # create all widgets for CA
        self.iterations_label = customtkinter.CTkLabel(self, text="Iterations")
        self.iterations_slider = customtkinter.CTkSlider(self, from_= self.iter_start, to=self.iter_end, number_of_steps=self.iter_steps, command=lambda val:self.slider_value(val, self.iterations_value))
        self.iterations_value = customtkinter.CTkLabel(self, text="Value: ")
        self.density_label = customtkinter.CTkLabel(self, text="Density")
        self.density_slider = customtkinter.CTkSlider(self, from_=self.density_start, to=self.density_end, number_of_steps=self.density_steps, command=lambda val:self.slider_value(val, self.density_value))
        self.density_value = customtkinter.CTkLabel(self, text="Value: ")

        self.iterations_label.grid(row=0)
        self.iterations_slider.grid(row=1,column=0)
        self.iterations_value.grid(row=2, column=0)
        self.density_label.grid(row=0, column=1)
        self.density_slider.grid(row=1, column=1)
        self.density_value.grid(row=2, column=1)

        self.density_slider.set(60.0)

        self.t = CTkToolTip(self.density_slider, message="Density of water in map. Quite a sensitive setting, 60 is nice")


class NoiseSettings(customtkinter.CTkFrame):
    # all 3 settings are passed as tuples containing the start value, end value, and desired increment
    def __init__(self, master, freq_settings, amp_settings, fractaliser_settings, slider_value, **kwargs):
        # type check and length check all arguments
        if not isinstance(freq_settings, tuple) or len(freq_settings) != 3:
            raise ValueError("freq_settings must be a tuple of length 3: start, end, increment")
        if not isinstance(amp_settings, tuple) or len(amp_settings) != 3:
            raise ValueError("amp_settings must be a tuple of length 3: start, end, increment")
        if not isinstance(fractaliser_settings, tuple) or len(fractaliser_settings) != 3:
            raise ValueError("fractaliser_settings must be a tuple of length 3: start, end, increment")
        
        super().__init__(master, **kwargs)

        # extract from settings tuples
        self.freq_start = freq_settings[0]
        self.freq_end = freq_settings[1]
        self.freq_increment = freq_settings[2]
        self.freq_steps = (self.freq_end - self.freq_start) / self.freq_increment

        self.amp_start = amp_settings[0]
        self.amp_end = amp_settings[1]
        self.amp_increment = amp_settings[2]
        self.amp_steps = (self.amp_end - self.amp_start) / self.amp_increment

        self.fractaliser_start = fractaliser_settings[0]
        self.fractaliser_end = fractaliser_settings[1]
        self.fractaliser_increment = fractaliser_settings[2]
        self.fractaliser_steps = (self.fractaliser_end - self.fractaliser_start) / self.fractaliser_increment

        self.slider_value = slider_value

        # generic template for a noise algorithm's settings. fractaliser is useless though
        self.freq_label = customtkinter.CTkLabel(self, text="Frequency")
        self.freq_label.grid(row=0, column=0)
        self.freq_slider = customtkinter.CTkSlider(self, from_=self.freq_start, to= self.freq_end, number_of_steps=self.freq_steps, command=lambda val: self.slider_value(val, self.freq_value))
        self.freq_slider.grid(row=1, column=0)
        self.freq_value = customtkinter.CTkLabel(self, text="Value: ")
        self.freq_value.grid(row=2, column=0)
        self.amp_label = customtkinter.CTkLabel(self, text="Amplitude")
        self.amp_label.grid(row=0, column=1)
        self.amp_slider = customtkinter.CTkSlider(self, from_=self.amp_start, to=self.amp_end, number_of_steps=self.amp_steps, command=lambda val: self.slider_value(val, self.amp_value))
        self.amp_slider.grid(row=1, column=1)
        self.amp_value = customtkinter.CTkLabel(self, text="Value: ")
        self.amp_value.grid(row=2, column=1)
        self.fractaliser_label = customtkinter.CTkLabel(self, text="Fractaliser")
        self.fractaliser_label.grid(row=3, column=0, columnspan=2)
        self.fractaliser = customtkinter.CTkSlider(self, from_=self.fractaliser_start, to=self.fractaliser_end, number_of_steps=self.fractaliser_steps, command=lambda val: self.slider_value(val, self.fractaliser_value))
        self.fractaliser.set(1.00)
        self.fractaliser.grid(row=4, column=0, columnspan=2)
        self.fractaliser_value = customtkinter.CTkLabel(self, text="Level: ")
        self.fractaliser_value.grid(row=5, column=0, columnspan=2)
        self.t1=CTkToolTip(self.fractaliser, message="How chaotic should it be? Low is less chaotic to high is more chaotic.", delay=0)
        self.t2=CTkToolTip(self.freq_slider, message="Frequency is essentially how often the noise function repeats in a given space. A higher frequency creates more detailed fractal terrain, while lower frequency gives zoomed in and broader terrain")




class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()


        self.title('Procedural map generator')
        self.geometry("1025x600")
        self.resizable(0, 0)

        # Canvas frame
        self.canvasframe = CanvasFrame(master=self)
        self.canvasframe.grid(row=0,column=1,padx=15,pady=15, sticky="nsew")
        self.canvasframe.grid_rowconfigure(0, weight=1)
        self.canvasframe.grid_columnconfigure((0, 1), weight=1)


        # All settings and execute buttons
        self.settingsframe = MainFrame(master=self,
                                   combobox_callback=self.combobox_callback,
                                   slider_value=self.slider_value,
                                   openimages=self.openimages,
                                   plot=self.plot)
        self.settingsframe.grid(row=0,column=0,padx=15,pady=15, sticky="ew")


        ##### framelist containing all individual settings frames embedded in main settings frame ###############
        self.framelist = {}

        ##### cellular automaton settings sliders ##########

        """
        All settings passed must be tuples of length 3 in format (start, end, increment per step)
        """
        
        self.ca_frame = CellularAutomatonSettings(master=self.settingsframe,
                                                  iterations_settings=(1, 20, 1),
                                                  density_settings=(0, 100, 1),
                                                  slider_value=self.slider_value,
                                                  width=350, 
                                                  height=400)
        self.framelist['Basic cellular automaton'] = self.ca_frame


        ######## simplex noise sttings ################
        self.simplexframe = NoiseSettings(master=self.settingsframe,
                                        freq_settings=(0.005, 0.05, 0.005),
                                        amp_settings=(32, 256, 32), 
                                        fractaliser_settings=(0.5, 1.5, 0.25), 
                                        slider_value=self.slider_value,
                                        width=350, 
                                        height=400)
        self.framelist['OpenSimplex noise'] = self.simplexframe
        


        ######################perlin noise###############################
        self.perlinframe = NoiseSettings(master=self.settingsframe,
                                        freq_settings=(0.005, 0.05, 0.005),
                                        amp_settings=(32, 256, 32),
                                        fractaliser_settings=(0.1, 0.6, 0.05),
                                        slider_value=self.slider_value,
                                        width=350,
                                        height=400)
        self.framelist['Perlin noise'] = self.perlinframe
        
        #self.fractaliser_perlin.set(0.25)
       
        ########## stack settings frames on top of each other ################
        for frames in self.framelist.values():
            frames.grid(row=5, column=0, sticky='nsew')

    ############ UPDATING SLIDERS #################
    def slider_value(self, val, label):
        label.configure(text=f"Value: {val:.3f}")

    ############ update which settings frame to show based on combobox ##############
    def combobox_callback(self, choice):
        print("combobox dropdown clicked:", choice)
        self.framelist[choice].tkraise()

    ########### get all values needed for algorithms and save files ##################
    def plot(self):
        map_height = int(self.settingsframe.dimensions_slider.get())
        map_width = int(self.settingsframe.dimensions_slider.get())
        map = np.empty((map_width, map_height), dtype=float)
        option = self.settingsframe.combobox.get()
        if option == 'Basic cellular automaton':
            iterations = int(self.ca_frame.iterations_slider.get())
            density = int(self.ca_frame.density_slider.get())
            #create cellular automaton object with empty map primed up
            ca = CellularAutomaton(map, density, map_width, map_height, self.settingsframe.islandchoice.get())
            grid = ca.noise_grid()  # modify object to have value noise grid (grid is unused variable)
            animation = self.createanimation(ca, iterations)

            newfilename = next_filename("map", ".gif")
            animation.save(filename=f"Saved/{newfilename}", writer="pillow")

        elif option == 'OpenSimplex noise':
            freq = self.simplexframe.freq_slider.get()
            amp = self.simplexframe.amp_slider.get()
            fractalLevel = self.simplexframe.fractaliser.get()
            # create a NoiseConfig object containing all settings neeeded for noise algorithm
            config = NoiseConfig(freq, amp, 2, 0.5, fractalLevel)
            # NoiseGenerator sets up an object to create terrain
            emptymap = NoiseGenerator(map, map_width, map_height, config, self.settingsframe.islandchoice.get())
            island = emptymap.opensimplex()
            self.plotmap(island)

            #save filenames in incrementing order
            newfilename = next_filename("simplex", ".png")
            self.canvasframe.fig.savefig(f"Saved/{newfilename}", bbox_inches="tight")
        
        elif option == 'Perlin noise':
            freq = self.perlinframe.freq_slider.get()
            amp = self.perlinframe.amp_slider.get()
            fractalLevel = self.perlinframe.fractaliser.get()
            config = NoiseConfig(freq, amp, 2, 0.5, fractalLevel)
            emptymap = NoiseGenerator(map, map_width, map_height, config, self.settingsframe.islandchoice.get())
            island = emptymap.perlinnoise2()
            self.plotmap(island)
            newfilename = next_filename("perlin", ".png")
            self.canvasframe.fig.savefig(f"Saved/{newfilename}", bbox_inches="tight")


    # uses this colour map to plot the OpenSimplex and Perlin noise maps   
    def plotmap(self, grid):

        self.canvasframe.axes.set_axis_off()

        colours = [(0, colors["deepocean"]), 
                (0.37, colors["water"]), 
                (0.46,colors["sand"]), 
                (0.47, colors["wetsand"]), 
                (0.56, colors["grass"]),
                (0.59, colors["forest"]),
                (0.64,colors["darkforest"]),
                (0.80,colors["mountain"]), 
                (0.85,colors["highmountain"]), 
                (1,colors["snow"])]
        colourmap = LinearSegmentedColormap.from_list('colourmap',colours, 256)
        #colourmap = colourmap(np.array([0, 0.5,0.53,0.56,0.7,0.73,0.87,1]))

        #places map on canvasframe
        self.canvasframe.axes.imshow(grid, cmap=colourmap, interpolation="bilinear") 
        self.canvasframe.canvas.draw()

    def openimages(self):
        path = r"Saved"
        os.startfile(path)

    ################ CELLULAR AUTOMATON #######################
    
    #automaton is an object plotting. It contains the actual map, methods to generate the value noise grid, and apply the cellular automaton
    def createanimation(self, automaton, totalframes):

        cmap = ListedColormap(["lawngreen","royalblue"])
        #fig.colorbar(plt.cm.ScalarMappable(cmap=cmap), label='Colours', shrink=0.5, ax=axes)
        im = self.canvasframe.axes.imshow(automaton.map, cmap=cmap)
        def animate(i, automaton):

            map = automaton.cellular_automaton()    #creates a map using cellular automata
            im.set_array(map)
            self.canvasframe.canvas.draw()   #UPDATE CANVAS PER ANIMATION WITHIN EVENT LOOP. matplotlib canvas has no automatic redraw upon update
            return [im]
        animation = FuncAnimation(self.canvasframe.fig, animate, frames=totalframes, interval=350, repeat=False, fargs=[automaton], blit=True)  # fargs is additional arguments

        return animation

# begin the app when running
customtkinter.set_appearance_mode("dark")
app = App()
app.mainloop()