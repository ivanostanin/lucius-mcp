# ProjectStatsDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**automated_test_cases** | **int** |  | [optional] 
**automation_percent** | **float** |  | [optional] 
**launches** | **int** |  | [optional] 
**manual_test_cases** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.project_stats_dto import ProjectStatsDto

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectStatsDto from a JSON string
project_stats_dto_instance = ProjectStatsDto.from_json(json)
# print the JSON string representation of the object
print(ProjectStatsDto.to_json())

# convert the object into a dict
project_stats_dto_dict = project_stats_dto_instance.to_dict()
# create an instance of ProjectStatsDto from a dict
project_stats_dto_from_dict = ProjectStatsDto.from_dict(project_stats_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


