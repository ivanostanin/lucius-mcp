# TreeDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_by** | **str** |  | [optional] 
**created_date** | **int** |  | [optional] 
**fields** | [**List[CustomFieldDto]**](CustomFieldDto.md) |  | [optional] 
**id** | **int** |  | [optional] 
**last_modified_by** | **str** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**project_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.tree_dto import TreeDto

# TODO update the JSON string below
json = "{}"
# create an instance of TreeDto from a JSON string
tree_dto_instance = TreeDto.from_json(json)
# print the JSON string representation of the object
print(TreeDto.to_json())

# convert the object into a dict
tree_dto_dict = tree_dto_instance.to_dict()
# create an instance of TreeDto from a dict
tree_dto_from_dict = TreeDto.from_dict(tree_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


