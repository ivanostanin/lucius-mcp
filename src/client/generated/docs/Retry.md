# Retry


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**status** | [**TestStatus**](TestStatus.md) |  | [optional] 

## Example

```python
from src.client.generated.models.retry import Retry

# TODO update the JSON string below
json = "{}"
# create an instance of Retry from a JSON string
retry_instance = Retry.from_json(json)
# print the JSON string representation of the object
print(Retry.to_json())

# convert the object into a dict
retry_dict = retry_instance.to_dict()
# create an instance of Retry from a dict
retry_from_dict = Retry.from_dict(retry_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


