# Matrimony API Reference

This API serves staff clients in React, Android, and tools such as Postman. Both apps use the same profile and staff-management endpoints. Authentication transport differs: Android uses Bearer tokens; the browser uses JWT cookies.

## Connection Basics

- Local base URL: `http://127.0.0.1:8000`
- Android emulator base URL: `http://10.0.2.2:8000`
- Physical devices: use the computer's LAN IP, run Django on `0.0.0.0:8000`, and allow that host in Django settings.
- Production: use your deployed HTTPS base URL.
- All paths below include `/api/` and end with `/`.
- JSON requests use `Content-Type: application/json`. File uploads use `multipart/form-data`.
- UUIDs and tokens in examples are placeholders. Use values returned by your server.

## Endpoint Summary

| Method | Path | Purpose | Access |
| --- | --- | --- | --- |
| GET | `/api/auth/csrf/` | Initialize CSRF cookie | No login required |
| POST | `/api/auth/login/` | Obtain JSON JWTs | No login required |
| POST | `/api/auth/browser-login/` | Sign in with JWT cookies | No login required |
| POST | `/api/auth/refresh/` | Refresh JSON JWTs | Valid refresh token |
| POST | `/api/auth/browser-refresh/` | Refresh JWT cookies | Valid refresh cookie |
| POST | `/api/auth/logout/` | Blacklist a refresh token | Authenticated |
| POST | `/api/auth/browser-logout/` | Blacklist refresh token and clear cookies | Authenticated |
| GET | `/api/auth/me/` | Read current staff account | Authenticated |
| GET | `/api/admins/` | List staff accounts | Active SUPER_ADMIN |
| POST | `/api/admins/` | Create staff account | Active SUPER_ADMIN |
| GET | `/api/profiles/` | List/search profiles | Active ADMIN or SUPER_ADMIN |
| POST | `/api/profiles/` | Create profile | Active ADMIN or SUPER_ADMIN |
| GET | `/api/profiles/<uuid>/` | Read profile | Active ADMIN or SUPER_ADMIN |
| PATCH | `/api/profiles/<uuid>/` | Update profile | Active ADMIN or SUPER_ADMIN |

These are staff APIs, not public candidate registration or browsing APIs. `OPTIONS` is also available through DRF; `HEAD` accompanies GET views.

## Authentication

### Android and Postman

1. Log in using `/api/auth/login/`.
2. Send the access token on protected requests:

```http
Authorization: Bearer <access-token>
```

3. When access expires, call `/api/auth/refresh/` and store both returned tokens.
4. On logout, blacklist the refresh token and discard both local tokens.

Access tokens last 15 minutes; refresh tokens last 7 days. Refresh rotation is enabled: the submitted refresh token is blacklisted after a successful refresh. Always replace it with the new refresh token.

### React and Browser Clients

1. Call `/api/auth/csrf/` to obtain the `csrftoken` cookie.
2. Call `/api/auth/browser-login/` with email/password.
3. Use `credentials: 'include'` in fetch requests to send cookies.
4. The frontend sends `X-CSRFToken` from `csrftoken` on requests, including writes.
5. Call `/api/auth/browser-refresh/` when access expires, then retry the protected request.
6. Call `/api/auth/browser-logout/` to blacklist refresh and clear JWT cookies.

`access_token` and `refresh_token` cookies are HttpOnly, have `SameSite=Lax`, and use path `/`. They use `Secure` when Django `DEBUG=False`; local debug cookies do not. Cookie maximum ages match the token lifetimes above. Keep browser/API deployment compatible with these cookie and CORS settings; arbitrary cross-site deployments are not supported by this configuration.

**Current security limitation:** cookie JWT authentication does not itself enforce CSRF validation. DRF session authentication does enforce CSRF for authenticated session requests. Sending a CSRF header alone does not establish backend enforcement; this needs hardening before production use.

Bearer authentication takes precedence when an Authorization header is present. Do not send stale Authorization headers/cookies to login or refresh endpoints: authentication can reject a request even when its permission allows anonymous access. Django session authentication is also enabled for protected APIs.

### GET /api/auth/csrf/

No body. Returns `200 OK`, sets `csrftoken`, and responds:

```json
{"detail": "CSRF cookie set."}
```

### POST /api/auth/login/

Both fields are required. The account must be active (`is_active=true`, `status=ACTIVE`).

```json
{"email": "admin@example.com", "password": "your-password"}
```

Returns `200 OK`:

