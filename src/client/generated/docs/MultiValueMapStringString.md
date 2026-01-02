# MultiValueMapStringString


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**all** | **Dict[str, str]** |  | [optional] 
**empty** | **bool** |  | [optional] 

## Example

```python
from src.client.generated.models.multi_value_map_string_string import MultiValueMapStringString

# TODO update the JSON string below
json = "{}"
# create an instance of MultiValueMapStringString from a JSON string
multi_value_map_string_string_instance = MultiValueMapStringString.from_json(json)
# print the JSON string representation of the object
print(MultiValueMapStringString.to_json())

# convert the object into a dict
multi_value_map_string_string_dict = multi_value_map_string_string_instance.to_dict()
# create an instance of MultiValueMapStringString from a dict
multi_value_map_string_string_from_dict = MultiValueMapStringString.from_dict(multi_value_map_string_string_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


