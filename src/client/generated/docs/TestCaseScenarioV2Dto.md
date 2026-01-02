# TestCaseScenarioV2Dto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**steps** | [**List[SharedStepScenarioDtoStepsInner]**](SharedStepScenarioDtoStepsInner.md) |  | [optional] 

## Example

```python
from src.client.generated.models.test_case_scenario_v2_dto import TestCaseScenarioV2Dto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseScenarioV2Dto from a JSON string
test_case_scenario_v2_dto_instance = TestCaseScenarioV2Dto.from_json(json)
# print the JSON string representation of the object
print(TestCaseScenarioV2Dto.to_json())

# convert the object into a dict
test_case_scenario_v2_dto_dict = test_case_scenario_v2_dto_instance.to_dict()
# create an instance of TestCaseScenarioV2Dto from a dict
test_case_scenario_v2_dto_from_dict = TestCaseScenarioV2Dto.from_dict(test_case_scenario_v2_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


