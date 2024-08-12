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


colors = {
    "grass": '#7b9c50',
    "water": '#0952c7',
    "deepocean": '#003eaf',
    "dirt": [114,98,49],
    "sand": '#c2b282',
    "wetsand": '#a49661',
    "darkforest": '#3c6216',
    "verydarkforest": [40,77,0],
    "forest": [85,122,45],
    "mountain": [140,142,123],
    "highmountain": [160,162,143],
    "snow": "white"
}


def plot():
    map_height = int(dimensions_slider.get())
    map_width = int(dimensions_slider.get())
    map = np.empty((map_width, map_height), dtype=float)
    option = combobox.get()
    if option == 'Basic cellular automaton':
        iterations = int(iterations_slider.get())
        density = int(density_slider.get())
        ca = CellularAutomaton(map, density, map_width, map_height, islandchoice.get())
        grid = ca.noise_grid()
        animation = createanimation(ca, iterations, map_width, map_height)

        newfilename = next_filename("map", ".gif")
        animation.save(filename=f"Saved/{newfilename}", writer="pillow")

    elif option == 'OpenSimplex noise':
        freq = freq_slider.get()
        amp = amp_slider.get()
        fractalLevel = fractaliser.get()
        config = NoiseConfig(freq, amp, 2, 0.5, fractalLevel)
        emptymap = NoiseGenerator(map, map_width, map_height, config, islandchoice.get())
        island = emptymap.opensimplex()
        plotmap(island)
        newfilename = next_filename("simplex", ".png")
        fig.savefig(f"Saved/{newfilename}", bbox_inches="tight")
    
    elif option == 'Perlin noise':
        freq = freq_slider_perlin.get()
        amp = amp_slider_perlin.get()
        config = NoiseConfig(freq, amp, 2, 0.5, fractalLevel)
        emptymap = NoiseGenerator(map, map_width, map_height, config, islandchoice.get())
        island = emptymap.perlinnoise2()
        plotmap(island)
        newfilename = next_filename("perlin", ".png")
        fig.savefig(f"Saved/{newfilename}", bbox_inches="tight")

    
def plotmap(grid):

    axes.set_axis_off()

    colours = [(0, colors["deepocean"]), 
               (0.37, colors["water"]), 
               (0.46,colors["sand"]), 
               (0.47, colors["wetsand"]), 
               (0.56, colors["grass"]), 
               (0.65,colors["darkforest"]),
                (0.80,'darkgray'), 
                (0.85,'lightgray'), 
                (1,'white')]
    colourmap = LinearSegmentedColormap.from_list('colourmap',colours, 256)
    #colourmap = colourmap(np.array([0, 0.5,0.53,0.56,0.7,0.73,0.87,1]))
    axes.imshow(grid, cmap=colourmap, interpolation="bilinear") 
    canvas.draw()

def openimages():
    path = r"Saved"
    os.startfile(path)
################ CELLULAR AUTOMATON #######################
 
#automaton is an object plotting. It contains the actual map, methods to generate the value noise grid, and apply the cellular automaton
def createanimation(automaton, totalframes):

    cmap = ListedColormap(["lawngreen","royalblue"])
    #fig.colorbar(plt.cm.ScalarMappable(cmap=cmap), label='Colours', shrink=0.5, ax=axes)
    im = axes.imshow(automaton.map, cmap=cmap)
    def animate(i, automaton):

        map = automaton.cellular_automaton()
        im.set_array(map)
        canvas.draw()   #UPDATE CANVAS PER ANIMATION WITHIN EVENT LOOP. matplotlib canvas has no automatic redraw upon update
        return [im]
    animation = FuncAnimation(fig, animate, frames=totalframes, interval=200, repeat=False, fargs=[automaton], blit=True)

    return animation



############################INITIALISE CTK WINDOW##############################################
customtkinter.set_appearance_mode("dark")

window = customtkinter.CTk()
window.title('Procedural map generator')
window.geometry("1025x600")
window.resizable(0, 0)

