# TestCaseTreeFilterCountDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**filtered** | **int** |  | [optional] 
**total** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.test_case_tree_filter_count_dto import TestCaseTreeFilterCountDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseTreeFilterCountDto from a JSON string
test_case_tree_filter_count_dto_instance = TestCaseTreeFilterCountDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseTreeFilterCountDto.to_json())

# convert the object into a dict
test_case_tree_filter_count_dto_dict = test_case_tree_filter_count_dto_instance.to_dict()
# create an instance of TestCaseTreeFilterCountDto from a dict
test_case_tree_filter_count_dto_from_dict = TestCaseTreeFilterCountDto.from_dict(test_case_tree_filter_count_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


