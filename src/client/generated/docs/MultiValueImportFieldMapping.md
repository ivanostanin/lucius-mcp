# MultiValueImportFieldMapping


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items_separator** | **str** |  | [optional] 
**regex** | **bool** |  | [optional] 

## Example

```python
from src.client.generated.models.multi_value_import_field_mapping import MultiValueImportFieldMapping

# TODO update the JSON string below
json = "{}"
# create an instance of MultiValueImportFieldMapping from a JSON string
multi_value_import_field_mapping_instance = MultiValueImportFieldMapping.from_json(json)
# print the JSON string representation of the object
print(MultiValueImportFieldMapping.to_json())

# convert the object into a dict
multi_value_import_field_mapping_dict = multi_value_import_field_mapping_instance.to_dict()
# create an instance of MultiValueImportFieldMapping from a dict
multi_value_import_field_mapping_from_dict = MultiValueImportFieldMapping.from_dict(multi_value_import_field_mapping_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


