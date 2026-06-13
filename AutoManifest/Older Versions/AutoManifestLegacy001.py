from pathlib import Path
import sys

#search folders recursively for image with name
#return image text insert for manifest
def image_insert(header, directory, name):
    images = sorted(directory.rglob(f"{name}.[jp][pn]g"))
    if images:
        return f"""{header} "{images[0].relative_to(directory).as_posix()}","""
    else:
        return """"""

#extract text between header text and footer text from prev_manifest text
#return extracted text or default text for text insert for manifest
def text_insert(prev_manifest, header, footer, default):
    if prev_manifest != "" and  header in prev_manifest:
        temp_text = prev_manifest.split(header)[1]
        if footer in temp_text:
            return temp_text.split(footer)[0]
        else:
            return default
    else:
        return default

#get mod folder, containing all option and sub-option folders
main_dir = Path(input("Enter mod directory: "))

#find pre-existing manifest
#save it to variable (for extracts) and .txt file (as backup)
if Path(main_dir/"manifest.json").is_file():
    with open(f"{main_dir}/manifest.json", "r") as prev_file:
        prev_manifest = prev_file.read()
    with open(f"{main_dir}/old_manifests.txt", "a") as store_file:
        store_file.write(prev_manifest)
else:
    prev_manifest = ""

#extract pre-existing manifest version, guid, and main description
version = text_insert(
    prev_manifest, 
    """\n\t"Version": """, 
    """,\n""", 
    "1")
guid = text_insert(
    prev_manifest, 
    """\n\t"Guid": \"""", 
    """\",\n""", 
    "insert guid from https://www.uuidgenerator.net/")
description = text_insert(
    prev_manifest, 
    f"""\n\t"Name": "{main_dir.name}",\n\t"Description": \"""", 
    """\",\n""", 
    "")

#write main overhead in new manifest.json file
with open(f"{main_dir}/manifest.json", "w") as file:
    ins_str =   """{"""
    ins_str += f"""\n\t"Version": {version},"""
    ins_str += f"""\n\t"Guid": "{guid}","""
    ins_str += f"""\n\t"Name": "{main_dir.name}","""
    ins_str += f"""\n\t"Description": "{description}","""
    ins_str += image_insert(f"""\n\t"IconPath":""", main_dir, main_dir.stem)
    ins_str +=  """\n\t"Options": ["""
    file.write(ins_str)

#loop through option folders
for mod_sub_dir in main_dir.iterdir():
    #make sure it's a folder
    if Path(mod_sub_dir).is_dir():
        #skip if option folder doesn't have sub-option folders or patch files
        if not any(item.is_dir() or ".patch_" in str(item) for item in Path(mod_sub_dir).iterdir()):
            continue

        #extract pre-existing manifest option description
        sub_description = text_insert(
            prev_manifest, 
            f"""\n\t\t\t"Name": "{mod_sub_dir.name}",\n\t\t\t"Description": \"""", 
            """\",\n""", 
            "")
        
        #write new option in manifest.json file
        with open(f"{main_dir}/manifest.json", "a") as file:
            ins_str =   """\n\t\t{"""
            ins_str += f"""\n\t\t\t"Name": "{mod_sub_dir.name}","""
            ins_str += f"""\n\t\t\t"Description": "{sub_description}","""
            ins_str += image_insert(f"""\n\t\t\t"Image":""", main_dir, mod_sub_dir.stem)
            file.write(ins_str)
        
        #check if option folder has sub-option folders
        if any(item.is_dir() for item in Path(mod_sub_dir).iterdir()):
            #write new sub-options overhead in manifest.json file
            with open(f"{main_dir}/manifest.json", "a") as file:
                file.write("""\n\t\t\t"SubOptions": [""")

            #loop through sub-option folders
            for mod_subsub_dir in Path(mod_sub_dir).iterdir():
                #make sure it's a folder
                if Path(mod_subsub_dir).is_dir():
                    #exit if sub-option folder has internal folders (improper layout)
                    if any(item.is_dir() for item in mod_subsub_dir.iterdir()):
                        input("Folders nested incorrectly! Press any key to exit...")
                        sys.exit()
                    #skip if sub-option folder doesn't have patch files
                    elif not any(".patch_" in str(item) for item in Path(mod_subsub_dir).iterdir()):
                        continue

                    #extract pre-existing manifest sub-option description
                    sub_sub_description = text_insert(
                        prev_manifest, 
                        f"""\n\t\t\t\t\t"Name": "{mod_subsub_dir.name}",\n\t\t\t\t\t"Description": \"""", 
                        """\",\n""", 
                        "")
                    
                    #write new sub-option in manifest.json file
                    with open(f"{main_dir}/manifest.json", "a") as file:
                        ins_str =   """\n\t\t\t\t{"""
                        ins_str += f"""\n\t\t\t\t\t"Name": "{mod_subsub_dir.name}","""
                        ins_str += f"""\n\t\t\t\t\t"Description": "{sub_sub_description}","""
                        ins_str += image_insert(f"""\n\t\t\t\t\t"Image":""", main_dir, mod_subsub_dir.stem)
                        ins_str += f"""\n\t\t\t\t\t"Include": ["{mod_sub_dir.name}/{mod_subsub_dir.name}"]"""
                        ins_str +=  """\n\t\t\t\t},"""
                        file.write(ins_str)

            #write new sub-options closing brackets in manifest.json file
            with open(f"{main_dir}/manifest.json", "a") as file:
                file.write("""\n\t\t\t]""")
        #check if option folder has patch files
        elif any(".patch_" in str(item) for item in Path(mod_sub_dir).iterdir()):
            #write new option body in manifest.json file
            with open(f"{main_dir}/manifest.json", "a") as file:
                file.write(f"""\n\t\t\t"Include": ["{mod_sub_dir.name}"]""")
        
        #write new option closing brackets in manifest.json file
        with open(f"{main_dir}/manifest.json", "a") as file:
            file.write("""\n\t\t},""")

#write main closing brackets in manifest.json file
with open(f"{main_dir}/manifest.json", "a") as file:
    ins_str =  """\n\t]"""
    ins_str += """\n}"""
    file.write(ins_str)

input("Press any key to exit...")
