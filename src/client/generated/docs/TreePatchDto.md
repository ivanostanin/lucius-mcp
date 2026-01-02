# TreePatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**fields** | [**List[IdOnlyDto]**](IdOnlyDto.md) |  | [optional] 
**name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.tree_patch_dto import TreePatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of TreePatchDto from a JSON string
tree_patch_dto_instance = TreePatchDto.from_json(json)
# print the JSON string representation of the object
print(TreePatchDto.to_json())

# convert the object into a dict
tree_patch_dto_dict = tree_patch_dto_instance.to_dict()
# create an instance of TreePatchDto from a dict
tree_patch_dto_from_dict = TreePatchDto.from_dict(tree_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


