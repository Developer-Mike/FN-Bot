import requests, zipfile, io, os, shutil, glob, re, tempfile
from dotenv import load_dotenv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(CURRENT_DIR)

BACKUP_ZIP_PATH = os.path.join(CURRENT_DIR, "old.zip")
TEMP_DIR = os.path.join(CURRENT_DIR, "temp")
ASSETS_DIR = os.path.join(CURRENT_DIR, "assets")
OLD_DOT_ENV_PATH = os.path.join(CURRENT_DIR, "old.env")
DOT_ENV_PATH = os.path.join(CURRENT_DIR, ".env")
GITHUB_REPO_URL = "https://github.com/Developer-Mike/FN-Bot/archive/refs/heads/main.zip"

# Backup files
shutil.rmtree(BACKUP_ZIP_PATH, ignore_errors=True)
with tempfile.TemporaryDirectory() as temp_dir:
    BACKUP_ZIP_TEMP_PATH = shutil.make_archive(os.path.join(temp_dir, "old"), "zip", CURRENT_DIR)
    shutil.move(BACKUP_ZIP_TEMP_PATH, BACKUP_ZIP_PATH)

# Download new files
r = requests.get(GITHUB_REPO_URL)
zip = zipfile.ZipFile(io.BytesIO(r.content))
zip.extractall(TEMP_DIR)

NEW_DIR = os.path.join(TEMP_DIR, os.listdir(TEMP_DIR)[0])
TEMPLATE_DOT_ENV_PATH = os.path.join(NEW_DIR, "template.env")

# Check if new version is available
with open(os.path.join(CURRENT_DIR, "version.txt"), "r") as version_file:
    current_version = version_file.read().strip()
with open(os.path.join(NEW_DIR, "version.txt"), "r") as version_file:
    new_version = version_file.read().strip()

if current_version == new_version:
    print("You are already on the latest version.")
    exit()

# Update py files
for source_path in glob.glob(os.path.join(NEW_DIR, "**"), recursive=True):
    target_path = source_path.replace(NEW_DIR, CURRENT_DIR)

    # Skip directories
    if os.path.isdir(source_path):
        continue

    # Skip update helper
    if os.path.basename(source_path) == os.path.basename(__file__):
        continue

    # Dont replace assets
    if target_path.startswith(ASSETS_DIR) and os.path.exists(target_path):
        continue
        
    shutil.copy(source_path, target_path)

# Update env file
os.rename(DOT_ENV_PATH, OLD_DOT_ENV_PATH)
OLD_DOT_ENV = load_dotenv(OLD_DOT_ENV_PATH)
shutil.move(TEMPLATE_DOT_ENV_PATH, DOT_ENV_PATH)

with open(DOT_ENV_PATH, "rw") as env_file:
    new_env = env_file.read()

    for key, value in OLD_DOT_ENV.items():
        new_env = re.sub(f"{key}=*\n", f"{key}={value}\n", new_env)

    env_file.write(new_env)

shutil.rmtree(OLD_DOT_ENV)
shutil.rmtree(TEMP_DIR)