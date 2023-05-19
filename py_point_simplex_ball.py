import numpy as np
import pygltflib
import random
import opensimplex
import pyrender
import trimesh
import math


noiseMin = -0.75
noiseMax = 0.8
noiseRealMax = 0
noiseRealMin = 0
noiseAboveZero = 0
noiseBelowZero = 0
noiseRange = noiseMax - noiseMin
noiseDistribution = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
pointLimit = 10000
thresholdMin = 0.25
thresholdMax = 0.25
range = thresholdMax - thresholdMin
mult = 10
points_orig = []
point_count = 0;
noise = opensimplex.OpenSimplex (seed=42)

def checkNoiseVal(x, y, z):
    x *= mult
    y *= mult
    z *= mult
    return noise.noise3(x, y, z)

def normaliseNoise(val):
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

   # index = math.floor((max([min([val,1]),-1]) * 10))
    #print('val:'+str(val)+ ' index:'+str(index))
    noiseDistribution[index+10] += 1
    normalized = (val - noiseMin)/noiseRange
    #index = math.floor(normalized*10)
    #index = max([0, min([index, 1])])
    #print(index)
    #noiseDistribution[index] += 1
    return normalized

def shouldInclude(val):
    
    if val > thresholdMax:
        return True
    elif val < thresholdMin:
        return False
    
    return False
    normalized = (val - thresholdMin)/thresholdMax
    if normalized**8.0 > random.random():
        return True
    else:
        return False


starsCount = 0;
while point_count < pointLimit:
    point_count += 1
    randomVector = [        
        (random.random() * 2.0) - 1.0,
        (random.random() * 2.0) - 1.0,
        (random.random() * 2.0) - 1.0
        ]
    normalizedVector = randomVector / np.linalg.norm(randomVector)
    normalizedVector *= random.random()*0.33

    noiseValue = checkNoiseVal(normalizedVector[0], normalizedVector[1], normalizedVector[2])
    normalizedNoise = normaliseNoise(noiseValue)    
    #print(str(noiseValue) + ' of ' + str(normalizedVector[0]) )
    addStar = shouldInclude(normalizedNoise)
    if addStar:
        starsCount += 1
        points_orig.append(normalizedVector)

points = np.array(points_orig, dtype="float32")
points_binary_blob = points.tobytes()
print(str(starsCount) + 'stars')
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
viewable = trimesh.points.PointCloud(points)
#viewable.show()
print(str(noiseRealMin) + ' -> ' + str(noiseRealMax))
print(str(noiseBelowZero) + ' | ' + str(noiseAboveZero))
print(noiseDistribution)
m = pyrender.Mesh.from_points(points)
scene = pyrender.Scene()
scene.add(m)
pyrender.Viewer(scene)