# Canvas frame
rightframe = customtkinter.CTkFrame(master=window, bg_color="red")
rightframe.grid(row=0,column=1,padx=15,pady=15, sticky="nsew")
rightframe.grid_rowconfigure(0, weight=1)
rightframe.grid_columnconfigure((0, 1), weight=1)

fig = Figure(figsize=(7,7))
axes = fig.add_subplot(111)
axes.set_axis_off()

canvas = FigureCanvasTkAgg(fig, master=rightframe)
canvas.draw()

canvas.get_tk_widget().grid(row=0, column=0)


# All settings and execute buttons
leftframe = customtkinter.CTkFrame(master=window)
leftframe.grid(row=0,column=0,padx=15,pady=15, sticky="ew")

icon = customtkinter.CTkImage(Image.open("icon.png"), size=(50,50))
opendir_button = customtkinter.CTkButton(master=leftframe, width=50, height=50, image=icon, text="", fg_color='transparent', hover_color="#2B2B2B", command=openimages)
opendir_button.grid(row=0, column=0, sticky="w")
plot_button = customtkinter.CTkButton(master=leftframe, text="Plot", width=200, command=plot, height=50, border_color="aqua", border_width = 2)
plot_button.grid(row=0, column=0, pady=5)

############ UPDATING SLIDERS #################
def slider_value(val, label):
    label.configure(text=f"Value: {val:.3f}")
########## map height x width settings ############
dimensions_label = customtkinter.CTkLabel(master=leftframe, text="Map dimensions", pady = 5, font=('Helvetica',13,'bold'))
dimensions_label.grid(row=1, column=0)

dimensions_slider = customtkinter.CTkSlider(master=leftframe, from_=128, to=2048, number_of_steps=15, command=lambda val:slider_value(val, dimension_value))
dimensions_slider.grid(row=2, column=0)
dimensions_slider.set(256)

dimension_value = customtkinter.CTkLabel(master=leftframe, text="Value: 256")
dimension_value.grid(row=3, column=0)


###### handling option selections ##########
def combobox_callback(choice):
    print("combobox dropdown clicked:", choice)
    framelist[choice].tkraise()

combobox_var = customtkinter.StringVar(value="Algorithm")
combobox = customtkinter.CTkComboBox(leftframe, values=["Basic cellular automaton", "OpenSimplex noise", "Perlin noise"],
                                     command=combobox_callback, variable=combobox_var, width=300, justify='center')
combobox_var.set("Algorithm")
combobox.grid(row=4, column=0,pady=40)

islandchoice = customtkinter.CTkSwitch(leftframe, text="Generate island")
islandchoice.grid(row=6, column=0, columnspan=2, pady=10)
##############################################################################
framelist = {}
settings_frame = customtkinter.CTkFrame(master=leftframe, width=350, height=400)

##### cellular automaton settings sliders ##########
ca_frame = customtkinter.CTkFrame(master=leftframe, width=350, height=400)
framelist['Basic cellular automaton'] = ca_frame
iterations_label = customtkinter.CTkLabel(ca_frame, text="Iterations")
iterations_slider = customtkinter.CTkSlider(ca_frame, from_=1, to=20, number_of_steps=19, command=lambda val:slider_value(val, iterations_value))
iterations_value = customtkinter.CTkLabel(ca_frame, text="Value: ")
density_label = customtkinter.CTkLabel(ca_frame, text="Density")
density_slider = customtkinter.CTkSlider(ca_frame, from_=0, to=100, number_of_steps=100, command=lambda val:slider_value(val, density_value))
density_value = customtkinter.CTkLabel(ca_frame, text="Value: ")

iterations_label.grid(row=0)
iterations_slider.grid(row=1,column=0)
iterations_value.grid(row=2, column=0)
density_label.grid(row=0, column=1)
density_slider.grid(row=1, column=1)
density_value.grid(row=2, column=1)

