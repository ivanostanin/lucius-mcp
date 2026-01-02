# TestStatusCount


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**count** | **int** |  | [optional] 
**status** | [**TestStatus**](TestStatus.md) |  | [optional] 

## Example

```python
from src.client.generated.models.test_status_count import TestStatusCount

# TODO update the JSON string below
json = "{}"
# create an instance of TestStatusCount from a JSON string
test_status_count_instance = TestStatusCount.from_json(json)
# print the JSON string representation of the object
print(TestStatusCount.to_json())

# convert the object into a dict
test_status_count_dict = test_status_count_instance.to_dict()
# create an instance of TestStatusCount from a dict
test_status_count_from_dict = TestStatusCount.from_dict(test_status_count_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