```json
{"access": "<access-token>", "refresh": "<refresh-token>", "user": {"id": "<staff-uuid>", "email": "admin@example.com", "first_name": "", "last_name": "", "phone": "", "role": "ADMIN", "status": "ACTIVE", "is_active": true, "created_at": "2026-11-06T10:00:00Z", "updated_at": "2026-11-06T10:00:00Z"}}
```

Missing credentials return `400` with `Email and password are required.` Invalid credentials or an inactive account return `401` with `Invalid credentials.`

### POST /api/auth/browser-login/

Same JSON input and credential validation as login. Returns `200 OK`, sets both JWT cookies, and responds:

```json
{"detail": "Logged in successfully.", "user": {"id": "<staff-uuid>", "email": "admin@example.com", "first_name": "", "last_name": "", "phone": "", "role": "ADMIN", "status": "ACTIVE", "is_active": true, "created_at": "2026-11-06T10:00:00Z", "updated_at": "2026-11-06T10:00:00Z"}}
```

Login does not return JWTs in this response body.

### POST /api/auth/refresh/

No access token is required. Send JSON:

```json
{"refresh": "<current-refresh-token>"}
```

Returns `200 OK`:

```json
{"access": "<new-access-token>", "refresh": "<new-refresh-token>"}
```

Missing refresh returns `400` field validation errors; expired, invalid, or blacklisted tokens return `401`. A refresh token cannot be used as a Bearer access token.

### POST /api/auth/browser-refresh/

No body is needed. Reads `refresh_token` from cookies, rotates the token, and updates both JWT cookies. Currently also returns `access` and `refresh` in JSON, in the same shape as the JSON refresh endpoint. Browser clients can rely on cookies instead of storing these response tokens.

Returns `200` on success, `400` if the refresh cookie is missing (`Refresh token is required.`), or `401` for an invalid/expired/blacklisted refresh token.

### POST /api/auth/logout/

Requires authentication with a valid access token (or another enabled authentication method) and a refresh token belonging to the same user:

```json
{"refresh": "<current-refresh-token>"}
```

Blacklists refresh and returns `205 Reset Content`. Treat this as success without relying on a response body. Missing refresh returns `400` with `{"refresh": "This field is required."}`. Invalid/expired refresh or a token owned by another user returns `400` with a `detail` message.

Logout does not revoke an already-issued access token: it remains valid until expiry. If access has expired, refresh it before making an authenticated logout request.

### POST /api/auth/browser-logout/

Requires authentication. Reads the refresh cookie first, or falls back to a JSON `refresh` field. Checks token ownership, blacklists refresh, and clears both JWT cookies on success (`205`). Missing refresh or invalid/expired/wrong-owner refresh returns `400`; those error responses do not clear cookies.

### GET /api/auth/me/

No body. Returns `200` with the staff user object shown in login responses, without an outer `user` wrapper. Passwords and tokens are not included. Authentication failure normally returns `401`.

## Staff Management

Both operations require an authenticated active `SUPER_ADMIN`. These APIs do not expose staff detail/update/delete routes.

### GET /api/admins/

Returns `200` with paginated staff user objects. Despite the URL name, the list contains all staff accounts, including super admins and disabled accounts, ordered newest first. Optional `page` defaults to 1; page size is 20. There is no search/status filter on this endpoint.

### POST /api/admins/

Creates a staff account. Required: unique valid `email` and `password` (minimum 8 characters). Optional: `first_name`, `last_name`, `phone` (maximum 20 characters), `role` (`ADMIN` or `SUPER_ADMIN`, default `ADMIN`), and `status` (`INVITED`, `ACTIVE`, or `DISABLED`, default `ACTIVE`). Passwords are hashed and never returned. This serializer checks password length; it does not run Django's full configured password-validator suite.

```json
{"email": "new-admin@example.com", "password": "example-password-123", "first_name": "Maya", "last_name": "Rao", "phone": "", "role": "ADMIN", "status": "ACTIVE"}
```

Returns `201 Created` with the staff user object. Invalid fields or duplicate email return `400`. The caller is recorded as the creator internally.

## Profiles

All profile operations require an authenticated, active `ADMIN` or `SUPER_ADMIN`. There is currently no per-profile assignment restriction: either role can access the profile collection.

### GET /api/profiles/

Returns `200` with profiles ordered by `created_at` descending, then ID descending. Query parameters:

| Parameter | Meaning |
| --- | --- |
| `page` | Page number, default 1; page size 20 |
| `search` | Search profile code, full name, profession, and mother tongue |

Example: `/api/profiles/?page=1&search=maya`. The API currently has no `status` filter, even though the legacy HTML list does.

Both profile and staff lists use this response envelope:

```json
{"count": 1, "next": null, "previous": null, "results": []}
```

