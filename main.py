import customtkinter
import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
import os
from tktooltip import ToolTip
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
        map = noise_grid(map, density, map_width, map_height, islandchoice.get())
        animation = createanimation(map, iterations, map_width, map_height)

        newfilename = next_filename("map", ".gif")
        animation.save(filename=f"Saved/{newfilename}", writer="pillow")

    elif option == 'OpenSimplex noise':
        freq = freq_slider.get()
        amp = amp_slider.get()
        fractalLevel = fractaliser.get()
        map = opensimplex(map, freq, amp, 2, 0.5, islandchoice.get(), map_width, map_height, fractalLevel)
        plotmap(map)
        newfilename = next_filename("simplex", ".png")
        fig.savefig(f"Saved/{newfilename}", bbox_inches="tight")
    
    elif option == 'Perlin noise':
        freq = freq_slider_perlin.get()
        amp = amp_slider_perlin.get()
        fractalLevel = fractaliser_perlin.get()
        map = perlinnoise2(map, freq, amp, 2, 0.5, islandchoice.get(), map_width, map_height, fractalLevel)
        plotmap(map)
        newfilename = next_filename("perlin", ".png")
        fig.savefig(f"Saved/{newfilename}", bbox_inches="tight")

    
def plotmap(grid):

    axes.set_axis_off()
    #cmap = ListedColormap(["lawngreen", "aquamarine"])

    colours = [(0, colors["deepocean"]), (0.37, colors["water"]), (0.46,colors["sand"]), (0.47, colors["wetsand"]), (0.56, colors["grass"]), (0.65,colors["darkforest"]),
                (0.80,'darkgray'), (0.85,'lightgray'), (1,'white')]
    colourmap = LinearSegmentedColormap.from_list('colourmap',colours, 256)
    #colourmap = colourmap(np.array([0, 0.5,0.53,0.56,0.7,0.73,0.87,1]))
    axes.imshow(grid, cmap=colourmap, interpolation="None") 
    canvas.draw()

def openimages():
    path = r"Saved"
    os.startfile(path)
################ CELLULAR AUTOMATON #######################
 

def createanimation(map, totalframes, map_width, map_height):
    #axes = fig.axes()
    #axes.set_axis_off()
    cmap = ListedColormap(["lawngreen","royalblue"])
    #fig.colorbar(plt.cm.ScalarMappable(cmap=cmap), label='Colours', shrink=0.5, ax=axes)
    im = axes.imshow(map, cmap=cmap)
    def animate(i, map, map_width, map_height):

        map = cellular_automaton(map, map_width, map_height)
        im.set_array(map)
        canvas.draw()   #UPDATE CANVAS PER ANIMATION WITHIN EVENT LOOP. matplotlib canvas has no automatic redraw upon update
        return [im]
    animation = FuncAnimation(fig, animate, frames=totalframes, interval=200, repeat=False, fargs=[map, map_width, map_height], blit=True)

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

    
def update_algorithm_change(option):
    return
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
ToolTip(fractaliser_label, msg="How chaotic should it be? Low is less chaotic to high is more chaotic. The default is probably best", delay=0, follow=False)


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
ToolTip(fractaliser_label_perlin, msg="How chaotic should it be? Low is less chaotic to high is more chaotic. The default is probably best", delay=0)

###### Stack all settings frames on top of each other ##############
for frames in framelist.values():
    frames.grid(row=5, column=0, sticky='nsew')
####################

window.mainloop()