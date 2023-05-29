# Small automation for MC custom textures
Me and my friends want to use Hermitcraft's custom_roleplay_data datapack so let's automate the process of creating server side resourcepack.

Steps required to create the pack:

## 1. Copy original mc item model json to our custom resourcepack
For tidyness we also create a folder to store our custom textures for each item.

## 2. Copy cutom texture provided by user
By default it will also have original item name, we need to rename it.

## 3. Copy custom texture's json model
This also needs to be renamed and inside the path leading to the texture needs to be changes.
As we are using our file system.

In case such file doesn't exits we create a basic model from original mc model json

## 4. Add predicates mc model json from step 1
To allow our custom texture to work we need to link mc original item with our cutom item
For every new texture connected to mc item we add new pridicate

`{"predicate": {"custom_model_data": IDNumber}, "model": "path/to/cutom/model/json"}`

## 5. Zip resulting resourcepack
## 6. Generate SHA-1 for the zip file
Both of those steps are required to put te resourcepack on the server


### Our file structure

```
- Resource Pack
  |- assets
  |  |- minecraft
  |  |  |- models
  |  |  |  |- item
  |  |  |  |  |- mc_item.json
  |  |  |  |  |- mc_item
  |  |  |  |  |  |- custom_item.json
  |  |  |- textures
  |  |  |  |- item
  |  |  |  |  |- custom_item.png
  |- pack.mcmeta
 ```
