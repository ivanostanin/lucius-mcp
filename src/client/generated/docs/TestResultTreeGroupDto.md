# TestResultTreeGroupDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**custom_field_id** | **int** |  | [optional] 
**id** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**statistic** | [**StatisticDto**](StatisticDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.test_result_tree_group_dto import TestResultTreeGroupDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestResultTreeGroupDto from a JSON string
test_result_tree_group_dto_instance = TestResultTreeGroupDto.from_json(json)
# print the JSON string representation of the object
print(TestResultTreeGroupDto.to_json())

# convert the object into a dict
test_result_tree_group_dto_dict = test_result_tree_group_dto_instance.to_dict()
# create an instance of TestResultTreeGroupDto from a dict
test_result_tree_group_dto_from_dict = TestResultTreeGroupDto.from_dict(test_result_tree_group_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


