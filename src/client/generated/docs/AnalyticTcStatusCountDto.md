# AnalyticTcStatusCountDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**count** | **int** |  | [optional] 
**status_color** | **str** |  | [optional] 
**status_id** | **int** |  | [optional] 
**status_name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.analytic_tc_status_count_dto import AnalyticTcStatusCountDto

# TODO update the JSON string below
json = "{}"
# create an instance of AnalyticTcStatusCountDto from a JSON string
analytic_tc_status_count_dto_instance = AnalyticTcStatusCountDto.from_json(json)
# print the JSON string representation of the object
print(AnalyticTcStatusCountDto.to_json())

# convert the object into a dict
analytic_tc_status_count_dto_dict = analytic_tc_status_count_dto_instance.to_dict()
# create an instance of AnalyticTcStatusCountDto from a dict
analytic_tc_status_count_dto_from_dict = AnalyticTcStatusCountDto.from_dict(analytic_tc_status_count_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