######## simplex noise sttings ################
simplexframe = customtkinter.CTkFrame(master=leftframe, width=350, height=400)
framelist['OpenSimplex noise'] = simplexframe
freq_label = customtkinter.CTkLabel(simplexframe, text="Frequency")
freq_label.grid(row=0, column=0)
freq_slider = customtkinter.CTkSlider(simplexframe, from_=0.005, to= 0.05, number_of_steps=9, command=lambda val:slider_value(val, freq_value))
freq_slider.grid(row=1, column=0)
freq_value = customtkinter.CTkLabel(simplexframe, text="Value: ")
freq_value.grid(row=2, column=0)
amp_label = customtkinter.CTkLabel(simplexframe, text="Amplitude")
amp_label.grid(row=0, column=1)
amp_slider = customtkinter.CTkSlider(simplexframe, from_=32, to=256, number_of_steps=7, command=lambda val:slider_value(val, amp_value))
amp_slider.grid(row=1, column=1)
amp_value = customtkinter.CTkLabel(simplexframe, text="Value: ")
amp_value.grid(row=2, column=1)
fractaliser_label = customtkinter.CTkLabel(simplexframe, text="Fractaliser")
fractaliser_label.grid(row=3, column=0, columnspan=2)
fractaliser = customtkinter.CTkSlider(simplexframe, from_=0.5, to=1.5, number_of_steps=4, command=lambda val:slider_value(val, fractaliser_value))
fractaliser.set(1.00)
fractaliser.grid(row=4, column=0, columnspan=2)
fractaliser_value = customtkinter.CTkLabel(simplexframe, text="Level: ")
fractaliser_value.grid(row=5, column=0, columnspan=2)
t1=CTkToolTip(fractaliser, message="How chaotic should it be? Low is less chaotic to high is more chaotic. The default is probably best", delay=0, follow=False)


######################perlin noise###############################
perlinframe = customtkinter.CTkFrame(master=leftframe, width=350, height=400)
framelist['Perlin noise'] = perlinframe
freq_label_perlin = customtkinter.CTkLabel(perlinframe, text="Frequency")
freq_label_perlin.grid(row=0, column=0)
freq_slider_perlin = customtkinter.CTkSlider(perlinframe, from_=0.005, to= 0.05, number_of_steps=9, command=lambda val:slider_value(val, freq_value_perlin))
freq_slider_perlin.grid(row=1, column=0)
freq_value_perlin = customtkinter.CTkLabel(perlinframe, text="Value: ")
freq_value_perlin.grid(row=2, column=0)
amp_label_perlin = customtkinter.CTkLabel(perlinframe, text="Amplitude")
amp_label_perlin.grid(row=0, column=1)
amp_slider_perlin = customtkinter.CTkSlider(perlinframe, from_=32, to=256, number_of_steps=7, command=lambda val:slider_value(val, amp_value_perlin))
amp_slider_perlin.grid(row=1, column=1)
amp_value_perlin = customtkinter.CTkLabel(perlinframe, text="Value: ")
amp_value_perlin.grid(row=2, column=1)
fractaliser_label_perlin = customtkinter.CTkLabel(perlinframe, text="Fractaliser")
fractaliser_label_perlin.grid(row=3, column=0, columnspan=2)
fractaliser_perlin = customtkinter.CTkSlider(perlinframe, from_=0.1, to=0.6, number_of_steps=10, command=lambda val:slider_value(val, fractaliser_value_perlin))
fractaliser_perlin.set(0.25)
fractaliser_perlin.grid(row=4, column=0, columnspan=2)
fractaliser_value_perlin = customtkinter.CTkLabel(perlinframe, text="Level: ")
fractaliser_value_perlin.grid(row=5, column=0, columnspan=2)
t2=CTkToolTip(fractaliser_label_perlin, message="How chaotic should it be? Low is less chaotic to high is more chaotic. The default is probably best", delay=0)

###### Stack all settings frames on top of each other ##############
for frames in framelist.values():
    frames.grid(row=5, column=0, sticky='nsew')
####################

