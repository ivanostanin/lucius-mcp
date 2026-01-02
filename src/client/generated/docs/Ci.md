# Ci


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**endpoint** | **str** |  | [optional] 
**type** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.ci import Ci

# TODO update the JSON string below
json = "{}"
# create an instance of Ci from a JSON string
ci_instance = Ci.from_json(json)
# print the JSON string representation of the object
print(Ci.to_json())

# convert the object into a dict
ci_dict = ci_instance.to_dict()
# create an instance of Ci from a dict
ci_from_dict = Ci.from_dict(ci_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


