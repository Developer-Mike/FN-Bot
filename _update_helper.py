import requests, zipfile, io, os, shutil, glob, tempfile, dotenv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(CURRENT_DIR)

BACKUP_ZIP_PATH = os.path.join(CURRENT_DIR, "old.zip")
TEMP_DIR = os.path.join(CURRENT_DIR, "temp")
ASSETS_DIR = os.path.join(CURRENT_DIR, "assets")
OLD_DOT_ENV_PATH = os.path.join(CURRENT_DIR, "old.env")
DOT_ENV_PATH = os.path.join(CURRENT_DIR, ".env")
GITHUB_REPO_URL = "https://github.com/Developer-Mike/FN-Bot/archive/refs/heads/main.zip"

# Backup files
if os.path.exists(BACKUP_ZIP_PATH):
    os.remove(BACKUP_ZIP_PATH)

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
if os.path.exists(OLD_DOT_ENV_PATH): os.remove(OLD_DOT_ENV_PATH) 
os.rename(DOT_ENV_PATH, OLD_DOT_ENV_PATH)

dotenv.load_dotenv(OLD_DOT_ENV_PATH)
shutil.move(TEMPLATE_DOT_ENV_PATH, DOT_ENV_PATH)

with open(DOT_ENV_PATH, "r") as env_file:
    new_env = env_file.readlines()

with open(DOT_ENV_PATH, "w") as env_file:
    for i, line in enumerate(new_env):
        if line.startswith("#") or line == "":
            continue
        key = line.split("=")[0]

        if key in os.environ:
            new_env[i] = f"{key}={os.environ[key]}\n"

    env_file.write("".join(new_env))

shutil.rmtree(TEMP_DIR)