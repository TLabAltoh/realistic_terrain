import bpy
import random
import math
import numpy as np

######################################################################
# methods
######################################################################

# =============================
# delete all object
# =============================

def delete_all_objects():
    
    """ delate all objects exist in the scene. """
    
    # the behavior of the two codes is the same.
    for col in bpy.data.collections:
        for item in col.objects:
            col.objects.unlink(item)
            bpy.data.objects.remove(item)
            
    """
    for item in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(item)
        bpy.data.objects.remove(item)
    """
    
    """ delete all meshe and material data. """
    
    # delete all data.meshes.
    for item in bpy.data.meshes:
        bpy.data.meshes.remove(item)

    # delete all data.materials.
    for item in bpy.data.materials:
        bpy.data.materials.remove(item)


# ===================================
# create perlin nosie map
# ===================================

# liner interpolation.
def fade(t):return 6*t**5-15*t**4+10*t**3
def lerp(a,b,t):return a+fade(t)*(b-a)

def perlin(r,seed=np.random.randint(0,100)):
    np.random.seed(seed)

    # integer part use as index.
    ri = np.floor(r).astype(int)
    
    # make sure the minimum value is 0.
    ri[0] -= ri[0].min()
    ri[1] -= ri[1].min()
    
    # decimal part. this value is used as a complementary value.
    rf = np.array(r) % 1
    
    # create grid points and set gradient.
    # conversion 0, 1 to -1, 1.
    # the larger the map, the better the number of grids.
    # 2 columns (ri[0].max()+2) * (ri[1].max()+2) set.
    g = 2 * np.random.rand(ri[0].max()+2,ri[1].max()+2,2) - 1
    
    # four corners.
    # 4 dimention array.
    e = np.array([[[[0,0], [0,1], [1,0], [1,1]]]])
    
    # distance vector with each point of the four corners.
    # 3 dimention array to 5 dimention array.
    # 1 row 2 columns r.shape[1] * r.shape[2] * 4 set.
    er = (np.array([rf]).transpose(2,3,0,1) - e).reshape(r.shape[1],r.shape[2],4,1,2)
    
    # gradient of each grad.
    # switch row and columns.
    # 2 row 1 columns r.shape[1] * r.shape[2] * 4 set.
    gr = np.r_["3,4,0",g[ri[0],ri[1]],g[ri[0],ri[1]+1],g[ri[0]+1,ri[1]],g[ri[0]+1,ri[1]+1]].transpose(0,1,3,2).reshape(r.shape[1],r.shape[2],4,2,1)
    
    # calculate the inner product of er and gr.
    # @ is an operator that calculate the inner product of a mtrix defined by numpy.
    p = (er@gr).reshape(r.shape[1],r.shape[2],4).transpose(2,0,1)

    # lerp and return.
    # -1 to 1 --> 0 to 1
    return lerp(lerp(p[0],p[2],rf[0]),lerp(p[1],p[3],rf[0]),rf[1])


def create_perlin_noise(N, maxDetail, maxHeight):
    
    # obviously useless code, but this is finr.
    # calculate the power of 2 for maxDetail.
    maxPower = 0
    while(maxDetail != 1):
        maxDetail = maxDetail / 2
        maxPower += 1
        
    # N * N array all value is 0.
    y = np.zeros((N,N))

    # perlin noise is sampled at several frequencies and superimposed.
    for power in range(0,maxPower):
        frequency = 2**power
        amp = 1 / frequency
        
        # arithmetic progression of the range 0 to frequency into N.
        x = np.linspace(0,frequency,N)
    
        # r is array that (2, N, N).
        r = np.array(np.meshgrid(x,x))
        y += perlin(r) * amp
    
    # return inverse lerp value multiplyed amplitude.
    return (y  - y.min()) / (y.max() - y.min()) * maxHeight



# =======================================
# calculate hydraulic erosion
# =======================================

class heightAndGradient:
    
    height = None
    gradientX = None
    gradientY = None

    # constructor
    def __init__(self,height, gradientX, gradientY):
        self.height = height
        self.gradientX = gradientX
        self.gradientY = gradientY

# calculate gradient and height as NW's value.
def CalculateHeightAndGradient(perlin_map, posX, posY):
    
    # find the coordinates by turncating a decimal.
    coordX = np.floor(posX).astype(int)
    coordY = np.floor(posY).astype(int)
    # make the fractinal part a complementary value.  
    x = posX % 1
    y = posY % 1
    
    # (0,1)
    heightNW = perlin_map[coordX][coordY+1]
    # (1,1)
    heightNE = perlin_map[coordX+1][coordY+1]
    # (0,0)
    heightSW = perlin_map[coordX][coordY]
    # (1,0)
    heightSE = perlin_map[coordX+1][coordY]
    
    gradientX = (heightSW - heightSE) * (1 - y) + (heightNW - heightNE) * y
    gradientY = (heightSW - heightNW) * (1 - x) + (heightSE - heightNE) * x
    
    # complement four values as NW's value.
    height = heightNW * (1 - x) * y + heightNE * x * y + heightSW * (1 - x) * (1 - y) + heightSE * x * (1 - y)
    
    return heightAndGradient(height,gradientX,gradientY)


