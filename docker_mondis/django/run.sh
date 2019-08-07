echo "Making Migrations..."
python /usr/src/mondis/mondis/manage.py makemigrations api --noinput

echo "Migrating..."
python /usr/src/mondis/mondis/manage.py migrate --noinput

echo "Run server..."
python /usr/src/mondis/mondis/manage.py runserver 0.0.0.0:8000
