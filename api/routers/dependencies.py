from infrastructure.database.connector import DatabaseSingleton
from ipstack_client.ipstack_client import IPStackAPIClientSingleton


async def get_database():
    return DatabaseSingleton.get_instance()


async def get_ip_stack_client():
    return IPStackAPIClientSingleton.get_instance()
