# TestCaseTreeRunStatRequestDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**deleted** | **bool** |  | [optional] 
**filter_id** | **int** |  | [optional] 
**groups_exclude** | **List[List[int]]** |  | [optional] 
**groups_include** | **List[List[int]]** |  | [optional] 
**inverted** | **bool** |  | [optional] 
**jobs_mapping** | [**List[JobMapping]**](JobMapping.md) |  | [optional] 
**leafs_exclude** | **List[int]** |  | [optional] 
**leafs_include** | **List[int]** |  | [optional] 
**path** | **List[int]** |  | [optional] 
**project_id** | **int** |  | 
**search** | **str** |  | [optional] 
**tree_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.test_case_tree_run_stat_request_dto import TestCaseTreeRunStatRequestDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseTreeRunStatRequestDto from a JSON string
test_case_tree_run_stat_request_dto_instance = TestCaseTreeRunStatRequestDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseTreeRunStatRequestDto.to_json())

# convert the object into a dict
test_case_tree_run_stat_request_dto_dict = test_case_tree_run_stat_request_dto_instance.to_dict()
# create an instance of TestCaseTreeRunStatRequestDto from a dict
test_case_tree_run_stat_request_dto_from_dict = TestCaseTreeRunStatRequestDto.from_dict(test_case_tree_run_stat_request_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


