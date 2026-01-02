# ProjectCustomFieldDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_by** | **str** |  | [optional] 
**created_date** | **int** |  | [optional] 
**custom_field_id** | **int** |  | [optional] 
**custom_field_locked** | **bool** |  | [optional] 
**custom_field_name** | **str** |  | [optional] 
**custom_field_required** | **bool** |  | [optional] 
**id** | **int** |  | [optional] 
**is_public** | **bool** |  | [optional] 
**last_modified_by** | **str** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.project_custom_field_dto import ProjectCustomFieldDto

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectCustomFieldDto from a JSON string
project_custom_field_dto_instance = ProjectCustomFieldDto.from_json(json)
# print the JSON string representation of the object
print(ProjectCustomFieldDto.to_json())

# convert the object into a dict
project_custom_field_dto_dict = project_custom_field_dto_instance.to_dict()
# create an instance of ProjectCustomFieldDto from a dict
project_custom_field_dto_from_dict = ProjectCustomFieldDto.from_dict(project_custom_field_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


