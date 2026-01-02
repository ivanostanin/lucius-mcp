# TestCaseRunStatsRequestDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**jobs_mapping** | [**List[JobMapping]**](JobMapping.md) |  | [optional] 
**selection** | [**TestCaseSelectionDtoV2**](TestCaseSelectionDtoV2.md) |  | 

## Example

```python
from src.client.generated.models.test_case_run_stats_request_dto import TestCaseRunStatsRequestDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseRunStatsRequestDto from a JSON string
test_case_run_stats_request_dto_instance = TestCaseRunStatsRequestDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseRunStatsRequestDto.to_json())

# convert the object into a dict
test_case_run_stats_request_dto_dict = test_case_run_stats_request_dto_instance.to_dict()
# create an instance of TestCaseRunStatsRequestDto from a dict
test_case_run_stats_request_dto_from_dict = TestCaseRunStatsRequestDto.from_dict(test_case_run_stats_request_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


