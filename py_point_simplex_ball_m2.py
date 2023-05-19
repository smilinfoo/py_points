import numpy as np
import pygltflib
import random
import opensimplex
import math
from pathlib import Path
import os

aboveMaxThreshold = 0
belowMinCount = 0
inRange = 0
distribution = [0,0,0,0,0,0,0,0,0,0,0]
starsInNode = 10
nodeRange = 0.0000001
nodeLimit = 1000
thresholdMin = 0.3
thresholdMax = 0.75
range = thresholdMax - thresholdMin
mult = 6
points_orig = []
point_count = 0
noise = opensimplex.OpenSimplex (seed=42)
aboveMaxThreshold = 0
belowMinCount = 0
inRange = 0


def checkNoiseVal(x, y, z):
    x *= mult
    y *= mult
    z *= mult
    return noise.noise3(x, y, z)

def shouldInclude(val):
    global belowMinCount, aboveMaxThreshold, inRange

    returnVal = 0
    if val > thresholdMax:
        aboveMaxThreshold += 1
        returnVal =  0
    elif val < thresholdMin:
        belowMinCount += 1
        returnVal =  1
    else:
        inRange += 1
        normalized = (val - thresholdMin)/thresholdMax
        #print('normalized ' + str(normalized))
        sloped = normalized**1.0
        #print('sloped ' + str(sloped))
        scaled =  math.floor(sloped * 10)
        #print('scaled ' + str(scaled))
        distribution[scaled] += 1
        returnVal = scaled * 10
    # if sloped > random.random():
    #     return 
    # else:
    #     return 0
    return returnVal

def createXPointsWithinX(numberToAdd, maxDistance, coord):
    #print('t')
    createdPoints = []
    loopCount = 0
    #print('node of ' + str(numberToAdd))
    while loopCount < numberToAdd:
        #print('         ' + str(loopCount))
        loopCount += 1
        createPointWininX(maxDistance, coord)

def createPointWininX(maxDistance, coord):
    randomVector = [        
        (random.random() * 2.0) - 1.0,
        (random.random() * 2.0) - 1.0,
        (random.random() * 2.0) - 1.0
    ]  
    normalizedVector = randomVector / np.linalg.norm(randomVector)
    scaledToRange = normalizedVector * maxDistance
    offset = coord + scaledToRange
    createPointAtX(offset)

def createPointAtX(coord):
    global points_orig
    #print('p')
    #print(type(points_orig))
    #print(type(coord))
    points_orig = points_orig + coord.tolist()

def get_write_path():
    file_name = os.path.splitext(os.path.basename(os.path.realpath(__file__)))[0]
    full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "results")
    if not os.path.exists(full_path):
        os.mkdir(full_path)

        if not os.path.exists(os.path.join(full_path, file_name)):
            os.mkdir(os.path.join(full_path, file_name))

    file_location = os.path.join(full_path, file_name, 'stars.gltf')
    return file_location


starsCount = 0
while point_count < nodeLimit:
    point_count += 1
    randomVector = [        
        (random.random() * 2.0) - 1.0,
        (random.random() * 2.0) - 1.0,
        (random.random() * 2.0) - 1.0
        ]
    normalizedVector = randomVector / np.linalg.norm(randomVector)
    normalizedVector *= random.random()**0.33

    noiseValue = checkNoiseVal(normalizedVector[0], normalizedVector[1], normalizedVector[2])
    addStar = shouldInclude(noiseValue)
    createXPointsWithinX(addStar, nodeRange, normalizedVector)
    #if addStar:
        #starsCount += 1
        #points_orig.append(normalizedVector)

print(str( len(points_orig)))
points = np.array(points_orig, dtype="float32")
points_binary_blob = points.tobytes()
print(str(len(points)/3) + 'stars from ' + str(nodeLimit))
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
file_path = get_write_path()
gltf.save(file_path)

print('over ' + str(aboveMaxThreshold) + ' under ' + str(belowMinCount) + ' in range ' + str(inRange))
print(distribution)