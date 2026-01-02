# TestDurationCount


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**count** | **int** |  | [optional] 
**duration** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.test_duration_count import TestDurationCount

# TODO update the JSON string below
json = "{}"
# create an instance of TestDurationCount from a JSON string
test_duration_count_instance = TestDurationCount.from_json(json)
# print the JSON string representation of the object
print(TestDurationCount.to_json())

# convert the object into a dict
test_duration_count_dict = test_duration_count_instance.to_dict()
# create an instance of TestDurationCount from a dict
test_duration_count_from_dict = TestDurationCount.from_dict(test_duration_count_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


