import json
from pathlib import Path
from typing import Dict, Any

if __name__ == '__main__':

    with Path('../pkl-cache/ontology_mapping.json').open('r') as fp:
        mapping_configuration: dict[str, Any] = json.load(fp)

        for json_file in Path('/Users/markus/develop/research/knowledge-graph-bootstrapper/ontology-mapping')\
                .glob('**/*.json'):
            print(f"Processing {json_file}")
            with json_file.open('r') as fp:
                configuration: dict[str, Any] = json.load(fp)
                for class_mapping in configuration['class-mapping']:
                    class_name: str = class_mapping['wacom-knowledge']
                    wikidata_classes: dict[str, Any] = class_mapping['wikidata']
                    if class_name in mapping_configuration['classes']:
                        class_configuration: dict[str, Any] = mapping_configuration['classes'][class_name]
                        for wikidata_class in wikidata_classes:
                            if wikidata_class not in class_configuration['wikidata_types']:
                                if wikidata_class not in class_configuration['wikidata_types']:
                                    class_configuration['wikidata_types'].append(wikidata_class)
                                print(f"Adding {wikidata_class} for class {class_name}")
                        for literal in class_mapping['literals']:
                            data_property_name: str = literal['wacom-knowledge']
                            if data_property_name in mapping_configuration['data_properties']:
                                data_configuration: dict[str, Any] = \
                                    mapping_configuration['data_properties'][data_property_name]
                                wikidata: str = literal['wikidata']
                                if wikidata not in data_configuration['wikidata_types']:
                                    if wikidata not in data_configuration['wikidata_types']:
                                        data_configuration['wikidata_types'].append(wikidata)
                                    print(f"Adding {wikidata} for data property {data_property_name}")

                        for relation in class_mapping['relations']:
                            object_property_name: str = relation['wacom-knowledge']
                            if object_property_name in mapping_configuration['object_properties']:
                                object_configuration: dict[str, Any] = \
                                    mapping_configuration['object_properties'][object_property_name]
                                wikidata: str = relation['wikidata']
                                if object_property_name not in object_configuration['wikidata_types']:
                                    if wikidata not in object_configuration['wikidata_types']:
                                        object_configuration['wikidata_types'].append(wikidata)
                                    print(f"Adding {wikidata} for object property {object_property_name}")
                    else:
                        print(f"Class {class_name} not found in configuration")

    with Path('../pkl-cache/ontology_mapping.json').open('w') as fp:
        json.dump(mapping_configuration, fp, indent=2)