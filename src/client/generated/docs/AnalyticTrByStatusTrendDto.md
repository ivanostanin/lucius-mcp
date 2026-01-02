# AnalyticTrByStatusTrendDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**broken** | **int** |  | [optional] 
**var_date** | **str** |  | [optional] 
**failed** | **int** |  | [optional] 
**passed** | **int** |  | [optional] 
**skipped** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.analytic_tr_by_status_trend_dto import AnalyticTrByStatusTrendDto

# TODO update the JSON string below
json = "{}"
# create an instance of AnalyticTrByStatusTrendDto from a JSON string
analytic_tr_by_status_trend_dto_instance = AnalyticTrByStatusTrendDto.from_json(json)
# print the JSON string representation of the object
print(AnalyticTrByStatusTrendDto.to_json())

# convert the object into a dict
analytic_tr_by_status_trend_dto_dict = analytic_tr_by_status_trend_dto_instance.to_dict()
# create an instance of AnalyticTrByStatusTrendDto from a dict
analytic_tr_by_status_trend_dto_from_dict = AnalyticTrByStatusTrendDto.from_dict(analytic_tr_by_status_trend_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


