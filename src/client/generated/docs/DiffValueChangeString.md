# DiffValueChangeString


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**new_value** | **str** |  | [optional] 
**old_value** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.diff_value_change_string import DiffValueChangeString

# TODO update the JSON string below
json = "{}"
# create an instance of DiffValueChangeString from a JSON string
diff_value_change_string_instance = DiffValueChangeString.from_json(json)
# print the JSON string representation of the object
print(DiffValueChangeString.to_json())

# convert the object into a dict
diff_value_change_string_dict = diff_value_change_string_instance.to_dict()
# create an instance of DiffValueChangeString from a dict
diff_value_change_string_from_dict = DiffValueChangeString.from_dict(diff_value_change_string_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


