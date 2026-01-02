# ParameterValueDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**value** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.parameter_value_dto import ParameterValueDto

# TODO update the JSON string below
json = "{}"
# create an instance of ParameterValueDto from a JSON string
parameter_value_dto_instance = ParameterValueDto.from_json(json)
# print the JSON string representation of the object
print(ParameterValueDto.to_json())

# convert the object into a dict
parameter_value_dto_dict = parameter_value_dto_instance.to_dict()
# create an instance of ParameterValueDto from a dict
parameter_value_dto_from_dict = ParameterValueDto.from_dict(parameter_value_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


