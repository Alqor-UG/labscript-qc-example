"""
The module that contains all the necessary logic for processing jobs in the database queue.
"""

from decouple import config

# import the storage provider that you would like to use
# currently we have dropbox and mongodb
from sqooler.storage_providers.mongodb import MongodbProvider
from sqooler.schemes import MongodbLoginInformation
from sqooler.utils import update_backends, main

from config import spooler_object  # pylint: disable=import-error

# configure the backends that are accessible to the maintainer
# typicall this is the spooler object from the experiment and only one backend is needed here.
backends = {
    "mot": spooler_object,
}
# configure the storage provider

mongodb_username = config("MONGODB_USERNAME")
mongodb_password = config("MONGODB_PASSWORD")
mongodb_database_url = config("MONGODB_DATABASE_URL")
login_dict = {
    "mongodb_username": mongodb_username,
    "mongodb_password": mongodb_password,
    "mongodb_database_url": mongodb_database_url,
}
mongodb_login = MongodbLoginInformation(**login_dict)
storage_provider = MongodbProvider(mongodb_login)

print("Update")
update_backends(storage_provider, backends)
print("Now run as usual.")
main(storage_provider, backends)
