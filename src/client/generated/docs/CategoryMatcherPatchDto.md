# CategoryMatcherPatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**category** | [**IdOnlyDto**](IdOnlyDto.md) |  | [optional] 
**message_regex** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**trace_regex** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.category_matcher_patch_dto import CategoryMatcherPatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of CategoryMatcherPatchDto from a JSON string
category_matcher_patch_dto_instance = CategoryMatcherPatchDto.from_json(json)
# print the JSON string representation of the object
print(CategoryMatcherPatchDto.to_json())

# convert the object into a dict
category_matcher_patch_dto_dict = category_matcher_patch_dto_instance.to_dict()
# create an instance of CategoryMatcherPatchDto from a dict
category_matcher_patch_dto_from_dict = CategoryMatcherPatchDto.from_dict(category_matcher_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


