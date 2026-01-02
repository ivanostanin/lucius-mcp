# TestKeyImportFieldMapping


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**integration_id** | **int** |  | 
**items_separator** | **str** |  | [optional] 
**regex** | **bool** |  | [optional] 

## Example

```python
from src.client.generated.models.test_key_import_field_mapping import TestKeyImportFieldMapping

# TODO update the JSON string below
json = "{}"
# create an instance of TestKeyImportFieldMapping from a JSON string
test_key_import_field_mapping_instance = TestKeyImportFieldMapping.from_json(json)
# print the JSON string representation of the object
print(TestKeyImportFieldMapping.to_json())

# convert the object into a dict
test_key_import_field_mapping_dict = test_key_import_field_mapping_instance.to_dict()
# create an instance of TestKeyImportFieldMapping from a dict
test_key_import_field_mapping_from_dict = TestKeyImportFieldMapping.from_dict(test_key_import_field_mapping_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


