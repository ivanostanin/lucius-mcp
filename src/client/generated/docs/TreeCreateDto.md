# TreeCreateDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**fields** | [**List[IdOnlyDto]**](IdOnlyDto.md) |  | 
**name** | **str** |  | 
**project_id** | **int** |  | 

## Example

```python
from src.client.generated.models.tree_create_dto import TreeCreateDto

# TODO update the JSON string below
json = "{}"
# create an instance of TreeCreateDto from a JSON string
tree_create_dto_instance = TreeCreateDto.from_json(json)
# print the JSON string representation of the object
print(TreeCreateDto.to_json())

# convert the object into a dict
tree_create_dto_dict = tree_create_dto_instance.to_dict()
# create an instance of TreeCreateDto from a dict
tree_create_dto_from_dict = TreeCreateDto.from_dict(tree_create_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


