# TreePathItemDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**custom_field_id** | **int** |  | [optional] 
**id** | **int** |  | [optional] 
**name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.tree_path_item_dto import TreePathItemDto

# TODO update the JSON string below
json = "{}"
# create an instance of TreePathItemDto from a JSON string
tree_path_item_dto_instance = TreePathItemDto.from_json(json)
# print the JSON string representation of the object
print(TreePathItemDto.to_json())

# convert the object into a dict
tree_path_item_dto_dict = tree_path_item_dto_instance.to_dict()
# create an instance of TreePathItemDto from a dict
tree_path_item_dto_from_dict = TreePathItemDto.from_dict(tree_path_item_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