window.mainloop()

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()


        self.title('Procedural map generator')
        self.geometry("1025x600")
        self.resizable(0, 0)

        # Canvas frame
        self.rightframe = customtkinter.CTkFrame(master=self)
        self.rightframe.grid(row=0,column=1,padx=15,pady=15, sticky="nsew")
        self.rightframe.grid_rowconfigure(0, weight=1)
        self.rightframe.grid_columnconfigure((0, 1), weight=1)

        self.fig = Figure(figsize=(7,7))
        self.axes = self.fig.add_subplot(111)
        self.axes.set_axis_off()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.rightframe)
        self.canvas.draw()

        self.canvas.get_tk_widget().grid(row=0, column=0)

        # All settings and execute buttons
        self.leftframe = customtkinter.CTkFrame(master=self)
        self.leftframe.grid(row=0,column=0,padx=15,pady=15, sticky="ew")

        self.icon = customtkinter.CTkImage(Image.open("icon.png"), size=(50,50))
        self.opendir_button = customtkinter.CTkButton(master=self.leftframe, width=50, height=50, image=self.icon, text="", fg_color='transparent', hover_color="#2B2B2B", command=self.openimages)
        self.opendir_button.grid(row=0, column=0, sticky="w")
        self.plot_button = customtkinter.CTkButton(master=self.leftframe, text="Plot", width=200, command=self.plot, height=50, border_color="aqua", border_width = 2)
        self.plot_button.grid(row=0, column=0, pady=5)

        self.dimensions_label = customtkinter.CTkLabel(master=self.leftframe, text="Map dimensions", pady = 5, font=('Helvetica',13,'bold'))
        self.dimensions_label.grid(row=1, column=0)

        self.dimensions_slider = customtkinter.CTkSlider(master=self.leftframe, from_=128, to=2048, number_of_steps=15, command=lambda val:self.slider_value(val, self.dimension_value))
        self.dimensions_slider.grid(row=2, column=0)
        self.dimensions_slider.set(256)

        self.dimension_value = customtkinter.CTkLabel(master=self.leftframe, text="Value: 256")
        self.dimension_value.grid(row=3, column=0)

        self.combobox_var = customtkinter.StringVar(value="Algorithm")
        self.combobox = customtkinter.CTkComboBox(self.leftframe, values=["Basic cellular automaton", "OpenSimplex noise", "Perlin noise"],
                                            command=self.combobox_callback, variable=self.combobox_var, width=300, justify='center')
        self.combobox_var.set("Algorithm")
        self.combobox.grid(row=4, column=0,pady=40)

        self.islandchoice = customtkinter.CTkSwitch(self.leftframe, text="Generate island")
        self.islandchoice.grid(row=6, column=0, columnspan=2, pady=10)

        ##### framelist containing all settings frames ###############
        self.framelist = {}
        self.settings_frame = customtkinter.CTkFrame(master=self.leftframe, width=350, height=400)

        ##### cellular automaton settings sliders ##########
        self.ca_frame = customtkinter.CTkFrame(master=self.leftframe, width=350, height=400)
        self.framelist['Basic cellular automaton'] = self.ca_frame
        self.iterations_label = customtkinter.CTkLabel(self.ca_frame, text="Iterations")
        self.iterations_slider = customtkinter.CTkSlider(self.ca_frame, from_=1, to=20, number_of_steps=19, command=lambda val:self.slider_value(val, self.iterations_value))
        self.iterations_value = customtkinter.CTkLabel(self.ca_frame, text="Value: ")
        self.density_label = customtkinter.CTkLabel(self.ca_frame, text="Density")
        self.density_slider = customtkinter.CTkSlider(self.ca_frame, from_=0, to=100, number_of_steps=100, command=lambda val:self.slider_value(val, self.density_value))
        self.density_value = customtkinter.CTkLabel(self.ca_frame, text="Value: ")

        self.iterations_label.grid(row=0)
        self.iterations_slider.grid(row=1,column=0)
        self.iterations_value.grid(row=2, column=0)
        self.density_label.grid(row=0, column=1)
        self.density_slider.grid(row=1, column=1)
        self.density_value.grid(row=2, column=1)

        ######## simplex noise sttings ################
        self.simplexframe = customtkinter.CTkFrame(master=self.leftframe, width=350, height=400)
        self.framelist['OpenSimplex noise'] = self.simplexframe
        self.freq_label = customtkinter.CTkLabel(self.simplexframe, text="Frequency")
        self.freq_label.grid(row=0, column=0)
        self.freq_slider = customtkinter.CTkSlider(self.simplexframe, from_=0.005, to= 0.05, number_of_steps=9, command=lambda val:self.slider_value(val, self.freq_value))
        self.freq_slider.grid(row=1, column=0)
        self.freq_value = customtkinter.CTkLabel(self.simplexframe, text="Value: ")
        self.freq_value.grid(row=2, column=0)
        self.amp_label = customtkinter.CTkLabel(self.simplexframe, text="Amplitude")
        self.amp_label.grid(row=0, column=1)
        self.amp_slider = customtkinter.CTkSlider(self.simplexframe, from_=32, to=256, number_of_steps=7, command=lambda val:self.slider_value(val, self.amp_value))
        self.amp_slider.grid(row=1, column=1)
        self.amp_value = customtkinter.CTkLabel(self.simplexframe, text="Value: ")
        self.amp_value.grid(row=2, column=1)
        self.fractaliser_label = customtkinter.CTkLabel(self.simplexframe, text="Fractaliser")
        self.fractaliser_label.grid(row=3, column=0, columnspan=2)
        self.fractaliser = customtkinter.CTkSlider(self.simplexframe, from_=0.5, to=1.5, number_of_steps=4, command=lambda val:self.slider_value(val, self.fractaliser_value))
        self.fractaliser.set(1.00)
        self.fractaliser.grid(row=4, column=0, columnspan=2)
        self.fractaliser_value = customtkinter.CTkLabel(self.simplexframe, text="Level: ")
        self.fractaliser_value.grid(row=5, column=0, columnspan=2)
        self.t1=CTkToolTip(self.fractaliser, message="How chaotic should it be? Low is less chaotic to high is more chaotic. The default is probably best", delay=0, follow=False)


        ######################perlin noise###############################
        self.perlinframe = customtkinter.CTkFrame(master=self.leftframe, width=350, height=400)
        self.framelist['Perlin noise'] = self.perlinframe
        self.freq_label_perlin = customtkinter.CTkLabel(self.perlinframe, text="Frequency")
        self.freq_label_perlin.grid(row=0, column=0)
        self.freq_slider_perlin = customtkinter.CTkSlider(self.perlinframe, from_=0.005, to= 0.05, number_of_steps=9, command=lambda val:self.slider_value(val, self.freq_value_perlin))
        self.freq_slider_perlin.grid(row=1, column=0)
        self.freq_value_perlin = customtkinter.CTkLabel(self.perlinframe, text="Value: ")
        self.freq_value_perlin.grid(row=2, column=0)
        self.amp_label_perlin = customtkinter.CTkLabel(self.perlinframe, text="Amplitude")
        self.amp_label_perlin.grid(row=0, column=1)
        self.amp_slider_perlin = customtkinter.CTkSlider(self.perlinframe, from_=32, to=256, number_of_steps=7, command=lambda val:self.slider_value(val, self.amp_value_perlin))
        self.amp_slider_perlin.grid(row=1, column=1)
        self.amp_value_perlin = customtkinter.CTkLabel(self.perlinframe, text="Value: ")
        self.amp_value_perlin.grid(row=2, column=1)
        self.fractaliser_label_perlin = customtkinter.CTkLabel(self.perlinframe, text="Fractaliser")
        self.fractaliser_label_perlin.grid(row=3, column=0, columnspan=2)
        self.fractaliser_perlin = customtkinter.CTkSlider(self.perlinframe, from_=0.1, to=0.6, number_of_steps=10, command=lambda val:self.slider_value(val, self.fractaliser_value_perlin))
        self.fractaliser_perlin.set(0.25)
        self.fractaliser_perlin.grid(row=4, column=0, columnspan=2)
        self.fractaliser_value_perlin = customtkinter.CTkLabel(self.perlinframe, text="Level: ")
        self.fractaliser_value_perlin.grid(row=5, column=0, columnspan=2)
        self.t2=CTkToolTip(self.fractaliser_label_perlin, message="How chaotic should it be? Low is less chaotic to high is more chaotic. The default is probably best", delay=0)

        for frames in self.framelist.values():
            frames.grid(row=5, column=0, sticky='nsew')

    ############ UPDATING SLIDERS #################
    def slider_value(self, val, label):
        label.configure(text=f"Value: {val:.3f}")

    
    def combobox_callback(self, choice):
        print("combobox dropdown clicked:", choice)
        self.framelist[choice].tkraise()

    
    def plot(self):
        map_height = int(self.dimensions_slider.get())
        map_width = int(self.dimensions_slider.get())
        map = np.empty((map_width, map_height), dtype=float)
        option = self.combobox.get()
        if option == 'Basic cellular automaton':
            iterations = int(self.iterations_slider.get())
            density = int(self.density_slider.get())
            #create cellular automaton object with empty map primed up
            ca = CellularAutomaton(map, density, map_width, map_height, self.islandchoice.get())
            grid = ca.noise_grid()  # modify object to have value noise grid (grid is unused variable)
            animation = self.createanimation(ca, iterations, map_width, map_height)

            newfilename = next_filename("map", ".gif")
            animation.save(filename=f"Saved/{newfilename}", writer="pillow")

        elif option == 'OpenSimplex noise':
            freq = self.freq_slider.get()
            amp = self.amp_slider.get()
            fractalLevel = self.fractaliser.get()
            config = NoiseConfig(freq, amp, 2, 0.5, fractalLevel)
            emptymap = NoiseGenerator(map, map_width, map_height, config, self.islandchoice.get())
            island = emptymap.opensimplex()
            self.plotmap(island)
            newfilename = next_filename("simplex", ".png")
            self.fig.savefig(f"Saved/{newfilename}", bbox_inches="tight")
        
        elif option == 'Perlin noise':
            freq = self.freq_slider_perlin.get()
            amp = self.amp_slider_perlin.get()
            fractalLevel = self.fractaliser_perlin.get()
            config = NoiseConfig(freq, amp, 2, 0.5, fractalLevel)
            emptymap = NoiseGenerator(map, map_width, map_height, config, self.islandchoice.get())
            island = emptymap.perlinnoise2()
            self.plotmap(island)
            newfilename = next_filename("perlin", ".png")
            self.fig.savefig(f"Saved/{newfilename}", bbox_inches="tight")

        
    def plotmap(self, grid):

        self.axes.set_axis_off()

        colours = [(0, colors["deepocean"]), 
                (0.37, colors["water"]), 
                (0.46,colors["sand"]), 
                (0.47, colors["wetsand"]), 
                (0.56, colors["grass"]), 
                (0.65,colors["darkforest"]),
                (0.80,'darkgray'), 
                (0.85,'lightgray'), 
                (1,'white')]
        colourmap = LinearSegmentedColormap.from_list('colourmap',colours, 256)
        #colourmap = colourmap(np.array([0, 0.5,0.53,0.56,0.7,0.73,0.87,1]))
        self.axes.imshow(grid, cmap=colourmap, interpolation="bilinear") 
        self.canvas.draw()

    def openimages(self):
        path = r"Saved"
        os.startfile(path)
    ################ CELLULAR AUTOMATON #######################
    
    #automaton is an object plotting. It contains the actual map, methods to generate the value noise grid, and apply the cellular automaton
    def createanimation(self, automaton, totalframes):

        cmap = ListedColormap(["lawngreen","royalblue"])
        #fig.colorbar(plt.cm.ScalarMappable(cmap=cmap), label='Colours', shrink=0.5, ax=axes)
        im = self.axes.imshow(automaton.map, cmap=cmap)
        def animate(i, automaton):

            map = automaton.cellular_automaton()
            im.set_array(map)
            self.canvas.draw()   #UPDATE CANVAS PER ANIMATION WITHIN EVENT LOOP. matplotlib canvas has no automatic redraw upon update
            return [im]
        animation = FuncAnimation(self.fig, animate, frames=totalframes, interval=200, repeat=False, fargs=[automaton], blit=True)

        return animation

customtkinter.set_appearance_mode("dark")
app = App()
app.mainloop()