# TestResultScenarioV2Dto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**steps** | [**List[TestResultScenarioV2DtoStepsInner]**](TestResultScenarioV2DtoStepsInner.md) |  | [optional] 

## Example

```python
from src.client.generated.models.test_result_scenario_v2_dto import TestResultScenarioV2Dto

# TODO update the JSON string below
json = "{}"
# create an instance of TestResultScenarioV2Dto from a JSON string
test_result_scenario_v2_dto_instance = TestResultScenarioV2Dto.from_json(json)
# print the JSON string representation of the object
print(TestResultScenarioV2Dto.to_json())

# convert the object into a dict
test_result_scenario_v2_dto_dict = test_result_scenario_v2_dto_instance.to_dict()
# create an instance of TestResultScenarioV2Dto from a dict
test_result_scenario_v2_dto_from_dict = TestResultScenarioV2Dto.from_dict(test_result_scenario_v2_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


