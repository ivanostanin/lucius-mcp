# CustomFieldExportFieldMapping


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_field** | **object** |  | [optional] 
**name** | **str** |  | [optional] 
**custom_field_id** | **int** |  | 
**items_separator** | **str** |  | 

## Example

```python
from src.client.generated.models.custom_field_export_field_mapping import CustomFieldExportFieldMapping

# TODO update the JSON string below
json = "{}"
# create an instance of CustomFieldExportFieldMapping from a JSON string
custom_field_export_field_mapping_instance = CustomFieldExportFieldMapping.from_json(json)
# print the JSON string representation of the object
print(CustomFieldExportFieldMapping.to_json())

# convert the object into a dict
custom_field_export_field_mapping_dict = custom_field_export_field_mapping_instance.to_dict()
# create an instance of CustomFieldExportFieldMapping from a dict
custom_field_export_field_mapping_from_dict = CustomFieldExportFieldMapping.from_dict(custom_field_export_field_mapping_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


