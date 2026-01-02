# DefectPatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**closed** | **bool** |  | [optional] 
**description** | **str** |  | [optional] 
**name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.defect_patch_dto import DefectPatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of DefectPatchDto from a JSON string
defect_patch_dto_instance = DefectPatchDto.from_json(json)
# print the JSON string representation of the object
print(DefectPatchDto.to_json())

# convert the object into a dict
defect_patch_dto_dict = defect_patch_dto_instance.to_dict()
# create an instance of DefectPatchDto from a dict
defect_patch_dto_from_dict = DefectPatchDto.from_dict(defect_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


