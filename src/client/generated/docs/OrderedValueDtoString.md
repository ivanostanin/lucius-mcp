# OrderedValueDtoString


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**order** | **int** |  | [optional] 
**value** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.ordered_value_dto_string import OrderedValueDtoString

# TODO update the JSON string below
json = "{}"
# create an instance of OrderedValueDtoString from a JSON string
ordered_value_dto_string_instance = OrderedValueDtoString.from_json(json)
# print the JSON string representation of the object
print(OrderedValueDtoString.to_json())

# convert the object into a dict
ordered_value_dto_string_dict = ordered_value_dto_string_instance.to_dict()
# create an instance of OrderedValueDtoString from a dict
ordered_value_dto_string_from_dict = OrderedValueDtoString.from_dict(ordered_value_dto_string_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


