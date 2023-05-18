import numpy as np
import pygltflib
import random
import opensimplex

pointLimit = 1000000
thresholdMin = 0.25
thresholdMax = 0.8
range = thresholdMax - thresholdMin
mult = 6
points_orig = []
point_count = 0;
noise = opensimplex.OpenSimplex (seed=42)

def checkNoiseVal(x, y, z):
    x *= mult
    y *= mult
    z *= mult
    return noise.noise3(x, y, z)

def shouldInclude(val):
    
    if val > thresholdMax:
        return True
    elif val < thresholdMin:
        return False
    
    normalized = (val - thresholdMin)/thresholdMax
    if normalized**1.0 > random.random():
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
    normalizedVector *= random.random()**0.33

    noiseValue = checkNoiseVal(normalizedVector[0], normalizedVector[1], normalizedVector[2])
    #print(str(noiseValue) + ' of ' + str(normalizedVector[0]) )
    addStar = shouldInclude(noiseValue)
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

