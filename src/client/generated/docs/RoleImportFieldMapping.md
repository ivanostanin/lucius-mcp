# RoleImportFieldMapping


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items_separator** | **str** |  | [optional] 
**regex** | **bool** |  | [optional] 
**role_id** | **int** |  | 

## Example

```python
from src.client.generated.models.role_import_field_mapping import RoleImportFieldMapping

# TODO update the JSON string below
json = "{}"
# create an instance of RoleImportFieldMapping from a JSON string
role_import_field_mapping_instance = RoleImportFieldMapping.from_json(json)
# print the JSON string representation of the object
print(RoleImportFieldMapping.to_json())

# convert the object into a dict
role_import_field_mapping_dict = role_import_field_mapping_instance.to_dict()
# create an instance of RoleImportFieldMapping from a dict
role_import_field_mapping_from_dict = RoleImportFieldMapping.from_dict(role_import_field_mapping_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


