# TreeCustomFieldProjectDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**custom_field** | [**CustomFieldRawDto**](CustomFieldRawDto.md) |  | [optional] 
**default_custom_field_value_id** | **int** |  | [optional] 
**id** | **int** |  | [optional] 
**locked** | **bool** |  | [optional] 
**required** | **bool** |  | [optional] 

## Example

```python
from src.client.generated.models.tree_custom_field_project_dto import TreeCustomFieldProjectDto

# TODO update the JSON string below
json = "{}"
# create an instance of TreeCustomFieldProjectDto from a JSON string
tree_custom_field_project_dto_instance = TreeCustomFieldProjectDto.from_json(json)
# print the JSON string representation of the object
print(TreeCustomFieldProjectDto.to_json())

# convert the object into a dict
tree_custom_field_project_dto_dict = tree_custom_field_project_dto_instance.to_dict()
# create an instance of TreeCustomFieldProjectDto from a dict
tree_custom_field_project_dto_from_dict = TreeCustomFieldProjectDto.from_dict(tree_custom_field_project_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