# befour cutting a mountain, preset a map of which coordinates to cut at what ratio for all coordinates.
# array is reference type, so arguments are passed by reference.
def initialize_brush_indices(radius,mapSize,erosionBrushIndices,erosionBrushWeights,seed=np.random.randint(0,100)):
    
    # prepare for 4 quadrents.
    xOffsets = np.zeros((radius*radius*4))
    yOffsets = np.zeros((radius*radius*4))
    
    weights = np.zeros((radius*radius*4))
    weightSum = 0
    addIndex = 0
    
    np.random.seed(seed)
    
    for i in range(0,mapSize):
        for j in range(0,mapSize):
                 
            centerX = i
            centerY = j
             
            # if the range circle is off the map,
            # determines if the specified coordinates are with in the map range.
            # if conditional expression is false, you dont need to calculate because you can use the previous result. 
            # what is worng ?
            if (centerY <= radius or centerY >= mapSize - radius or centerX <= radius + 1 or centerX >= mapSize - radius):    
                weightSum = 0
                addIndex = 0
                    
                for x in range(-radius,radius):
                    for y in range(-radius,radius):    
                        sqrDst = x*x+y*y
                        # if the distance is within a range circle...
                        if(sqrDst < radius*radius):
                            coordX = centerX+x
                            coordY = centerY+y
                            # and coordinate is within a map, set calculate weight.
                            if(coordX>=0 and coordX<mapSize and coordY>=0 and coordY<mapSize):                                
                                # The farther from the center, the smaller the weight.
                                weight = 1 - math.sqrt(sqrDst) / radius
                                
                                weightSum += weight
                                weights[addIndex] = weight
                                xOffsets[addIndex] = x
                                yOffsets[addIndex] = y
                                addIndex += 1

            numEntries = addIndex
            
            # add the 3rd dimention in the 2nd dimention.
            # because verts is 1st dimention array. append 1 dimention value.
            for k in range(0,numEntries):
                # cast to int.
                erosionBrushIndices[i][j].insert(k,[int(centerX + xOffsets[k]),int(centerY + yOffsets[k])])
                # make it 1 in total.
                erosionBrushWeights[i][j].insert(k,weights[k] / weightSum);

                
