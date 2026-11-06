# Matrimony Dashboard

A Django-based matrimony staff dashboard and API foundation built for the requirements described in the project specification.

## Stack
- Django 5
- Django REST Framework
- PostgreSQL-ready configuration
- Private file storage oriented design
- Custom staff auth with Super Admin/Admin roles

## Getting started

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Notes
- The project enforces a no-delete policy for profile records in the API layer.
- The initial implementation focuses on the core project foundation and the first protected profile endpoints.

## API Documentation

See [the API reference](docs/API.md) for all registered endpoints, browser and Android authentication, request/response examples, profile fields, image uploads, permissions, errors, and Postman testing steps.

## Android API

The API is for staff/admin clients. Sign in with an active staff account; profile endpoints require the `ADMIN` or `SUPER_ADMIN` role. Use HTTPS outside local development.

For the Android Studio emulator, use `http://10.0.2.2:8000` as the development host. A physical device should use the development computer's LAN IP, with Django listening on `0.0.0.0:8000` and that host allowed by `ALLOWED_HOSTS`.

### Authentication

`POST /api/auth/login/` accepts JSON:

```json
{"email":"admin@example.com","password":"your-password"}
```

It returns `access`, `refresh`, and `user`. Send the access token on protected requests:

```http
Authorization: Bearer <access-token>
```

Refresh an access token with `POST /api/auth/refresh/` and `{"refresh":"<refresh-token>"}`. Log out with `POST /api/auth/logout/`, the Bearer access token, and `{"refresh":"<refresh-token>"}`. Refresh tokens are rotated and blacklisted on logout. `GET /api/auth/me/` returns the authenticated staff account.

### Profiles

- `GET /api/profiles/?page=1&search=maya` lists profiles with pagination and optional search across name, code, profession, and mother tongue.
- `POST /api/profiles/` creates a profile.
- `GET /api/profiles/<uuid>/` retrieves a profile.
- `PATCH /api/profiles/<uuid>/` updates a profile.
- `DELETE` is intentionally unavailable; archive or change profile status instead.

Profile fields are returned as JSON. The response includes `primary_photo` and `gallery_images`. For image uploads, send `multipart/form-data`; use `primary_photo` for the main image and repeat the `additional_photos` field for gallery images. A profile allows up to five photos total. Gallery uploads are returned in `gallery_images` after saving.
