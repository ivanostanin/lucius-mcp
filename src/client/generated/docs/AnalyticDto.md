# AnalyticDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**avg_duration** | **float** |  | [optional] 
**avg_success_rate** | **float** |  | [optional] 
**var_date** | **str** |  | [optional] 
**not_retried_count** | **int** |  | [optional] 
**retried_count** | **int** |  | [optional] 
**sum_duration** | **int** |  | [optional] 
**sum_duration_not_retried** | **int** |  | [optional] 
**sum_duration_retried** | **int** |  | [optional] 
**test_cases_count** | **int** |  | [optional] 
**test_results_count** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.analytic_dto import AnalyticDto

# TODO update the JSON string below
json = "{}"
# create an instance of AnalyticDto from a JSON string
analytic_dto_instance = AnalyticDto.from_json(json)
# print the JSON string representation of the object
print(AnalyticDto.to_json())

# convert the object into a dict
analytic_dto_dict = analytic_dto_instance.to_dict()
# create an instance of AnalyticDto from a dict
analytic_dto_from_dict = AnalyticDto.from_dict(analytic_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


