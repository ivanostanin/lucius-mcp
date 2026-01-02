# TestCaseVersionDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_by** | **str** |  | [optional] 
**created_date** | **int** |  | [optional] 
**description** | **str** |  | [optional] 
**id** | **int** |  | [optional] 
**test_case_last_modified_date** | **int** |  | [optional] 
**title** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.test_case_version_dto import TestCaseVersionDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseVersionDto from a JSON string
test_case_version_dto_instance = TestCaseVersionDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseVersionDto.to_json())

# convert the object into a dict
test_case_version_dto_dict = test_case_version_dto_instance.to_dict()
# create an instance of TestCaseVersionDto from a dict
test_case_version_dto_from_dict = TestCaseVersionDto.from_dict(test_case_version_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


