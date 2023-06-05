import numpy as np
import pygltflib
import random
import opensimplex
import pyrender
import trimesh
import math

# opensimplex returns values ~ between -1 and 1
# this sets the threshold for a point to be generated
# any value below noiseMin will result in empty space, and value above moiseMax will garauntee a point
noiseMin = 0
noiseMax = 0.8
# once the noise is normalized between noiseMin and noiseMax to 0-1 we can apply an exponent to
# shape the slope into a curve.  Higher values push the curve toward 0, lower values toward 1.  
# 1 is a straight line
curve = 3.0

# TODO: better comments for this
noiseRealMax = 0
noiseRealMin = 0
noiseAboveZero = 0
noiseBelowZero = 0
noiseRange = noiseMax - noiseMin
noiseDistribution = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
normalizedDistribution = [0,0,0,0,0,0,0,0,0,0]
pointLimit = 1000000
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
    
    normalized = (val - noiseMin)/noiseRange
    
    noiseDistribution[abs(index)+10] += 1
    return normalized

def shouldInclude(val):
    global normalizedDistribution

    
    sloped = val**curve
    normalizedDistribution[clamp( math.floor(sloped*10), 0, 9 )] += 1

    if sloped > random.random():
        return True
    else:
        return False


starsCount = 0
while point_count < pointLimit:
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

# Stats about output distribution
# TODO: explain the outut
viewable = trimesh.points.PointCloud(points)
#viewable.show()
print(str(noiseRealMin) + ' -> ' + str(noiseRealMax))
print(str(noiseBelowZero) + ' | ' + str(noiseAboveZero))
print('noise dist ')
print(noiseDistribution)
print('sloped dist ')
print(normalizedDistribution)
total = sum(normalizedDistribution)
perc = []
for incident in normalizedDistribution:
    perc.append(round(incident/total, 4))

print(perc)
print(' total: '+ str(total))
m = pyrender.Mesh.from_points(points)
scene = pyrender.Scene()
scene.add(m)
pyrender.Viewer(scene)
