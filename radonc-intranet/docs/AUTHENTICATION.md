# Authentication

Out of the box the site uses Django's built-in user accounts (`/admin/` to create users, `bootstrap_site` to create groups). Every page requires login via `LoginRequiredMiddleware`. For a hospital deployment you'll almost certainly want Active Directory.

## Active Directory via LDAP (django-auth-ldap)

1. Uncomment `django-auth-ldap` (and install the `python-ldap` system prerequisites) in `requirements.txt`, then `pip install -r requirements.txt`.

2. Add to `config/settings/prod.py` (values via environment variables — never commit credentials):

```python
import ldap
from django_auth_ldap.config import LDAPSearch, GroupOfNamesType, ActiveDirectoryGroupType

AUTH_LDAP_SERVER_URI = env("LDAP_SERVER_URI")            # ldaps://dc01.hospital.local
AUTH_LDAP_BIND_DN = env("LDAP_BIND_DN")                  # service account
AUTH_LDAP_BIND_PASSWORD = env("LDAP_BIND_PASSWORD")

AUTH_LDAP_USER_SEARCH = LDAPSearch(
    "OU=Staff,DC=hospital,DC=local",
    ldap.SCOPE_SUBTREE,
    "(sAMAccountName=%(user)s)",
)

AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
    "OU=Groups,DC=hospital,DC=local",
    ldap.SCOPE_SUBTREE,
    "(objectClass=group)",
)
AUTH_LDAP_GROUP_TYPE = ActiveDirectoryGroupType()

# Map AD groups onto the site's Django groups
AUTH_LDAP_MIRROR_GROUPS = False
AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    "is_staff": "CN=RadOnc-Admins,OU=Groups,DC=hospital,DC=local",
}
AUTH_LDAP_FIND_GROUP_PERMS = True

AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
}

AUTHENTICATION_BACKENDS = [
    "django_auth_ldap.backend.LDAPBackend",
    "django.contrib.auth.backends.ModelBackend",   # keep for local/admin fallback
]
```

3. To map AD security groups to the site groups (Physics, Reporting Access, ...), either name your AD groups identically and use `AUTH_LDAP_MIRROR_GROUPS = True`, or use a small signal on first login to translate names.

## Alternatives

- **Windows Integrated Auth / SSO:** front the app with IIS and use `RemoteUserMiddleware` + `RemoteUserBackend` so the domain login passes straight through (no password prompt). Good fit if the site lives on an IIS box already.
- **SAML / Entra ID:** if the hospital is on Entra (Azure AD), `python3-saml` or `mozilla-django-oidc` work; the rest of the site doesn't care which backend authenticates the user.

## Group reference

| Group | Grants |
|---|---|
| Physics, Dosimetry, Therapists | Organizational; available for gating future features |
| Reporting Access | Reporting section (`/reports/`) |
| Content Admins | Intended for staff who manage links/contacts in `/admin/` (pair with `is_staff` + model permissions) |
