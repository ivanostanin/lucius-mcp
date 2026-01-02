# TagImportFieldMapping


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items_separator** | **str** |  | [optional] 
**prefix** | **str** |  | [optional] 
**regex** | **bool** |  | [optional] 

## Example

```python
from src.client.generated.models.tag_import_field_mapping import TagImportFieldMapping

# TODO update the JSON string below
json = "{}"
# create an instance of TagImportFieldMapping from a JSON string
tag_import_field_mapping_instance = TagImportFieldMapping.from_json(json)
# print the JSON string representation of the object
print(TagImportFieldMapping.to_json())

# convert the object into a dict
tag_import_field_mapping_dict = tag_import_field_mapping_instance.to_dict()
# create an instance of TagImportFieldMapping from a dict
tag_import_field_mapping_from_dict = TagImportFieldMapping.from_dict(tag_import_field_mapping_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