`results` contains the matching objects (empty in this shape-only example); `count` is the total matching records, not the current page size. `next`/`previous` contain page URLs or null. An invalid/out-of-range page returns `404`.

### POST /api/profiles/

Creates a profile. Required: unique `profile_code` and `full_name`. Example without photos:

```json
{
  "profile_code": "P-4001",
  "full_name": "Maya Rao",
  "gender": "female",
  "date_of_birth": "1998-04-12",
  "height_cm": "165.5",
  "weight_kg": "58.2",
  "profession": "Software engineer",
  "income_range": "10_TO_20_LPA",
  "religion": "Hindu",
  "caste": "",
  "marital_status": "Never married",
  "mother_tongue": "Kannada",
  "status": "DRAFT",
  "about_me": "Enjoys music and travel."
}
```

Returns `201` with the saved profile object, including its UUID. Creator ID/name and timestamps are filled by the server. Invalid fields, duplicate code, invalid images, or more than five total photos return `400`.

### GET /api/profiles/<uuid>/

No body. Returns `200` with one profile object. A nonexistent UUID returns `404`. Use the `id` from create/list, not `profile_code`, in the URL.

Example response (illustrative values):

```json
{
  "id": "<profile-uuid>",
  "profile_code": "P-4001",
  "full_name": "Maya Rao",
  "primary_photo": null,
  "primary_photo_url": "",
  "gallery_images": [],
  "gender": "female",
  "date_of_birth": "1998-04-12",
  "age": 28,
  "height_cm": "165.5",
  "weight_kg": "58.2",
  "profession": "Software engineer",
  "income_range": "10_TO_20_LPA",
  "religion": "Hindu",
  "caste": "",
  "marital_status": "Never married",
  "mother_tongue": "Kannada",
  "status": "DRAFT",
  "about_me": "Enjoys music and travel.",
  "profile_created_by": "SELF",
  "consent_status": "PENDING",
  "consent_version": "",
  "consent_at": null,
  "created_by_name": "admin@example.com",
  "created_by": "<staff-uuid>",
  "updated_by_name": "admin@example.com",
  "updated_by": "<staff-uuid>",
  "assigned_to": null,
  "created_at": "2026-11-06T10:00:00Z",
  "updated_at": "2026-11-06T10:00:00Z"
}
```

### PATCH /api/profiles/<uuid>/

Updates only supplied fields and returns `200` with the updated object. Omitted fields stay unchanged. Send an empty string to clear blankable text fields; send JSON null to clear nullable fields.

```json
{"profession": "Product designer", "status": "APPROVED", "about_me": "Updated description."}
```

Archive without deleting using `{"status": "ARCHIVED"}`. This changes status only; it does not populate internal archive timestamps/actor fields. Archived profiles remain in lists. No status-transition approval workflow is enforced beyond validating the status choice.

`PUT` and `DELETE` are not registered and return `405` for an authorized request. No gallery-delete/reorder/caption-update endpoint is registered.

### Profile Field Reference

| Field | Input rules / response meaning |
| --- | --- |
| `profile_code` | Required on create, unique text, maximum 25 characters |
| `full_name` | Required on create, text, maximum 200 characters |
| `gender` | `male`, `female`, `other`, or blank |
| `date_of_birth` | `YYYY-MM-DD` or null |
| `height_cm` | Decimal string/number or null; 4 total digits, 1 decimal place |
| `weight_kg` | Decimal string/number or null; minimum 0.1, 5 total digits, 1 decimal place |
| `profession` | Text, maximum 120 characters, blank allowed |
| `income_range` | Choice below, or blank |
| `religion`, `caste`, `mother_tongue` | Text, maximum 80 characters each, blank allowed |
| `marital_status` | Free text, maximum 30 characters, blank allowed |
| `status` | `DRAFT` (default), `PENDING_REVIEW`, `APPROVED`, `REJECTED`, `ARCHIVED` |
| `about_me` | Text, blank allowed |
| `profile_created_by` | Text, maximum 30 characters, default `SELF` |
| `consent_status` | Text, maximum 30 characters, default `PENDING` |
| `consent_version` | Text, maximum 50 characters, blank allowed |
| `consent_at` | ISO 8601 datetime or null |
| `assigned_to` | Existing staff UUID or null |
| `primary_photo` | Image upload; response contains image URL or null; JSON null clears it |
| `additional_photos` | Write-only list of image uploads, appended to gallery |
| `gallery_images` | Read-only image objects: `id`, `image`, `image_url`, `is_primary`, `caption`, `created_at` |
| `id`, `age`, `primary_photo_url` | Read-only UUID, calculated age (or null), and photo URL (or empty string) |
| `created_by`, `created_by_name` | Read-only creator UUID (possibly null) and saved creator name/email; the name remains if the staff account is deleted |
| `updated_by`, `updated_by_name` | Read-only last-updater UUID (possibly null) and saved updater name/email; updated on each create or edit, and the name remains if the staff account is deleted |
| `created_at`, `updated_at` | Read-only ISO 8601 timestamps |

