# GameTileNet
A dataset for game tiles collected from OpenGameArt.org (CC licenses), with semantic labels and other information.

---
### File Structures

- **2024-GameTileNet**/
  - **src**/
    - SliceTile.py
    - LabelSimilarityGUI.py
    - CheckTileSimilarity.py
    - LabelingConnectivityGUI.py
    - LabelingObjectGUI.py            
    - CreateFileList.py
    - Transform16-32.py
    - Test.py
    - DisplayImage.py
    - FindNeighbots.py            
  <!-- - **annotations**/
    - dataset1.csv
    - dataset2.csv -->
  - README.md

  ---
### File Descriptions

* SliceTile.py: Slice tilesets into 32x32 size, and find corresponding segements on the tileset images. Create and save the slices in folder: <tileset_name: (collection_index)_(tileset_index)>. 
* LabelSimilarityGUI.py: Record the similarity of two adjacent tiles.
* CheckTileSimilarity.py: Check the similarity of two adjacent tiles, and other image processing functions: filter the blank image, set similarity to zero if all side blank, etc.. 
* LabelingConnectivityGUI.py: Record tile's possible connecting directions.
* LabelingObjectGUI.py: Record user input for labeling Object names.            
* CreateFileList.py: Import a folder and create a file list based on files inside.
* Transform16-32.py: Tranform 16x16 tile to 32x32 tiles.
* Test.py: Mixed testing scripts
* DisplayImage.py: Dispaly tileset with tile_size grids.
* FindNeighbots.py: For each split tiles in tileset folder, find all their exist neighbors.
---
### Instructions

Conda environment for the scripts and models:

```
conda env create -f environment.yml
```

---

### Citation

bibTex:

```


```
 