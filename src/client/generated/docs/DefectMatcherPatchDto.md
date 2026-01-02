# DefectMatcherPatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message_regex** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**trace_regex** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.defect_matcher_patch_dto import DefectMatcherPatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of DefectMatcherPatchDto from a JSON string
defect_matcher_patch_dto_instance = DefectMatcherPatchDto.from_json(json)
# print the JSON string representation of the object
print(DefectMatcherPatchDto.to_json())

# convert the object into a dict
defect_matcher_patch_dto_dict = defect_matcher_patch_dto_instance.to_dict()
# create an instance of DefectMatcherPatchDto from a dict
defect_matcher_patch_dto_from_dict = DefectMatcherPatchDto.from_dict(defect_matcher_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


