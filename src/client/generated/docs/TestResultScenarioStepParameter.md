# TestResultScenarioStepParameter


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**excluded** | **bool** |  | [optional] 
**hidden** | **bool** |  | [optional] 
**name** | **str** |  | [optional] 
**value** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.test_result_scenario_step_parameter import TestResultScenarioStepParameter

# TODO update the JSON string below
json = "{}"
# create an instance of TestResultScenarioStepParameter from a JSON string
test_result_scenario_step_parameter_instance = TestResultScenarioStepParameter.from_json(json)
# print the JSON string representation of the object
print(TestResultScenarioStepParameter.to_json())

# convert the object into a dict
test_result_scenario_step_parameter_dict = test_result_scenario_step_parameter_instance.to_dict()
# create an instance of TestResultScenarioStepParameter from a dict
test_result_scenario_step_parameter_from_dict = TestResultScenarioStepParameter.from_dict(test_result_scenario_step_parameter_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


