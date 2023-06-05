import numpy as np
import pygltflib
import random
import opensimplex
import pyrender
import math


noiseMin = 0
noiseMax = 0.7
curve = 0.5
geoMin = -1
geoMax = 1
resolution = 100
spread = 1.5
step = (geoMax-geoMin )/resolution



noiseRealMax = 0
noiseRealMin = 0
noiseAboveZero = 0
noiseBelowZero = 0
noiseRange = noiseMax - noiseMin
noiseDistribution = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
normalizedDistribution = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
starsAddedAtDistribution = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
pointLimit = 100
thresholdMin = 0.5
thresholdMax = 0.5
range = thresholdMax - thresholdMin
mult = 5
points_orig = []
point_count = 0
noise = opensimplex.OpenSimplex (seed=42)

def clamp(val, minVal, maxVal):
    returnVal = max([min([val, maxVal]), minVal])
    return returnVal

def checkNoiseVal(x, y, z):
    x *= mult
    y *= mult
    z *= mult
    return noise.noise3(x, y, z)

def normaliseNoise(val, fold):
    global noiseDistribution, noiseRealMax, noiseRealMin, noiseAboveZero, noiseBelowZero

    if val > noiseRealMax:
        noiseRealMax = val
    elif val < noiseRealMin:
        noiseRealMin = val

    if val > 0:
        noiseAboveZero += 1
    elif val < 0:
        noiseBelowZero += 1

    index = 0
    if val < 0:
        index =  max(math.ceil(val*10), -10)
    elif val > 0:
        index = min(math.floor(val*10), 10)

    if fold:
        val = abs(val)

   # index = math.floor((max([min([val,1]),-1]) * 10))
    #print('val:'+str(val)+ ' index:'+str(index))
    
    normalized = (val - noiseMin)/noiseRange
    
    
    #print(str(normalized))

    #print(str(sloped*10))
    #index = math.floor(normalized*10) 
    #index = max([0, min([index, 1])])
    #print(index)
    #noiseDistribution[index] += 1
    return normalized ** curve

def shouldInclude(val):
    global normalizedDistribution

    #returnValues = [0,1,2,4,8,16,32,64,128, 256]
    returnValues = [0,0,0,0,0,0,0,0,0,32]
    #curved = ((val/10.0)**2.0)*10
    #stars = (2**curved)-1
    #normalizedDistribution[val] = 

    #starsAddedAtDistribution[math.floor(val*10)] = stars
    #noiseDistribution[math.floor(val*10)] += 1
    #print(val)
    prepIndex = min([val, 9])
    index = 9 - prepIndex
    return returnValues[index]


    #return True
    # if val > thresholdMax:
    #     return True
    # elif val < thresholdMin:
    #     return False
    
    #return False


starsCount = 0
x = geoMin
y = geoMin
z = geoMin

while x < geoMax:
    x += step
    y = geoMin

    while y < geoMax:
        y += step
        z = geoMin
        #print(str(x) + ' , ' + str(y))
        while z < geoMax:
            z += step
            noiseVal = checkNoiseVal(x, y, z)
            normalizedNoise = normaliseNoise(noiseVal, True)
            quantized = clamp(math.floor(normalizedNoise*10), 0, 9)
            noiseDistribution[quantized] += 1
            starsToAdd = shouldInclude(quantized)
            starsAddedAtDistribution[quantized] += starsToAdd

            iteration = 0
            while iteration < starsToAdd:
                point_count += 1
                randomVector = [        
                    (random.random() * 2.0) - 1.0,
                    (random.random() * 2.0) - 1.0,
                    (random.random() * 2.0) - 1.0
                    ]
                normalizedVector = randomVector / np.linalg.norm(randomVector)
                normalizedVector *= random.random()**0.33  
                sizedVector = normalizedVector * step * spread
                fullVector = [
                    x + sizedVector[0],
                    y + sizedVector[1],
                    z + sizedVector[2],
                ]
                points_orig.append(fullVector)  
                iteration += 1        
        


while point_count < 1:
    point_count += 1
    randomVector = [        
        (random.random() * 2.0) - 1.0,
        (random.random() * 2.0) - 1.0,
        (random.random() * 2.0) - 1.0
        ]
    normalizedVector = randomVector / np.linalg.norm(randomVector)
    normalizedVector *= random.random()**0.33

    noiseValue = checkNoiseVal(normalizedVector[0], normalizedVector[1], normalizedVector[2])
    normalizedNoise = normaliseNoise(noiseValue, True)    
    #print(str(noiseValue) + ' of ' + str(normalizedVector[0]) )
    # addStar = shouldInclude(normalizedNoise)
    # if addStar:
    #     starsCount += 1
    #     points_orig.append(normalizedVector)

points = np.array(points_orig, dtype="float32")
points_binary_blob = points.tobytes()
print(str(starsCount) + 'stars')

print(str(noiseRealMin) + ' -> ' + str(noiseRealMax))
print(str(noiseBelowZero) + ' | ' + str(noiseAboveZero))
print('noiseDistribution')
print(noiseDistribution)
print('normalizedDistribution ')
print(normalizedDistribution)
print('starsAddedAtDistribution')
print(starsAddedAtDistribution)
print(str(7*255))

total = sum(normalizedDistribution)
print(' total: '+ str(total))

gltf = pygltflib.GLTF2(
    scene=0,
    scenes=[pygltflib.Scene(nodes=[0])],
    nodes=[pygltflib.Node(mesh=0)],
    meshes=[
        pygltflib.Mesh(
            primitives=[
                pygltflib.Primitive(
                    attributes=pygltflib.Attributes(POSITION=0), mode=pygltflib.POINTS
                )
            ]
        )
    ],
    accessors=[
        pygltflib.Accessor(
            bufferView=0,
            componentType=pygltflib.FLOAT,
            count=len(points),
            type=pygltflib.VEC3,
            max=points.max(axis=0).tolist(),
            min=points.min(axis=0).tolist(),
        ),
    ],
    bufferViews=[
        pygltflib.BufferView(
            buffer=0,
            byteOffset=0,
            byteLength=len(points_binary_blob),
            target=pygltflib.ARRAY_BUFFER,
        ),
    ],
    buffers=[
        pygltflib.Buffer(
            byteLength=len(points_binary_blob)
        )
    ],
)
gltf.set_binary_blob(points_binary_blob)


gltf.save('test_tpm.gltf')

#viewable = trimesh.verticies.copy()
#viewable = trimesh.points.PointCloud(points)
#viewable.show()

m = pyrender.Mesh.from_points(points)
scene = pyrender.Scene()
scene.add(m)
pyrender.Viewer(scene)
