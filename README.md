# IP Locator

## Run instructions
### Create file with environment variables
#### File `.environment_variables`:
```aiignore
IPSTACK_KEY=<ip_stack_key>
DATABASE_URI=<database_uri_with_async_driver_for_sqlalchemy>
```
Supported databases and drivers are:
 - postgresql+asyncpg
 - sqlite+aiosqlite

### Build and run Docker image
```aiignore
docker build -t ip_locator:latest .
docker run --env-file=<path_to_.environment_variables_file> -p 8080:8080 ip_locator:latest
```

## Links
 - API docs: `<host>/docs`
