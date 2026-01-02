# FilterPatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**body** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**shared** | **bool** |  | [optional] 

## Example

```python
from src.client.generated.models.filter_patch_dto import FilterPatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of FilterPatchDto from a JSON string
filter_patch_dto_instance = FilterPatchDto.from_json(json)
# print the JSON string representation of the object
print(FilterPatchDto.to_json())

# convert the object into a dict
filter_patch_dto_dict = filter_patch_dto_instance.to_dict()
# create an instance of FilterPatchDto from a dict
filter_patch_dto_from_dict = FilterPatchDto.from_dict(filter_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


