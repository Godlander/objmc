# optifine compatibility

for some reason optifine just sets alpha below 20 to 0, and forces mipmapping regardless of texture resolution

this version of objmc does not use alpha at the cost of needing more texture data space and more shader texture reads

block models do not work, only item models.