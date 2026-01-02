# TestResultStatsDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**automated** | **int** |  | [optional] 
**manual** | **int** |  | [optional] 
**resolved** | **int** |  | [optional] 
**total** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.test_result_stats_dto import TestResultStatsDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestResultStatsDto from a JSON string
test_result_stats_dto_instance = TestResultStatsDto.from_json(json)
# print the JSON string representation of the object
print(TestResultStatsDto.to_json())

# convert the object into a dict
test_result_stats_dto_dict = test_result_stats_dto_instance.to_dict()
# create an instance of TestResultStatsDto from a dict
test_result_stats_dto_from_dict = TestResultStatsDto.from_dict(test_result_stats_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


