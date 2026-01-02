# AnalyticMuteTrendDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_date** | **int** |  | [optional] 
**muted** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.analytic_mute_trend_dto import AnalyticMuteTrendDto

# TODO update the JSON string below
json = "{}"
# create an instance of AnalyticMuteTrendDto from a JSON string
analytic_mute_trend_dto_instance = AnalyticMuteTrendDto.from_json(json)
# print the JSON string representation of the object
print(AnalyticMuteTrendDto.to_json())

# convert the object into a dict
analytic_mute_trend_dto_dict = analytic_mute_trend_dto_instance.to_dict()
# create an instance of AnalyticMuteTrendDto from a dict
analytic_mute_trend_dto_from_dict = AnalyticMuteTrendDto.from_dict(analytic_mute_trend_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


