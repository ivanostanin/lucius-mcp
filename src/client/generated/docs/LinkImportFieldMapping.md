# LinkImportFieldMapping


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items_separator** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**regex** | **bool** |  | [optional] 
**type** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.link_import_field_mapping import LinkImportFieldMapping

# TODO update the JSON string below
json = "{}"
# create an instance of LinkImportFieldMapping from a JSON string
link_import_field_mapping_instance = LinkImportFieldMapping.from_json(json)
# print the JSON string representation of the object
print(LinkImportFieldMapping.to_json())

# convert the object into a dict
link_import_field_mapping_dict = link_import_field_mapping_instance.to_dict()
# create an instance of LinkImportFieldMapping from a dict
link_import_field_mapping_from_dict = LinkImportFieldMapping.from_dict(link_import_field_mapping_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


