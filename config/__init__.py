# Driver loader cho MySQL: Ưu tiên mysqlclient gốc (C-based, hiệu năng cao).
# Nếu môi trường không có mysqlclient, fallback sang pymysql và giả lập phiên bản tương thích Django.
try:
    import MySQLdb
except ImportError:
    try:
        import pymysql
        pymysql.version_info = (2, 2, 8, 'final', 0)
        pymysql.install_as_MySQLdb()
    except ImportError:
        pass

# Khởi tạo Celery Application khi Django khởi động (hỗ trợ tác vụ nền async)
try:
    from .celery import app as celery_app
    __all__ = ('celery_app',)
except ImportError:
    pass

