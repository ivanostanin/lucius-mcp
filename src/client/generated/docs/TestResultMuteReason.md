# TestResultMuteReason


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**issues** | [**List[IssueDto]**](IssueDto.md) |  | [optional] 
**name** | **str** |  | [optional] 
**reason** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.test_result_mute_reason import TestResultMuteReason

# TODO update the JSON string below
json = "{}"
# create an instance of TestResultMuteReason from a JSON string
test_result_mute_reason_instance = TestResultMuteReason.from_json(json)
# print the JSON string representation of the object
print(TestResultMuteReason.to_json())

# convert the object into a dict
test_result_mute_reason_dict = test_result_mute_reason_instance.to_dict()
# create an instance of TestResultMuteReason from a dict
test_result_mute_reason_from_dict = TestResultMuteReason.from_dict(test_result_mute_reason_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


