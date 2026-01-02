# AqlValidateResponseDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**count** | **int** |  | [optional] 
**valid** | **bool** |  | [optional] 

## Example

```python
from src.client.generated.models.aql_validate_response_dto import AqlValidateResponseDto

# TODO update the JSON string below
json = "{}"
# create an instance of AqlValidateResponseDto from a JSON string
aql_validate_response_dto_instance = AqlValidateResponseDto.from_json(json)
# print the JSON string representation of the object
print(AqlValidateResponseDto.to_json())

# convert the object into a dict
aql_validate_response_dto_dict = aql_validate_response_dto_instance.to_dict()
# create an instance of AqlValidateResponseDto from a dict
aql_validate_response_dto_from_dict = AqlValidateResponseDto.from_dict(aql_validate_response_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


