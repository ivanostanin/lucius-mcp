# ProjectTestCaseCountDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**test_case_count** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.project_test_case_count_dto import ProjectTestCaseCountDto

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectTestCaseCountDto from a JSON string
project_test_case_count_dto_instance = ProjectTestCaseCountDto.from_json(json)
# print the JSON string representation of the object
print(ProjectTestCaseCountDto.to_json())

# convert the object into a dict
project_test_case_count_dto_dict = project_test_case_count_dto_instance.to_dict()
# create an instance of ProjectTestCaseCountDto from a dict
project_test_case_count_dto_from_dict = ProjectTestCaseCountDto.from_dict(project_test_case_count_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


