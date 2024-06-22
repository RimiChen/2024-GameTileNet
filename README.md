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
  <!-- - **annotations**/
    - dataset1.csv
    - dataset2.csv -->
  - README.md

  ---
### File Descriptions

* SliceTile.py: Slice tilesets into 32x32 size, and find corresponding segements on the tileset images. Create and save the slices in folder: <tileset_name: (collection_index)_(tileset_index)>. 
* LabelSimilarityGUI.py: Record the similarity of two adjacent tiles.
* CheckTileSimilarity.py: Check the similarity of two adjacent tiles.
* LabelingConnectivityGUI.py: Record tile's possible connecting directions.
* LabelingObjectGUI.py: Record user input for labeling Object names.            
* CreateFileList.py: Import a folder and create a file list based on files inside.

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
 