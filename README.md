# sz_init_postgresql-v4

# Overview
Creates a v4 schema, sets an initial default configuration, and then tests initializing an engine.

This can be called multiple times and it will skip steps it believes have been successfully completed.  It
will always attempt to initialize the engine and output the engine version.

# API demonstrated
### Core
* szconfigmanager.get_default_config_id: Retrieves the ID of any currently installed ER configuration
* szconfigmanager.add_config: Adds the ER configuration to the Senzing repository, returning the ID
* szconfigmanager.set_default_config_id: Sets the configuration ID as the default for the repository
* szconfig.create_config(): Creates a new config based on the product's template
* szconfig.export_config(): Exports the ER configuration as JSON string
* szengine.prime_engine(): Explicitly completes the full initialization of the core engine
### Supporting
* senzing_core.SzAbstractFactory: To initialize the Sz environment
* szproduct.get_version(): Returns the JSON product verson string

For more details on the Senzing SDK go to https://docs.senzing.com

# Details

### Required parameter (environment)
```
SENZING_ENGINE_CONFIGURATION_JSON
```

## Building/Running
```
docker build -t brian/sz_init_postgresql-v4 .
docker run --user $UID -it -e SENZING_ENGINE_CONFIGURATION_JSON brian/sz_init_postgresql-v4
```

## Additional items to note
 * Does not support non-default schemas
 * Does not support Senzing database clustering
 * Does not support upgrades 
