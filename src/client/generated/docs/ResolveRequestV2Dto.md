# ResolveRequestV2Dto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**category_id** | **int** |  | [optional] 
**duration** | **int** |  | [optional] 
**execution** | [**TestResultScenarioV2Dto**](TestResultScenarioV2Dto.md) |  | [optional] 
**message** | **str** |  | [optional] 
**start** | **int** |  | [optional] 
**status** | [**TestStatus**](TestStatus.md) |  | 
**stop** | **int** |  | [optional] 
**trace** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.resolve_request_v2_dto import ResolveRequestV2Dto

# TODO update the JSON string below
json = "{}"
# create an instance of ResolveRequestV2Dto from a JSON string
resolve_request_v2_dto_instance = ResolveRequestV2Dto.from_json(json)
# print the JSON string representation of the object
print(ResolveRequestV2Dto.to_json())

# convert the object into a dict
resolve_request_v2_dto_dict = resolve_request_v2_dto_instance.to_dict()
# create an instance of ResolveRequestV2Dto from a dict
resolve_request_v2_dto_from_dict = ResolveRequestV2Dto.from_dict(resolve_request_v2_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


