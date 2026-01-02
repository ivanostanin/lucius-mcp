# TestCaseVersionPatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **str** |  | [optional] 
**title** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.test_case_version_patch_dto import TestCaseVersionPatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseVersionPatchDto from a JSON string
test_case_version_patch_dto_instance = TestCaseVersionPatchDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseVersionPatchDto.to_json())

# convert the object into a dict
test_case_version_patch_dto_dict = test_case_version_patch_dto_instance.to_dict()
# create an instance of TestCaseVersionPatchDto from a dict
test_case_version_patch_dto_from_dict = TestCaseVersionPatchDto.from_dict(test_case_version_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


