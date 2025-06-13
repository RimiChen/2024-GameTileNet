
# 📦 GameTileNet Project: Script Overview

This document summarizes all scripts in the project, grouped by task, with a brief description of their functionality and input/output.

---

## 🧩 1. Segmentation Scripts

Scripts that segment tiles into object groups.

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| `ExtractObject.py`, `ExtractObjectModel.py` | Group tiles into segments using recursive method or model | Tile grid | Segment images |
| `FindSegmentations.py`, `FindSegmentations_2.py` | Full segmentation pipeline | Tile folders | Segment folders |
| `CheckObjectComplete.py` | Checks whether a segment is complete | Segment image | Boolean label |
| `CountSegments.py` | Count number of segments | Segment directory | Count info |
| `ListSegments.py` | List segment info | Segment folder | Tile list per segment |
| `ExtractObjectMaxBox.py` | Extract object using bounding box | Tile images | Object crops |

---

## 🔗 2. Connectivity Scripts

Estimate or annotate connections between tiles (visual similarity, edges, adjacency).

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| `FindConnectivity.py`, `_2.py`, `_3.py` | Estimate connectivity across tiles | Tile grid | Connectivity map |
| `LabelingConnectivityGUI.py`, `LabelingConnectivityGUI2.py` | Manual annotation interface | Tile folder | Label files |
| `LabelingSimilarityAuto.py` | Auto-label similarity | Tile pairs | Prediction labels |
| `LabelSimilarityGUI.py` | GUI for similarity labels | Tile images | Annotated JSON |
| `CompareSimilarityLabels.py` | Compare human/model labels | JSON labels | Accuracy |
| `FindNeighbors.py` | Get tile adjacency info | Tile grid | Neighbor pairs |
| `StatisticsForSimilarity.py` | Similarity analysis | Labels | Stats |
| `CheckTileSimilarity.py` | Visual comparison heuristic | Tile pair | Similarity result |

---

## ✅ 3. Completeness Classification

Classify whether a tile is complete (full object) or partial (cropped or cut).

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| `Task_Completeness_data.py` | PyTorch dataset class | Labeled tile folder | Image dataset |
| `Task_Completeness_data_split.py` | Train/val/test split | Labels + tiles | 3-way folder |
| `Task_Completeness_data_training.py` | Train ResNet18 | Dataset | Trained model |
| `Task_Completeness_model_inference.py` | Use model for prediction | Images | Labels |
| `LabelingCompleteness.py`, `_v2.py` | GUI for manual annotation | Segment images | Label JSON |

---

## 🧠 4. Knowledge Graph Construction

Extract semantic and spatial knowledge from scenes and build KGs.

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| `ConstructSceneKG_*.py` | Build scene KGs | Parsed scenes | .json graphs |
| `Parsing*.py` | Extract scene components | Game scenes | Dictionaries |
| `LayerSceneGeneratorWithAffordance.py` | Build scene with layers | Parsed data | Scene layout |
| `Summarize_KG.py` | Analyze KG | Graphs | Summary |
| `checkKG.py` | Validate KG | Graph | Logs |

---

## 🌱 5. Cellular Automata

Generate terrain-like tile structures.

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| `CA_terrian_v*.py` | Terrain generation using CA | Seed + rules | Patch images |

---

## 🛠️ 6. Utilities

| Script | Purpose |
|--------|---------|
| `SliceTiles.py`, `Transform16-32.py`, `Identify16-32.py` | Tile transformation utilities |
| `DisplayImage.py` | Quick image viewer |
| `SelectImagePairs.py` | Tile pair setup |
| `CheckTilesetGrid.py` | Tileset integrity check |
| `NarrativePrompt_*.py` | Prompt templates |
| `README.md`, `tile_pipeline_documentation.md` | Docs |

---

*Last updated: June 2025*

