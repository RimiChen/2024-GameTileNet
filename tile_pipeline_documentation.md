# Tile Processing Pipeline: Function Inventory and Analysis Summary

This document catalogs the core functionality and purpose of each script from the uploaded codebase related to tile slicing, labeling, similarity detection, and connectivity analysis. It also outlines the input/output behavior and interdependencies of each component to plan the next implementation steps effectively.

---

## 1. Tile Segmentation and Preprocessing

| Task | Script(s) | Input | Output | Purpose |
|------|-----------|-------|--------|---------|
| Detect tile size (16/32) | `Identify16-32.py` | Tileset image | Tile size (16 or 32) | For routing later processing |
| Resize 16→32 | `Transform16-32.py` | 16×16 images | 32×32 images | Standardize tile size |
| Draw grid overlays | `CheckTilesetGrid.py`, `DisplayImage.py` | Tileset | Grid-labeled image | For inspection/debugging |

---

## 2. Object Extraction and Classification

| Task | Script(s) | Input | Output | Purpose |
|------|-----------|-------|--------|---------|
| Slice tiles + metadata | `SliceTiles.py` | Tileset PNG | Tiles as PNGs + annotations (JSON) | Core tile slicing step |
| Save file paths | `CreateFileList.py` | Folder | JSON list of files | For GUI and labeling scripts |
| Segment manually | `FindSegmentations.py` | Sliced tiles | Combined segments by object | Group connected tiles |
| Auto-segment w/ SAM | `ExtractObjectModel.py`, `ExtractObjectMaxBox.py` | Tileset | Object crops | Optional: Deep segmentation |
| Filter completeness | `CheckObjectComplete.py` | Segments | Crops labeled complete/incomplete | Use YOLOv5 to filter incomplete objects |

---

## 3. Tile Similarity and Adjacency Detection

| Task | Script(s) | Input | Output | Purpose |
|------|-----------|-------|--------|---------|
| Find neighbors | `FindNeighbors.py` | Cropped tiles | JSON neighbor map | Determines adjacency |
| Select image pairs | `SelectImagePairs.py` | Neighbor JSON | Pairs for labeling | Sampling input pairs |
| Label similarity (GUI) | `LabelSimilarityGUI.py` | Pairs JSON | Labeled similarity | Human verification |
| Auto label similarity | `LabelingSimilarityAuto.py` | Pairs JSON | Labeled similarity | SSIM-based auto-labeling |
| Compare labels | `CompareSimilarityLabels.py` | Labeled JSONs | Match stats | Evaluate model vs. human |
| Stats on similarity | `StatisticsForSimilarity.py` | Similarity JSON | Stats JSON | Threshold tuning |

---

## 4. Labeling Interfaces (Tkinter GUI Tools)

- `LabelingObjectGUI.py`: Manually tag object presence/type in tile images  
- `LabelingConnectivityGUI.py` / `LabelingConnectivityGUI2.py`: Interactive tool to tag tile-to-tile connectivity  
- `LabelingSimilarityAuto.py`, `LabelingCompleteness.py`: Auto-label completeness or similarity; may involve user confirmation  

---

## 5. Supporting Scripts

- `DisplayImage.py`: Viewer utility for showing processed tiles  
- `Test.py`, `testScriptForEnv.py`: Miscellaneous test or environment check scripts  

---

## 6. Narrative Scripts (Not part of tile pipeline)

- `NarrativePrompt_openAI.py`, `NarrativePrompt_langchain.py`: Generate story prompts and spatial relations using OpenAI or LangChain  

---

## Summary of Pipeline Flow

1. **Tileset Preparation**  
   - `SliceTiles.py` → `CreateFileList.py`
2. **Object Extraction (Optional)**  
   - `ExtractObject*.py`, `CheckObjectComplete.py`
3. **Connectivity & Similarity Computation**  
   - `FindConnectivity_*.py`, `CheckTileSimilarity.py`
4. **Manual + Semi-Auto Labeling**  
   - GUI scripts, auto-tagging (`Labeling*`)
5. **Analysis/Statistics**  
   - `CompareSimilarityLabels.py`, `StatisticsForSimilarity.py`

---

## Next Steps

To continue the tile pipeline:
- [ ] Confirm input tileset folder and verify output tiles (Step 1 done?)
- [ ] Re-run or inspect `FindConnectivity_3.py` for completeness
- [ ] Run `CheckTileSimilarity.py` and compare with GUI labels
- [ ] Choose auto-label or manual completeness tagger to finalize dataset
- [ ] Save all intermediate outputs to one JSON index
- [ ] (Optional) Link outputs to narrative scene generator

Once you confirm which parts are done or need fixing, I’ll help build the script chain.
