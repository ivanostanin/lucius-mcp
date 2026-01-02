# TestFixtureResultV2Dto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**duration** | **int** |  | [optional] 
**id** | **int** |  | [optional] 
**message** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**scenario** | [**TestResultScenarioV2Dto**](TestResultScenarioV2Dto.md) |  | [optional] 
**start** | **int** |  | [optional] 
**status** | [**TestStatus**](TestStatus.md) |  | [optional] 
**stop** | **int** |  | [optional] 
**trace** | **str** |  | [optional] 
**type** | [**TestFixtureResultTypeDto**](TestFixtureResultTypeDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.test_fixture_result_v2_dto import TestFixtureResultV2Dto

# TODO update the JSON string below
json = "{}"
# create an instance of TestFixtureResultV2Dto from a JSON string
test_fixture_result_v2_dto_instance = TestFixtureResultV2Dto.from_json(json)
# print the JSON string representation of the object
print(TestFixtureResultV2Dto.to_json())

# convert the object into a dict
test_fixture_result_v2_dto_dict = test_fixture_result_v2_dto_instance.to_dict()
# create an instance of TestFixtureResultV2Dto from a dict
test_fixture_result_v2_dto_from_dict = TestFixtureResultV2Dto.from_dict(test_fixture_result_v2_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


