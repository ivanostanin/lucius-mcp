# TestCodeGenerationRequestDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**lang** | **str** |  | 
**test_framework** | **str** |  | 
**sync_fields** | **bool** |  | 
**sync_name** | **bool** |  | 
**sync_tags** | **bool** |  | 
**sync_scenario** | **bool** |  | 

## Example

```python
from src.client.generated.models.test_code_generation_request_dto import TestCodeGenerationRequestDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCodeGenerationRequestDto from a JSON string
test_code_generation_request_dto_instance = TestCodeGenerationRequestDto.from_json(json)
# print the JSON string representation of the object
print(TestCodeGenerationRequestDto.to_json())

# convert the object into a dict
test_code_generation_request_dto_dict = test_code_generation_request_dto_instance.to_dict()
# create an instance of TestCodeGenerationRequestDto from a dict
test_code_generation_request_dto_from_dict = TestCodeGenerationRequestDto.from_dict(test_code_generation_request_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


