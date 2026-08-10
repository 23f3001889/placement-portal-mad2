"""
cache_keys.py
Centralizes cache key naming so @cache.cached prefixes & invalidation calls always stay consistent.

Cache TTL & Invalidation:
- all caches use a 5 min TTL. TTL is a fallbackif an invalidation is accidentally missed; 
- writes explicitly invalidate affected caches immediately.

student_drives:
- Only the unfiltered view (q='') is cached; search queries are not cached.
- Invalidated when a write changes whether a drive is Approved (approve/reject/bulk/delete, close/reopen)

admin_companies:
- Caches all q/status combinations.
- Invalidated on Company writes (approve/reject/blacklist/delete/bulk-status/self-registration).

admin_students:
- Caches all q combinations.
- Invalidated on Student writes (blacklist/delete/self-registration).
"""


from extensions import cache


def student_drives_key(q=''): 
    return f'student_drives_{q or "all"}'


def admin_companies_key(q='', status=''): #company_status
    return f'admin_companies_{q or "all"}_{status or "all"}'


def admin_students_key(q=''):
    return f'admin_students_{q or "all"}'


def safe_get(key):
    """on Redis read failure, fall back to a fresh DB query; not 500 to client"""
    try:
        return cache.get(key)
    except Exception as e:
        print(f'[CACHE WARNING] get({key!r}) failed: {e}')
        return None


def safe_set(key, value, timeout=300):
    """swallow Redis errors so cache failures never block valid responses frm the db"""
    try:
        cache.set(key, value, timeout=timeout)
    except Exception as e:
        print(f'[CACHE WARNING] set({key!r}) failed: {e}')


def safe_delete(key):
    """
    - Delete a cache key without letting Redis errors affect a successful write
    - called after commit; TTL is the fallback if deletion fails"""

    try:
        cache.delete(key)
    except Exception as e:
        print(f'[CACHE WARNING] delete({key!r}) failed: {e}')


def remember_key(namespace, key):
    """
    - track cache keys by namespace so all variants can be invalidated later (via invalidate_namespace())
    - called on cache misses; duplicate keys are ignored
    - Cache bookkeeping failures are swallowed so successful reads never return 500
    """
    try:
        tracked = cache.get(f'_tracked_{namespace}') or []
        if key not in tracked:
            tracked.append(key)
            cache.set(f'_tracked_{namespace}', tracked, timeout=600)
    except Exception as e:
        print(f'[CACHE WARNING] remember_key({namespace!r}) failed: {e}')


def invalidate_namespace(namespace):
    """
    - Clear all tracked cache keys in this namespace.
    - called from write routes (after commit) to invalidate all potentially stale variants
    - Redis failures must degrade to 'cache might be briefly stale until its TTL expires'
"""
    try:
        tracked = cache.get(f'_tracked_{namespace}') or []
        for key in tracked:
            cache.delete(key)
        cache.delete(f'_tracked_{namespace}')
    except Exception as e:
        print(f'[CACHE WARNING] invalidate_namespace({namespace!r}) failed: {e}')
