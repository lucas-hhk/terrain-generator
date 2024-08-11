import numpy as np
from perlin_noise import PerlinNoise
from opensimplex import noise2, seed, OpenSimplex

########################################################################
def noise_grid(grid, density, map_width, map_height, chooseisland):

    for row in range(map_width):
        for column in range(map_height):
            randomnumber = np.random.randint(0,100)
            if (randomnumber > density):
                grid[row][column] = 0 #0
            else:
                grid[row][column] = 1
    
    if chooseisland == True:
        grid = random_circle_gradient(grid, map_width, map_height)
    return grid
            
def cellular_automaton(grid, map_width, map_height): #iterate through Moore neighbourhoods
    copy = np.copy(grid)
    for row in range(map_width):
        for column in range(map_height):
            neighbour_wall_count = 0
            for j in range(row - 1, row + 2):
                for k in range(column - 1, column + 2):
                    if j < 0 or k < 0 or j > map_width - 1 or k > map_height - 1:
                        neighbour_wall_count += 1
                    elif j != row or k != column:
                        if copy[j][k] == 1:
                            neighbour_wall_count += 1
            if neighbour_wall_count > 4:
                grid[row][column] = 1
            else:
                grid[row][column] = 0
    return grid 

#removes all the outer noise
#removes 3 random small circles within the central circle in attempt to make a more realistic island
def random_circle_gradient(grid, map_width, map_height):
    centre_x = map_width / 2
    centre_y = map_height / 2
    # circle equation (x-x1)^2 + (y-y1)^2 = 900
    radius = centre_x * 0.6
    radius_squared = (radius)**2
    for x in range(map_width):
        for y in range(map_height):
            tmp = (x - centre_x)**2 + (y - centre_y)**2
            if tmp >= radius_squared:
                grid[x][y] = 1
    
    smaller_radius_squared = int((radius / 5)**2)
    for _ in range(5):
        randomcircle_x = np.random.randint(centre_x - radius, centre_x + radius)
        randomcircle_y = np.random.randint(centre_y - radius, centre_y + radius)
        for x in range(randomcircle_x - smaller_radius_squared, randomcircle_x + smaller_radius_squared):
            for y in range(randomcircle_y - smaller_radius_squared, randomcircle_y + smaller_radius_squared):
                tmp = (x - randomcircle_x)**2 + (y - randomcircle_y)**2
                if tmp <= smaller_radius_squared:
                    grid[x][y] = 1


    return grid

############### 2D MAPS ###########################
def islandgradient(currentmap, map_width, map_height):
    gradient = np.zeros_like(currentmap)
    centre_x = int(map_width / 2)
    centre_y = int(map_height / 2)
    endofgradient_x = int(map_width / 2)
    endofgradient_y = map_height / 4
    colour_change = 1 / endofgradient_x
    for i in range(endofgradient_x):
        #square gradient that gets gradually weaker from the centre
        #each iteration reduces the number to set the next ring
        gradient[centre_x - i, centre_x-i : centre_x+i+1] = 1 - (colour_change * i )
        gradient[centre_x + i, centre_x-i : centre_x+i+1] = 1 - (colour_change * i )

        gradient[centre_y-i : centre_y+i+1, centre_y + i] = 1 - (colour_change * i )
        gradient[centre_y-i : centre_y+i+1, centre_y - i] = 1 - (colour_change * i )

    normalised = (currentmap-np.min(currentmap)) / (np.max(currentmap)-np.min(currentmap)) #make opensimplex noise between 0-1, for mask to apply properly
    currentmap = normalised * gradient #take element by element multiplication
    return currentmap

def opensimplex(currentmap, frequency, amplitude, lacunarity, persistence, chooseisland, map_width, map_height, fractal_level):

    #offset values added to each octave shift the entire pattern every octave
    #this makes noise less predictable and less uniform, which is more realistic of real terrain
    #many features would be replicated in different places
    #I've tried applying a newly generated offset for every of the 10 octaves and for each coordinate, but it's too chaotic. Maybe could be added gradually
    #each octave should build on each layer of noise to create natural textures.
    offset_x = np.random.randint(-99999,99999)
    offset_y = np.random.randint(-99999,99999)
    seed = np.random.randint(0,99999)
    noise = OpenSimplex(seed=seed)
    for row in range(map_width):
        for column in range(map_height):
    
            noisevalue = 0
            r_frequency = frequency
            r_amplitude = amplitude
            #apply 10 octaves of simplex noise, doubling the frequency and halving the amplitude on each octave
            for i in range(10):
                x = row * r_frequency * fractal_level + offset_x #4000
                y = column * r_frequency * fractal_level + offset_y #5674
                noisevalue += noise.noise2(x,y) * r_amplitude
                r_frequency *= lacunarity
                r_amplitude *= persistence
            currentmap[row][column] = noisevalue

    # if you want to make it look like an island, apply this square gradient to remove outer noise.
    if chooseisland == True:
        currentmap = islandgradient(currentmap, map_width, map_height)

    return currentmap

############## PERLIN ####################################################

#https://rtouti.github.io/graphics/perlin-noise-algorithm
#Explains how adding octaves of noise, increasing frequency and decreasing amplitude on every octave gives noisy terrain (less smooth)
#octaves are multiple iterations of perlin noise in each sub rectangle
def perlinnoise2(currentmap, frequency, amplitude, lacunarity, persistence, chooseisland, map_width, map_height, fractal_level):
    noise1 = PerlinNoise(octaves=8)
    for row in range(map_width):
        for column in range(map_height):
            #multiplying by 0.25 (default of fractal_level) is necessary to achieve a satisfactory "zoom in" level
            #due to how the Perlin noise gradient grid works, you essentially feed smaller input values closer to 0
            #this reduces the FREQUENCY of noise, so you get more smoother and broader features (less like a satellite map)
            x = (row/map_width) * fractal_level
            y = (column/map_height) * fractal_level
            frequency = 4
            amplitude = 128 
            noisevalue = 0          
            for i in range(8):
                noisevalue += amplitude*noise1([x * frequency, y * frequency])
                frequency *= lacunarity
                amplitude *= persistence
            currentmap[row][column] = noisevalue

    if chooseisland == True:
        currentmap = islandgradient(currentmap, map_width, map_height)
    
    return currentmap