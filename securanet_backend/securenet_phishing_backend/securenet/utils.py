from django.db import connection

def get_db_handle():
    """
    Returns the active Django database connection.
    Use this if you need to run raw SQL queries
    outside of Django's ORM.
    """
    return connection
