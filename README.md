# Realistic Terrain
Add-on for Blender that generates terrain height map and simulates hydraulic erosion using DirectX11 compute shaders.

## Screenshot
[youtube](https://www.youtube.com/watch?v=v3CK-s1jXPg)

<details>

<summary>Feature</summary>

<table>
    <caption>Generate Terrain Height Map (Left: Perlin Noise, Right: Perlin Noise with Ridge)</caption>
    <tr>
        <td><img src="media/noise.png" width="530" /></td>
        <td><img src="media/ridge-noise.png" width="530" /></td>
    </tr>
</table>
<table>
    <caption>Erode Terrain Mesh (Left: Befor, Right: After)</caption>
    <tr>
        <td><img src="media/befor-erosion.png" width="530" /></td>
        <td><img src="media/after-erosion-and-smoothmesh.png" width="530" /></td>
    </tr>
</table>
<table>
    <caption>Terrain Material</caption>
    <tr>
        <td><img src="media/material.png" width="530" /></td>
    </tr>
</table>

</details>

## Requirements
- Windows10
- DirectX11
- Blender using Python 3.10.* (ex. Blender 3.4)
	- Numpy

## Note
<details><summary>Please see here</summary>
All versions 1.2 and later will be distributed with the release.
If you have already installed version 1.1 or earlier, please deactivate and uninstall the already installed realistic terrain before installing version 1.2 or later.
If you cannot uninstall version 1.1 or earlier, delete the folder directly. Add-ons for version 1.1 or earlier should be located in the following directory  

```
C:\Users\{USER_NAME}\AppData\Roaming\Blender Foundation\Blender\3.4\scripts\addons\realistic-terrain-master
```

</details>

## Install
<details>

<summary>Please see here</summary>

- Install 1.2 or later versions from release  
- Launch Blender and select the Zip file downloaded by Install from ```Edit/Preference/Add-ons```
<img src="media/install-to-blender.0.png" width="256"></img>  
- Enable "realistic terrain"  
<img src="media/install-to-blender.1.png" width="256"></img>  
- The toolbar will then appear here  
<img src="media/toolbar.png" width="256" /></img>  

</details>

## Tutorial
<details><summary>Process erosion for terrain mesh generated with A.N.T.Landscape</summary>

- Create an A.N.T. Landscape grid with a resolution of 1024x1024 (be sure to create the grid with NxN resolution)  
<img src="media/a.n.t-tutorial/000.png"></img>
- Run simulations from ```Terrain/Erode/Process```  
<img src="media/a.n.t-tutorial/001.png" width="256"></img>  
<img src="media/a.n.t-tutorial/002.png"></img>
- Create a grid with size 2.0 and resolution 1024x1024 from Terrain/Grid/Create (A.N.T. Landscape meshes are not UV expanded, and high-resolution grids take time to expand, so create a pre-expanded grid)  
- Apply Shrinkwrap to copy grid vertex height information  
<img src="media/a.n.t-tutorial/003.png" width="256"></img>
- Select the grid from which the height information was copied and attach TerrainMaterial  
<img src="media/a.n.t-tutorial/004.png" width="256"></img>  
<img src="media/a.n.t-tutorial/005.png"></img>
- Adjust parameters to complete  
<img src="media/a.n.t-tutorial/006.png"></img>

</details>


## Reference
- [SebLague: Hydraulic-Erosion](https://github.com/SebLague/Hydraulic-Erosion)
- [opensimplex](https://code.larus.se/lmas/opensimplex)
- [terrain-noise](https://www.youtube.com/watch?v=pmZQMzObjNo)
