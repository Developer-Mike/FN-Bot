import os, zipfile
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ignored_files = []
ignored_dirs = ['__pycache__', 'temp', '.vscode', '_upload_helper']
def valid_file(filename):
    for file in ignored_files:
        if file == filename:
            return False

    for dir in ignored_dirs:
        if dir in os.path.normpath(filename).split(os.sep):
            return False
    return True
    

path_list = [] # Make an array string with all paths to files
for root, directories, files in os.walk(os.getcwd()): # Scans for all subfolders and files in MyDirectoryPath
        for filename in files: # loops for every file
            file_path = os.path.relpath(os.path.join(root, filename), os.getcwd()) # Joins both the directory and the file name
            path_list.append(file_path) # appends to the array
filtered_paths = list(filter(valid_file, path_list))

with zipfile.ZipFile('_upload_helper/_upload.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
    for path in filtered_paths:
        zipf.write(path)