# TreeDtoV2


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**custom_fields_project** | [**List[TreeCustomFieldProjectDto]**](TreeCustomFieldProjectDto.md) |  | [optional] 
**id** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**project_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.tree_dto_v2 import TreeDtoV2

# TODO update the JSON string below
json = "{}"
# create an instance of TreeDtoV2 from a JSON string
tree_dto_v2_instance = TreeDtoV2.from_json(json)
# print the JSON string representation of the object
print(TreeDtoV2.to_json())

# convert the object into a dict
tree_dto_v2_dict = tree_dto_v2_instance.to_dict()
# create an instance of TreeDtoV2 from a dict
tree_dto_v2_from_dict = TreeDtoV2.from_dict(tree_dto_v2_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


