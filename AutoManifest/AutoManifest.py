import json
import uuid
import typing
import sys

from dataclasses import asdict, dataclass, field
from pathlib import Path

#class for sub-options and options without sub-options
@dataclass
class LeafOption:
    Name : str = ""
    Description : str = ""
    Image : Path = field(default_factory = lambda: Path("~"))
    Include : list[str] = field(default_factory = lambda: [])

#class for options with sub-options
@dataclass
class NodeOption:
    Name : str = ""
    Description : str = ""
    Image : Path = field(default_factory = lambda: Path("~"))
    SubOptions : list[LeafOption] = field(default_factory = lambda: [])

#class for the manifest
@dataclass
class Manifest:
    Version : typing.Literal[1] = 1
    Guid : str = uuid.uuid4().hex
    Name : str = ""
    Description : str = ""
    IconPath : Path = field(default_factory = lambda: Path("~"))
    Options : list[NodeOption] = field(default_factory = lambda: [])

def main():
    #get mod folder, containing all option and sub-option folders
    main_dir = Path(input("Enter mod directory: "))

    #find pre-existing manifest
    #save it to variable (for extracts) and .txt file (as backup)
    if Path(main_dir/"manifest.json").is_file():
        with open(f"{main_dir}/manifest.json", "r", encoding="utf-8") as prev_file:
            prev_manifest = json.load(prev_file)
        with open(f"{main_dir}/old_manifests.txt", "a") as store_file:
            store_file.write(json.dumps(prev_manifest, indent="\t"))
    else:
        prev_manifest = None

    #create new manifest
    manifest = Manifest()
    manifest.Name = main_dir.name

    #use pre-existing manifest version, guid, and main description
    if prev_manifest != None:
        manifest.Version = prev_manifest.get("Version", manifest.Version)
        manifest.Guid = prev_manifest.get("Guid", manifest.Guid)
        manifest.Description = prev_manifest.get("Description", manifest.Description)

    #find and add main mod image
    images = sorted(main_dir.rglob(f"{main_dir.stem}.[jp][pn]g"))
    if images: manifest.IconPath = f"""{images[0].relative_to(main_dir).as_posix()}"""

    #loop through option folders
    for mod_sub_dir in main_dir.iterdir():
        #make sure it's a folder
        if mod_sub_dir.is_dir():
            #check if option folder has sub-option folders
            if any(item.is_dir() for item in mod_sub_dir.iterdir()):
                #create new option
                option = NodeOption()

                #loop through sub-option folders
                for mod_subsub_dir in mod_sub_dir.iterdir():
                    #make sure it's a folder
                    if mod_subsub_dir.is_dir():
                        #exit if sub-option folder has internal folders (improper layout)
                        if any(item.is_dir() for item in mod_subsub_dir.iterdir()):
                            input("Folders nested incorrectly! Press any key to exit...")
                            sys.exit()
                        
                        #skip if sub-option folder doesn't have patch files
                        elif not any(".patch_" in str(item) for item in mod_subsub_dir.iterdir()):
                            continue

                        #create new sub-option
                        sub_option = LeafOption()
                        sub_option.Name = mod_subsub_dir.name
                        sub_option.Include = [f"{mod_sub_dir.name}/{mod_subsub_dir.name}"]
                        
                        #use pre-existing sub-option description
                        if prev_manifest != None:
                            sub_option.Description = next((
                                sub_item.get("Description") 
                                for item in prev_manifest.get("Options", []) 
                                for sub_item in item.get("SubOptions", [])
                                if sub_item.get("Name") == mod_subsub_dir.name), "")

                        #find and add sub-option image
                        images = sorted(main_dir.rglob(f"{mod_subsub_dir.stem}.[jp][pn]g"))
                        if images: sub_option.Image = f"""{images[0].relative_to(main_dir).as_posix()}"""
                        else:
                            images = sorted(mod_subsub_dir.glob("*.[jp][pn]g"))
                            if images: sub_option.Image = f"""{images[0].relative_to(main_dir).as_posix()}"""

                        #add sub-option to option
                        option.SubOptions.append(sub_option)

            #check if option folder has patch files
            elif any(".patch_" in str(item) for item in mod_sub_dir.iterdir()):
                #create new option
                option = LeafOption()
                option.Include = [f"{mod_sub_dir.name}"]

            #skip if option folder doesn't have sub-option folders or patch files
            else:
                continue

            #finish creating new option
            option.Name = mod_sub_dir.name
            
            #use pre-existing option description
            if prev_manifest != None:
                option.Description = next((
                    item.get("Description") 
                    for item in prev_manifest.get("Options", []) 
                    if item.get("Name") == mod_sub_dir.name), "")
            
            #find and add option image
            images = sorted(main_dir.rglob(f"{mod_sub_dir.stem}.[jp][pn]g"))
            if images: option.Image = f"""{images[0].relative_to(main_dir).as_posix()}"""
            else:
                images = sorted(mod_sub_dir.glob("*.[jp][pn]g"))
                if images: option.Image = f"""{images[0].relative_to(main_dir).as_posix()}"""
            
            #add option to manifest
            manifest.Options.append(option)

    #write manifest to manifest.json file
    with open(f"{main_dir}/manifest.json", "w") as main_file:
        json.dump(asdict(manifest), main_file, indent="\t", default=str)

    input("Press any key to exit...")

if __name__ == "__main__":
    main()