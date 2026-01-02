# SessionVariable


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**key** | **str** |  | [optional] 
**value** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.session_variable import SessionVariable

# TODO update the JSON string below
json = "{}"
# create an instance of SessionVariable from a JSON string
session_variable_instance = SessionVariable.from_json(json)
# print the JSON string representation of the object
print(SessionVariable.to_json())

# convert the object into a dict
session_variable_dict = session_variable_instance.to_dict()
# create an instance of SessionVariable from a dict
session_variable_from_dict = SessionVariable.from_dict(session_variable_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


