This is a procedural map generator, using a user-friendly GUI for customisation.
It employs 3 algorithms commonly used in computer graphics and game development:
- Cellular automaton
- OpenSimplex noise
- Perlin noise

## How do these algorithms create a terrain?

Cellular automata are discrete models of computation that create some beautiful iterative structures.
Generally, they require some grid of cells, where each cell has a neighbourhood consisting of the cells surrounding it.
Each cell is assigned a state, and starts where $t=0$ at generation 1.
According to a fixed rule, a new generation is created and all the states are updated.
This cellular automaton uses a noise grid consisting of randomly assigned 0s and 1s, and checks each cell's Moore neighbourhood (all cells surrounding it) and decides whether to change its state. The automaton runs for the amount of iterations input by the user.

Perlin noise is a type of gradient noise, whereas the automaton used value noise. It's a complex algorithm that uses a random grid of 2D vectors and computes dot products between the offset vectors and random gradient vectors in each cell for all 4 vertices at a grid point (assuming in 2 dimensions). The noise grid is then interpolated. The two important settings that can be customised are:
- Frequency 
- Amplitude

A higher frequency means the function repeats more often and creates more detailed fractal noise, while a lower frequency gives broader zoomed in features
Amplitude controls the intensity of these features, creating taller "peaks" and deeper "valleys", just like how a higher amplitude of a wave has higher peaks and troughs.

OpenSimplex noise developed as an improvement to the original Perlin noise. It features a lower computational complexity at $O(n^2)$ for $n$ dimensions compared to Perlin noise's $O(n^{2^n})$ by using an improved method of splitting spaces into $n$-dimensional triangles. In 2D, this would mean it operates on 3 vertices instead of 4 too. It also features less artifacts 

For all 3 algorithms, the entire 2D array is modified. This creates a terrain that looks unrealistic as its like a repeating fractal pattern. To create an island, a gradient is applied externally by multiplying the terrain map with a circular or square gradient array of the same size, which is strongest in the middle and gets gradually weaker. 

The time of running the algorithms grows quadratically with the size of the array. Applying noise to a 512 x 512 array takes 4 times longer than to a 256 x 256 array. The algorithms are already complex, so leaving the size at 256 x 256 is recommended from tests.

## The code structure

The two main libraries for display purposes are CustomTkinter and Matplotlib. CustomTkinter provides a sleeker, modern GUI framework with many useful widgets like sliders and switches for settings. Matplotlib provides the Tkinter canvas, and the figure for which a noise map can be brought to life. It provides a variety of different colourmap styles, and interpolation to make the maps look cleaner and smoother. NumPy is also very useful for all things to do with arrays.

`main.py` builds the GUI and contains all the customisation controls, and the functions that draw and manipulate the canvas where the map will be placed. All the frames are instantiated from their own classes. The `NoiseSettings` frame can be customised to change the start and end points of frequency and amplitude, and also fractaliser, which is similar to frequency but just multiplies each coordinate by the amount to reduce the input so the noise pattern is over a smaller part of the gradient grid. The `MainFrame` contains the dimensions controls and plot button and is where `NoiseSettings` are embedded. The `CanvasFrame` uses the Matplotlib canvas integrated into CustomTkinter to display the noise array. I tried to use best object-oriented practice, such as by passing around functions to the frames to keep encapsulation.

The `plot` button draws from `helpers.py` which contains the backend functions to generate the terrain map. You can instantiate a `NoiseGenerator` object for the OpenSimplex and Perlin noise which can be used on an empty 2D array by accessing its methods. For the cellular automaton, an animation of each iteration is created using Matplotlib's `FuncAnimation` feature which draws each iteration in set intervals. The map or animation is then saved in its appropriate format as `.png` or `.gif`, such as `perlin1.png`, `perlin2.png` etc. The incrementing number is done using regular expressions in `filename.py`. 

The colours used by the `plotmap` function for the OpenSimplex and Perlin noise are stored in a dictionary associating features of terrain like grass or mountain with RGB or hexadecimal colour. The colours are set at specific intervals between 0-1, and each array is thus defined a colour using Matplotlib's colormap features. These ranges can be modified to increase the amount of a feature appearing. For example, any values falling between 0.61-0.65 being set as "darkforest" colour could be changed to increase the amount of "darkforest" by changing this range to 0.54-0.67.