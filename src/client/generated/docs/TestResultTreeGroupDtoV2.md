# TestResultTreeGroupDtoV2


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**custom_field_id** | **int** |  | [optional] 
**statistic** | [**StatisticDto**](StatisticDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.test_result_tree_group_dto_v2 import TestResultTreeGroupDtoV2

# TODO update the JSON string below
json = "{}"
# create an instance of TestResultTreeGroupDtoV2 from a JSON string
test_result_tree_group_dto_v2_instance = TestResultTreeGroupDtoV2.from_json(json)
# print the JSON string representation of the object
print(TestResultTreeGroupDtoV2.to_json())

# convert the object into a dict
test_result_tree_group_dto_v2_dict = test_result_tree_group_dto_v2_instance.to_dict()
# create an instance of TestResultTreeGroupDtoV2 from a dict
test_result_tree_group_dto_v2_from_dict = TestResultTreeGroupDtoV2.from_dict(test_result_tree_group_dto_v2_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


