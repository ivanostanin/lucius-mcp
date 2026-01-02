# DiffValueChangeSetLong


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**new_value** | **List[int]** |  | [optional] 
**old_value** | **List[int]** |  | [optional] 

## Example

```python
from src.client.generated.models.diff_value_change_set_long import DiffValueChangeSetLong

# TODO update the JSON string below
json = "{}"
# create an instance of DiffValueChangeSetLong from a JSON string
diff_value_change_set_long_instance = DiffValueChangeSetLong.from_json(json)
# print the JSON string representation of the object
print(DiffValueChangeSetLong.to_json())

# convert the object into a dict
diff_value_change_set_long_dict = diff_value_change_set_long_instance.to_dict()
# create an instance of DiffValueChangeSetLong from a dict
diff_value_change_set_long_from_dict = DiffValueChangeSetLong.from_dict(diff_value_change_set_long_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


