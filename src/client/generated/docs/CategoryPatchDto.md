# CategoryPatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**color** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.category_patch_dto import CategoryPatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of CategoryPatchDto from a JSON string
category_patch_dto_instance = CategoryPatchDto.from_json(json)
# print the JSON string representation of the object
print(CategoryPatchDto.to_json())

# convert the object into a dict
category_patch_dto_dict = category_patch_dto_instance.to_dict()
# create an instance of CategoryPatchDto from a dict
category_patch_dto_from_dict = CategoryPatchDto.from_dict(category_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


