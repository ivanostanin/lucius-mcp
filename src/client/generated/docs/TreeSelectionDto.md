# TreeSelectionDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**groups_exclude** | **List[List[int]]** |  | [optional] 
**groups_include** | **List[List[int]]** |  | [optional] 
**inverted** | **bool** |  | [optional] 
**leafs_exclude** | **List[int]** |  | [optional] 
**leafs_include** | **List[int]** |  | [optional] 
**path** | **List[int]** |  | [optional] 

## Example

```python
from src.client.generated.models.tree_selection_dto import TreeSelectionDto

# TODO update the JSON string below
json = "{}"
# create an instance of TreeSelectionDto from a JSON string
tree_selection_dto_instance = TreeSelectionDto.from_json(json)
# print the JSON string representation of the object
print(TreeSelectionDto.to_json())

# convert the object into a dict
tree_selection_dto_dict = tree_selection_dto_instance.to_dict()
# create an instance of TreeSelectionDto from a dict
tree_selection_dto_from_dict = TreeSelectionDto.from_dict(tree_selection_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


