python manage.py makemigrations parameter xauth 
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py populate
python manage.py runserver