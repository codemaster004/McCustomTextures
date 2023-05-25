import os
import shutil
import json
import zipfile

FINAL_PACK_DIR = 'resource_packs/final-texture-pack'
ASSETS_PACKS_DIR = 'resource_packs/temp-packs'
BASE_MC_PACK_DIR = 'resource_packs/minecraft-base'

SUB_FOLDERS = ['assets', 'minecraft']
TEXTURE_FOLDER = ['textures', 'item']
MODELS_FOLDER = ['models', 'item']


def clear_final_pack():
	"""
	Removes everything inside final texture pack but the `pack.mcmeta` file
	:return: None
	"""
	with os.scandir(FINAL_PACK_DIR) as entries:
		for entry in entries:
			if entry.name != 'pack.mcmeta':
				
				if entry.is_file():
					os.remove(entry.path)
				elif entry.is_dir():
					shutil.rmtree(entry.path)


def generate_basic_pack_structure():
	"""
	Generates basic file structure for final texture pack
	:return: None
	"""
	new_assets_mc_path = os.path.join(FINAL_PACK_DIR, *SUB_FOLDERS)
	os.makedirs(new_assets_mc_path)
	
	required_folders = ['models/item', 'textures/item']
	for folder_name in required_folders:
		new_folder_path = os.path.join(new_assets_mc_path, folder_name)
		os.makedirs(new_folder_path)


def zip_files(output_path, file_paths):
	with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
		for file_path in file_paths:
			# Add each file to the zip archive
			zipf.write(file_path, os.path.basename(file_path))


def add_custom_model():
	"""
	Add new custom texture for mc item
	:return: None
	"""
	is_a_block = False
	for_mc_item = 'totem_of_undying'
	
	model_name = 'wither_totem'
	custom_model_json_path = 'resource_packs/temp-packs/test-totem/assets/minecraft/models/totem_of_undying.json'
	custom_texture_path = 'resource_packs/temp-packs/test-totem/assets/minecraft/textures/item/totem_of_undying.png'
	
	# 1. Copy Real model item and create its folder
	mc_resource_path = [
		*SUB_FOLDERS,
		'models',
		'block' if is_a_block else 'item'
	]
	
	source_file_path = os.path.join(BASE_MC_PACK_DIR, *mc_resource_path, f'{for_mc_item}.json')
	# We need to always copy to item folder. Custom models doesn't work for blocks.
	destination_directory = os.path.join(FINAL_PACK_DIR, *SUB_FOLDERS, *MODELS_FOLDER)
	if not os.path.exists(os.path.join(destination_directory, f'{for_mc_item}.json')):
		shutil.copy(source_file_path, destination_directory)
	
	# Create directory of the same name as item to store its custom models
	if not os.path.exists(os.path.join(destination_directory, for_mc_item)):
		os.mkdir(os.path.join(destination_directory, for_mc_item))
	
	# 2. Copy Custom texture
	source_file_path = os.path.join(custom_texture_path)
	destination_directory = os.path.join(FINAL_PACK_DIR, *SUB_FOLDERS, *TEXTURE_FOLDER)
	
	shutil.copy(source_file_path, destination_directory)
	
	# 3. Rename Custom texture to its custom name
	old_file_path = os.path.join(destination_directory, f'{for_mc_item}.png')
	new_file_path = os.path.join(destination_directory, f'{model_name}.png')
	os.rename(old_file_path, new_file_path)

	# 4. Copy JSON for custom model
	if custom_model_json_path:
		source_file_path = os.path.join(custom_model_json_path)
		destination_directory = os.path.join(FINAL_PACK_DIR, *SUB_FOLDERS, *MODELS_FOLDER, for_mc_item)
		
		shutil.copy(source_file_path, destination_directory)
		
		# 5. Rename model to its custom name
		old_file_path = os.path.join(destination_directory, f'{for_mc_item}.json')
		new_file_path = os.path.join(destination_directory, f'{model_name}.json')
		os.rename(old_file_path, new_file_path)
		
		# 6. Alter models path to its new texture
		with open(new_file_path) as f:
			json_model = json.load(f)
		
		keys = list(json_model['textures'].keys())
		json_model['textures'][keys[0]] = f'item/{model_name}'
		
		with open(new_file_path, 'w') as f:
			json.dump(json_model, f)
		
	else:  # Create basic model.json
		file_path = os.path.join(BASE_MC_PACK_DIR, *mc_resource_path, f'{for_mc_item}.json')
		with open(file_path) as f:
			basic_structure = json.load(f)
		
		keys = list(basic_structure['textures'].keys())
		basic_structure['textures'][keys[0]] = f'item/{model_name}'
		
		file_path = os.path.join(FINAL_PACK_DIR, *SUB_FOLDERS, *MODELS_FOLDER, for_mc_item, f'{model_name}.json')
		with open(file_path, 'w') as f:
			json.dump(basic_structure, f)
	
	# 7. Add predicate to mc Model
	file_path = os.path.join(FINAL_PACK_DIR, *SUB_FOLDERS, *MODELS_FOLDER, f'{for_mc_item}.json')
	with open(file_path) as f:
		mc_model = json.load(f)
	
	if 'overrides' not in mc_model:
		mc_model['overrides'] = []
	
	n_existing_items = len(mc_model['overrides'])
	new_predicate = {
		'predicate': {
			'custom_model_data': n_existing_items + 1
		},
		'model': f'item/{for_mc_item}/{model_name}'
	}
	mc_model['overrides'].append(new_predicate)
	
	with open(file_path, 'w') as f:
		json.dump(mc_model, f)
	
	# 8. Zip the resulting pack
	files_to_zip = []
	with os.scandir(FINAL_PACK_DIR) as entries:
		for entry in entries:
			files_to_zip.append(os.path.join(FINAL_PACK_DIR, entry.name))
	output_zip = 'CustomServerPack.zip'
	
	zip_files(output_zip, files_to_zip)
	

if __name__ == '__main__':
	pass
	clear_final_pack()
	generate_basic_pack_structure()
	add_custom_model()
