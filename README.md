CLOUDINARY_CLOUD_NAME=""
CLOUDINARY_API_KEY=""
CLOUDINARY_API_SECRET=""
DB_NAME=""
DB_USER=""
DB_PASSWORD=""
DB_HOST=""
DB_PORT=""
NUBEFACT_URL=""
NUBEFACT_TOKEN=""
MP_ACCESS_TOKEN=""

python -m venv myenv
pip install -r requirements. txt
python manage.py migrate
