# TestCaseRunByStats


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**automated** | **int** |  | [optional] 
**manual** | **int** |  | [optional] 
**not_run** | **int** |  | [optional] 
**total** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.test_case_run_by_stats import TestCaseRunByStats

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseRunByStats from a JSON string
test_case_run_by_stats_instance = TestCaseRunByStats.from_json(json)
# print the JSON string representation of the object
print(TestCaseRunByStats.to_json())

# convert the object into a dict
test_case_run_by_stats_dict = test_case_run_by_stats_instance.to_dict()
# create an instance of TestCaseRunByStats from a dict
test_case_run_by_stats_from_dict = TestCaseRunByStats.from_dict(test_case_run_by_stats_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


