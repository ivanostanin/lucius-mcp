# RoleExportFieldMapping


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_field** | **object** |  | [optional] 
**name** | **str** |  | [optional] 
**items_separator** | **str** |  | 
**role_id** | **int** |  | 

## Example

```python
from src.client.generated.models.role_export_field_mapping import RoleExportFieldMapping

# TODO update the JSON string below
json = "{}"
# create an instance of RoleExportFieldMapping from a JSON string
role_export_field_mapping_instance = RoleExportFieldMapping.from_json(json)
# print the JSON string representation of the object
print(RoleExportFieldMapping.to_json())

# convert the object into a dict
role_export_field_mapping_dict = role_export_field_mapping_instance.to_dict()
# create an instance of RoleExportFieldMapping from a dict
role_export_field_mapping_from_dict = RoleExportFieldMapping.from_dict(role_export_field_mapping_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


