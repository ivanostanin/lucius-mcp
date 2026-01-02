# TestCaseInfo


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**selector** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.test_case_info import TestCaseInfo

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseInfo from a JSON string
test_case_info_instance = TestCaseInfo.from_json(json)
# print the JSON string representation of the object
print(TestCaseInfo.to_json())

# convert the object into a dict
test_case_info_dict = test_case_info_instance.to_dict()
# create an instance of TestCaseInfo from a dict
test_case_info_from_dict = TestCaseInfo.from_dict(test_case_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


