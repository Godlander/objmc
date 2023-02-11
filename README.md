only works in snapshot 23w06a+

# heads

model geometry complexity is very limited, and textures must be 32x32

`python objh.py --obj model.obj --tex texture.png --out skin.png --scale 5`

will output a skin image and a command missing a base64 url in the nbt

upload the skin to your account, then run `python objh.py --skin username` to get the base64 url

complete the command, then you can run it to summon the model. anyone with the resourcepack will be able to see the model.

## example

tree model:

![image](https://user-images.githubusercontent.com/16228717/218281527-a05341cc-a478-4a80-b41b-0a7da3545f51.png)
```js
execute positioned ~ ~2 ~ summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display summon item_display as @e[type=item_display,distance=..0.1,nbt={item:{id:"minecraft:air"}}] run data merge entity @s {transformation:[0f,0f,0f,0f, 0f,0f,0f,0f, 0f,0f,0f,0f, 0f,0f,0f,1f],item:{id:"player_head",Count:1b,tag:{SkullOwner:{Id:[I;1617307098,1728332524,-1389744951,-1149641594],Properties:{textures:[{Value:"eyd0ZXh0dXJlcyc6IHsnU0tJTic6IHsndXJsJzogJ2h0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvMjI1YjM1NDhjMjFiZWE5MmU2YjQ5NTViMTZkMTQ1M2YzYmExMzE4MTE3YTgwNGE4ZmIzZTliZGJjNDQwMGM0Myd9fX0="}]}}}}}
```
