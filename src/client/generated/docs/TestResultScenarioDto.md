# TestResultScenarioDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**attachments** | [**List[TestResultAttachmentStepDtoAllOfAttachment]**](TestResultAttachmentStepDtoAllOfAttachment.md) |  | [optional] 
**steps** | [**List[TestResultScenarioStepDto]**](TestResultScenarioStepDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.test_result_scenario_dto import TestResultScenarioDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestResultScenarioDto from a JSON string
test_result_scenario_dto_instance = TestResultScenarioDto.from_json(json)
# print the JSON string representation of the object
print(TestResultScenarioDto.to_json())

# convert the object into a dict
test_result_scenario_dto_dict = test_result_scenario_dto_instance.to_dict()
# create an instance of TestResultScenarioDto from a dict
test_result_scenario_dto_from_dict = TestResultScenarioDto.from_dict(test_result_scenario_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


