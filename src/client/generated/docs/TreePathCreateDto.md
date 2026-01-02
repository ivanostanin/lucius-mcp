# TreePathCreateDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**List[IdOnlyDto]**](IdOnlyDto.md) |  | 
**tree_id** | **int** |  | 

## Example

```python
from src.client.generated.models.tree_path_create_dto import TreePathCreateDto

# TODO update the JSON string below
json = "{}"
# create an instance of TreePathCreateDto from a JSON string
tree_path_create_dto_instance = TreePathCreateDto.from_json(json)
# print the JSON string representation of the object
print(TreePathCreateDto.to_json())

# convert the object into a dict
tree_path_create_dto_dict = tree_path_create_dto_instance.to_dict()
# create an instance of TreePathCreateDto from a dict
tree_path_create_dto_from_dict = TreePathCreateDto.from_dict(tree_path_create_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


