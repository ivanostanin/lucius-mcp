# CustomFieldImportFieldMapping


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**custom_field_id** | **int** |  | 
**items_separator** | **str** |  | [optional] 
**regex** | **bool** |  | [optional] 

## Example

```python
from src.client.generated.models.custom_field_import_field_mapping import CustomFieldImportFieldMapping

# TODO update the JSON string below
json = "{}"
# create an instance of CustomFieldImportFieldMapping from a JSON string
custom_field_import_field_mapping_instance = CustomFieldImportFieldMapping.from_json(json)
# print the JSON string representation of the object
print(CustomFieldImportFieldMapping.to_json())

# convert the object into a dict
custom_field_import_field_mapping_dict = custom_field_import_field_mapping_instance.to_dict()
# create an instance of CustomFieldImportFieldMapping from a dict
custom_field_import_field_mapping_from_dict = CustomFieldImportFieldMapping.from_dict(custom_field_import_field_mapping_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


