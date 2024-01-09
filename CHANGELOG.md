2024/01/09 - RELEASE 2.0.1
==========================
- Adding missing dependency

2024/01/09 - RELEASE 2.0.0
==========================
- Major refactoring of the library
- Adding a script to set up a new tenant
- Support for async Client
- Introduction of token management and session handling (breaking change)
- Minor fixes and improvements
- Adding sample for async client
- Adding more unit tests

2023/7/13 - RELEASE 1.0.8
==========================
- Minor fix: No entities returned from Wikidata

2023/7/13 - RELEASE 1.0.7
==========================
- Minor fix: Unclosed file handle
- Ontology configuration update

2023/7/04 - RELEASE 1.0.6
==========================
- Improve handling of the ontology configuration file
- Handle aliases and labels in wikidata to thing mapping

2023/7/03 - RELEASE 1.0.5
==========================
- Ontology configuration file can be now defined as parameter
- Adding support for force parameter in delete group

2023/6/26 - RELEASE 1.0.4
==========================
- Minor fix: sendToNEL flag parse in entity pull
- Automatically fix issue with only alias for a language code defined in entity

2023/6/18 - RELEASE 1.0.3
==========================
- Minor fixe: State of thing object did not handle tenant access rights
- Adding support for fix ontology endpoint 
- Adding support for url data type in wikidata

2023/6/15 - RELEASE 1.0.2
==========================
- Minor fix: Update entity did ignore the sendToNEL flag

2023/6/15 - RELEASE 1.0.1
==========================
- Improve the wikidata scrapping 
- Refactoring typing
- pylint fixes
- Adding some helper functions for the entity management
- Fixing issues with unit tests
- Move Ontology classes to the ontology module

2023/5/23 - RELEASE 0.9.6
==========================
- Improve the session management
- Rename metaData tag to metadata
- Some fixes 

2023/4/24- RELEASE 0.9.5
==========================
- Adding some helper functions for the entity management 
- Fixing some issues with parameters, e.g., force in delete
- Introducing session with retry and backoff in case of private knowledge service is under load

2023/3/24- RELEASE 0.9.4
==========================
- Fixing named entity linking URL

2023/2/23- RELEASE 0.9.3
==========================
- REST API introduced versioning (v1), added the service endpoint constant in constructors
- Improvements in export entities script

2023/1/11- RELEASE 0.9.2
==========================
- Return datatime object rather than a str
- Adding several minor fixes

2022/11/30- RELEASE 0.9.1
==========================
- Adding helper functions for expiration date
- Fix of remove relation function

2022/11/23 - RELEASE 0.9.0
==========================
- Introduce refresh user flow

2022/11/19 - RELEASE 0.8.0
==========================
- Update all samples with the latest changes

2022/10/28 - RELEASE 0.7.1
==========================
- Minor fixes and updated samples

2022/10/26 - RELEASE 0.7.0
==========================
- Supporting the latest version of the service
- Remove the multiple contexts in ontology service
- Adding ownerID and group ids for entities

2022/09/20 - RELEASE 0.6.2
==========================
- Additional function to remove alias
- Fix group removal function

2022/08/26- RELEASE 0.6.1
==========================
- Fix parameters for object properties
- Adding push image functionality for local files

2022/08/09- RELEASE 0.6.0
==========================
- Improve consistency in parameter naming
- Adding visibility flag
- Adding delete concept and property functions
- Fix parameters for multiple domains

2022/07/03- RELEASE 0.5.0
==========================
- Update all samples and tools to pass the instance of the deployed service
- Check the supported languages

2022/03/31- RELEASE 0.4.0
==========================
- Properties can have now multiple domains and ranges.

2022/03/31- RELEASE 0.3.1
==========================
- Fix in ontology API.

2022/03/25- RELEASE 0.3.0
==========================
- Include API changes

2022/01/28- RELEASE 0.2.4
==========================
- Update library to work with the new deployment of Personal knowledge backend staging environment
- Adding User-Agent to request

2021/12/08- RELEASE 0.2.1
==========================
- Adding two functions to upload images for icons

2021/11/23- RELEASE 0.2.0
==========================
- Introducing data structures for user management
- Adding additional documentation
- Introducing group management

2021/11/19- RELEASE 0.1.5
==========================
- Refactoring the user management
- Adding wiki-data handling
- Integrating changes from Ontology services

2021/11/18- RELEASE 0.1.4
==========================
- Adding ontology class 
- Parse RDF export and create an ontology class
- Adding 

2021/11/10- RELEASE 0.1.2
==========================
- Adding support for ontology service. 
- Improving documentation
- Data structure refactoring

2021/11/05- RELEASE 0.1.1
==========================
First private release.