Income choices: `BELOW_3_LPA`, `3_TO_5_LPA`, `5_TO_10_LPA`, `10_TO_20_LPA`, `20_TO_50_LPA`, `ABOVE_50_LPA`, `PREFER_NOT_TO_SAY`. LPA means lakh INR per year.

### Uploading and Displaying Photos

Use multipart form data for create or PATCH. Add text fields normally, `primary_photo` as one file, and repeat `additional_photos` for each gallery file. Let Postman/fetch/curl generate the Content-Type boundary; do not manually set a bare multipart header.

```bash
curl -X POST http://127.0.0.1:8000/api/profiles/ \
  -H 'Authorization: Bearer <access-token>' \
  -F 'profile_code=P-4002' \
  -F 'full_name=Photo Candidate' \
  -F 'primary_photo=@/path/to/primary.png' \
  -F 'additional_photos=@/path/to/gallery-1.png' \
  -F 'additional_photos=@/path/to/gallery-2.png'
```

A profile may contain at most five photos total, counting primary, existing gallery, and new gallery uploads. PATCH appends gallery photos, not replaces them. Read returned `primary_photo_url` and gallery `image_url` to render images; do not submit an S3 URL as a new image upload.

URLs are generated by configured storage. Profile storage currently produces unsigned S3 URLs; an API response containing a URL does not guarantee the object is publicly readable. S3 access errors require checking storage/object access configuration, not the JWT header on the profile API. No signed-image URL endpoint is implemented.

## Errors

| Status | Typical meaning |
| --- | --- |
| 400 | Invalid/missing fields, duplicate email/code, invalid logout refresh, photo limit exceeded |
| 401 | Missing/invalid/expired access authentication or invalid refresh token |
| 403 | Authenticated user lacks active role permission, or session CSRF check fails |
| 404 | Unknown profile, unknown route, or invalid page |
| 405 | Method not registered (for example profile DELETE/PUT) |
| 415 | Unsupported request Content-Type |

Errors may use `detail`, individual field keys, or `non_field_errors`; do not assume every error has `detail`.

```json
{"profile_code": ["profile with this profile code already exists."]}
```

```json
{"additional_photos": ["A profile can have no more than 5 photos total."]}
```

## Postman Quick Test

1. Start Django with `python manage.py runserver` and create/use an active staff account.
2. Create environment variables `base_url=http://127.0.0.1:8000`, `access_token`, `refresh_token`, and `profile_id`.
3. POST `{{base_url}}/api/auth/login/` with raw JSON credentials. Save returned tokens in the environment.
4. For protected requests, choose Authorization > Bearer Token > `{{access_token}}`.
5. GET `{{base_url}}/api/auth/me/` and GET `{{base_url}}/api/profiles/`; expect `200`.
6. POST a profile with raw JSON (or form-data for files); expect `201`. Save its `id` as `profile_id`.
7. GET/PATCH `{{base_url}}/api/profiles/{{profile_id}}/`; expect `200` and verify saved values.
8. POST refresh with `{"refresh":"{{refresh_token}}"}` using No Auth. Save both replacement tokens.
9. POST logout with Bearer access and the current refresh token; expect `205`. Reusing that refresh should fail.
10. Test missing auth, invalid fields, and a sixth photo to confirm error handling. Use a SUPER_ADMIN account for `/api/admins/`.

For browser-flow testing, use Postman's cookie jar: request CSRF, browser-login, then protected endpoints without a Bearer header. Include `X-CSRFToken` from the cookie for writes to mirror the React client. Do not mix the JSON and browser flows accidentally through leftover cookies.

Postman isolates backend behavior from UI behavior and is useful for debugging. It complements, but does not replace, automated tests.

## Non-API Routes and Unimplemented Features

`/`, `/profiles/`, `/profiles/add/`, `/profiles/<uuid>/`, `/profiles/<uuid>/edit/`, and `/admin/` are legacy HTML/admin pages, not JSON APIs. Their Django session login is separate from JWT browser login.

Payments, verification, audit, and biodata have no routes registered under `/api/` yet. There are also no public signup, candidate login, staff update/delete, or profile photo deletion APIs currently.