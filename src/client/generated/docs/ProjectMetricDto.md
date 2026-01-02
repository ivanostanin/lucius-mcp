# ProjectMetricDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**labels** | **Dict[str, str]** |  | [optional] 
**metric_date** | **int** |  | [optional] 
**metric_id** | **int** |  | [optional] 
**project_id** | **int** |  | [optional] 
**value** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.project_metric_dto import ProjectMetricDto

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectMetricDto from a JSON string
project_metric_dto_instance = ProjectMetricDto.from_json(json)
# print the JSON string representation of the object
print(ProjectMetricDto.to_json())

# convert the object into a dict
project_metric_dto_dict = project_metric_dto_instance.to_dict()
# create an instance of ProjectMetricDto from a dict
project_metric_dto_from_dict = ProjectMetricDto.from_dict(project_metric_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


