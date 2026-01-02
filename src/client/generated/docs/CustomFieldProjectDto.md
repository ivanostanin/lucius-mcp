# CustomFieldProjectDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_by** | **str** |  | [optional] 
**created_date** | **int** |  | [optional] 
**custom_field** | [**CustomFieldDto**](CustomFieldDto.md) |  | [optional] 
**default_custom_field_value_id** | **int** |  | [optional] 
**id** | **int** |  | [optional] 
**last_modified_by** | **str** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**locked** | **bool** |  | [optional] 
**name** | **str** |  | [optional] 
**project_id** | **int** |  | [optional] 
**required** | **bool** |  | [optional] 
**single_select** | **bool** |  | [optional] 

## Example

```python
from src.client.generated.models.custom_field_project_dto import CustomFieldProjectDto

# TODO update the JSON string below
json = "{}"
# create an instance of CustomFieldProjectDto from a JSON string
custom_field_project_dto_instance = CustomFieldProjectDto.from_json(json)
# print the JSON string representation of the object
print(CustomFieldProjectDto.to_json())

# convert the object into a dict
custom_field_project_dto_dict = custom_field_project_dto_instance.to_dict()
# create an instance of CustomFieldProjectDto from a dict
custom_field_project_dto_from_dict = CustomFieldProjectDto.from_dict(custom_field_project_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