# simulate the accumulation and erosion of flowing water. 
def erode(perlinNoiseMap,mapSize,radius):
    
    # create list array's mapSize * mapSize array.
    erosionBrushIndices = [[ [] for i in range(mapSize)] for j in range(mapSize)]
    erosionBrushWeights = [[ [] for i in range(mapSize)] for j in range(mapSize)]
    initialize_brush_indices(radius,mapSize,erosionBrushIndices,erosionBrushWeights)
    
    # number of rain drops.
    numIteration = 100000
    
    # simulate each rain drops.
    for iteration in range(0,numIteration):
        
        posX = random.uniform(0,mapSize-1)
        posY = random.uniform(0,mapSize-1)
        dirX = 0
        dirY = 0
        inertia = 0.05
        
        # the smaller the speed and water, the better. if both the amount to be scraped and the amount to be left
        # are smalle, no noticeable spikes will occur.
        # however, regarding the speed, if the initial velocity too slow, it will not be possible to make a branch
        # pattern on the top of the mountain. so i will put it in 5th place.
        
        # speed = 5
        speed = 5
        gravity = 4
        
        # water = 1
        water = 1
        evaporateSpeed = 0.01
        
        sediment = 0
        # Used to prevent carry capacity getting too close to zero on flatter terrain.
        minSedimentCapacity = 0.01
        sedimentCapacityFactor = 4

        depositSpeed = 0.3
        erodeSpeed = 0.3
        
        # lifeTime of rain drops.
        maxDropletLifeTime = 30
        
        # while the raindrops are alive.
        for lifeTime in range(0,maxDropletLifeTime):
            # find closest vertex.
            nodeX = np.floor(posX).astype(int)
            nodeY = np.floor(posY).astype(int)            
            
            cellOffsetX = posX % 1
            cellOffsetY = posY % 1

            # calculate the gradient at the coordinate.
            heightAndGradient = CalculateHeightAndGradient(perlinNoiseMap, posX, posY)
            # guess the direction of raindrops by complementing.
            dirX = dirX * inertia + heightAndGradient.gradientX * (1 - inertia)
            dirY = dirY * inertia + heightAndGradient.gradientY * (1 - inertia)
            # normalize direction.
            length = math.sqrt(dirX * dirX + dirY * dirY)
            if(length != 0):
                dirX /= length
                dirY /= length
                #print([dirX, dirY])
            else:
                print("prevent error : length == 0!")
                
            # update raindrop position.
            posX += dirX
            posY += dirY
            
            # Stop simulating droplet if gradient is 0 or has flowed over edge of map.
            if ((dirX == 0 and dirY == 0) or posX < 0 or posX >= mapSize - 1 or posY < 0 or posY >= mapSize - 1):break
            
            # Find the droplet's new height and calculate the deltaHeight
            newHeight = CalculateHeightAndGradient (perlinNoiseMap, posX, posY).height
            # lager than 0 --> uphill. lower than 0 --> downhill
            deltaHeight = newHeight - heightAndGradient.height
            
            # Calculate the droplet's sediment capacity (higher when moving fast down a slope and contains lots of water)
            # the amount of sediment that that the water stream can carry at this time.
            sedimentCapacity = max(-deltaHeight * speed * water * sedimentCapacityFactor, minSedimentCapacity)
            
            # which deposit or erode
            # if uphill and now seddiment lager than capacity, be sure to deposit.
            if(sediment > sedimentCapacity or deltaHeight > 0):
                # If moving uphill (deltaHeight > 0) try fill up to the current height, otherwise deposit a fraction of the excess sediment
                amountToDeposit = min(deltaHeight, sediment) if deltaHeight > 0 else (sediment - sedimentCapacity) * depositSpeed
                sediment -= amountToDeposit
                
                # Add the sediment to the four nodes of the current cell using bilinear interpolation.
                perlinNoiseMap[nodeX][nodeY] += amountToDeposit * (1 - cellOffsetX) * (1 - cellOffsetY)
                perlinNoiseMap[nodeX+1][nodeY] += amountToDeposit * cellOffsetX * (1 - cellOffsetY)
                perlinNoiseMap[nodeX][nodeY+1] += amountToDeposit * (1 - cellOffsetX) * cellOffsetY
                perlinNoiseMap[nodeX+1][nodeY+1] += amountToDeposit * cellOffsetX * cellOffsetY
                
            else:
                # note : in here deltaHeight < 0. so the -deltaHeight > 0
                # possible and limited amount of scraping.
                amountToErode = min((sedimentCapacity - sediment) * erodeSpeed, -deltaHeight)

                for brushPointIndex in range(0,len(erosionBrushIndices[nodeX][nodeY])):
                    nodeIndex = erosionBrushIndices[nodeX][nodeY][brushPointIndex]
                    weighedErodeAmount = amountToErode * erosionBrushWeights[nodeX][nodeY][brushPointIndex]
                    # print([amountToErode, erosionBrushWeights[nodeX][nodeY][brushPointIndex]])
                    
                    deltaSediment = weighedErodeAmount if perlinNoiseMap[nodeIndex[0]][nodeIndex[1]] > weighedErodeAmount else perlinNoiseMap[nodeIndex[0]][nodeIndex[1]]
                    perlinNoiseMap[nodeIndex[0]][nodeIndex[1]] -= deltaSediment
                    sediment += deltaSediment
                    
            # water speed is slow down doing erode.
            speed = math.sqrt(max(speed * speed + deltaHeight * gravity,0))
            # Water eveporates in time.
            water *= (1 - evaporateSpeed)        
                    
# =======================
# create mesh
# =======================

def create_mesh(name,map,offsetX,offsetY,scale):
    
    # define vertexs and polygons.
    verts = []
    faces = []
    
    numX = len(map[1])
    numY = len(map[0])
    # generate vertex coordinates.
    for i in range (0, numX):
        for j in range(0,numY):
            x = scale * i
            y = scale * j
            z = map[i,j]
            vert = (x,y,z) 
            verts.append(vert)

    # generate a face from four vertices.
    count = 0
    for i in range (0, numY *(numX-1)):
        if count < numY-1:
            A = i
            B = i+1
            C = (i+numY)+1
            D = (i+numY)
            face = (A,B,C,D)
            faces.append(face)
            count = count + 1
        else:
            count = 0

    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts,[],faces)
    mesh.update(calc_edges=True)

    obj = bpy.data.objects.new(name,mesh)
    obj.location = (offsetX*scale,offsetY*scale,0)
    bpy.context.scene.collection.objects.link(obj)

    """
    # adaptation subdivision surface.
    obj.modifiers.new("subd surf", type='SUBSURF')
    obj.modifiers['subd surf'].levels = 3
    """

    ""
    # adaptation smooth shade.
    mypolys = mesh.polygons
    for p in mypolys:
        p.use_smooth = True
    ""

######################################################################
# end methods
######################################################################

# mesh resolution
numX = 256
numY = 256

maxHeight = 45
# make it power of 2
maxDetail = 16
scale = 0.5
radius = 3

# delete all objects.
delete_all_objects()
# create perlin noise map.
map = create_perlin_noise(numX, maxDetail, maxHeight)

create_mesh("befor",map,-255,0,scale)

""
# simulate water drops erode and deposit.
erode(map,numX,radius)

create_mesh("after",map,0,0,scale)
""
