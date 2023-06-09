import os
import shutil
import json
import zipfile
import hashlib
from datetime import datetime
import subprocess
import argparse

import dropbox
from dotenv import load_dotenv

load_dotenv()

FINAL_PACK_DIR = 'resource_packs/final-texture-pack'
ASSETS_PACKS_DIR = 'resource_packs/temp-packs'
BASE_MC_PACK_DIR = 'resource_packs/minecraft-base'
ZIPPED_PACK_DIR = 'packed_zips'

SUB_FOLDERS = ['assets', 'minecraft']
TEXTURE_FOLDER = ['textures', 'item']
MODELS_FOLDER = ['models', 'item']

ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')


dbx = dropbox.Dropbox(ACCESS_TOKEN)
dbx.users_get_current_account()

parser = argparse.ArgumentParser(description='Automation for creating Custom Server Resource packs')
parser.add_argument('-a', '--add_model', type=str, help='Add texture model')
parser.add_argument('-f', '--force', action='store_true', help='Force adding model potentially overwrite existing one')
parser.add_argument('-n', '--name', type=str, help='Name the custom model')
# parser.add_argument('box_token', help='Change dropbox Token')


def cli_input_handler():
	args = parser.parse_args()
	optional_arg_value = args.optional_arg
	
	if args.add_model:
		model_path = args.add_model
		for_mc_item = os.path.splitext(os.path.basename(model_path))[0]
		if args.name:
			custom_name = args.name


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


def zip_files(output_path, files_path, folder_path):
	""""
	Zipping given files into one zipfile
	"""
	with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
		# Add the file to the zip archive
		for path in files_path:
			zipf.write(path, os.path.basename(path))
		
		# Add the folder and its contents to the zip archive
		for root, _, files in os.walk(folder_path):
			for file in files:
				file_path = os.path.join(root, file)
				arcname = os.path.relpath(file_path, folder_path)
				zipf.write(file_path, os.path.join(os.path.basename(folder_path), arcname))


def calculate_sha1(file_path):
	"""
	Generates SHA-1 hash for given zip file
	:param file_path: path to tge zip file
	:return: Hash
	"""
	sha1_hash = hashlib.sha1()
	
	with open(file_path, 'rb') as file:
		while True:
			data = file.read(4096)  # Read file data in chunks
			if not data:
				break
			sha1_hash.update(data)
	
	return sha1_hash.hexdigest()


def copy_to_clipboard(text):
	process = subprocess.Popen('pbcopy', stdin=subprocess.PIPE, universal_newlines=True)
	process.communicate(input=text)


def generate_dropbox_link(dropbox_path):
	shared_link = dbx.sharing_create_shared_link_with_settings(dropbox_path)
	
	shared_link_url = shared_link.url
	
	downloadable_link = shared_link_url[:-1] + '1'
	print(downloadable_link)
	
	copy_to_clipboard(downloadable_link)


def upload_to_dropbox(file_path, file_name):
	dropbox_path = f'/{file_name}'
	
	# Upload the file
	path = os.path.join(file_path, file_name)
	with open(path, 'rb') as file:
		
		dbx.files_upload(file.read(), dropbox_path)
	
	generate_dropbox_link(dropbox_path)


def handle_created_pack():
	# 8. Zip the resulting pack
	files_to_zip = []
	with os.scandir(FINAL_PACK_DIR) as entries:
		for entry in entries:
			if entry.is_file():
				files_to_zip.append(os.path.join(FINAL_PACK_DIR, entry.name))
			elif entry.name == 'assets':
				assets_path = os.path.join(FINAL_PACK_DIR, entry.name)
	
	today = datetime.now().strftime("%d%m%Y-%H%M")
	file_name = f'CustomServerPack-{today}.zip'
	output_zip = os.path.join(ZIPPED_PACK_DIR, file_name)
	
	zip_files(output_zip, files_to_zip, assets_path)
	
	# 9. Generate SHA-1 for the zip file
	sha1 = calculate_sha1(output_zip)
	print(f"SHA-1 hash: {sha1}")
	
	upload_to_dropbox(ZIPPED_PACK_DIR, file_name)


def add_custom_model():
	"""
	Add new custom texture for mc item
	:return: None
	"""
	is_a_block = False
	for_mc_item = 'totem_of_undying'
	
	model_name = 'py_totem'
	custom_model_json_path = 'resource_packs/temp-packs/py-totem/assets/minecraft/models/item/totem_of_undying.json'
	custom_texture_path = 'resource_packs/temp-packs/py-totem/assets/minecraft/textures/item/totem_of_undying.png'
	
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


if __name__ == '__main__':
	pass
	cli_input_handler()
	# clear_final_pack()
	# generate_basic_pack_structure()
	# add_custom_model()
	# handle_created_pack()
