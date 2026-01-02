# AnalyticTcAutomationCountDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**automated** | **bool** |  | [optional] 
**count** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.analytic_tc_automation_count_dto import AnalyticTcAutomationCountDto

# TODO update the JSON string below
json = "{}"
# create an instance of AnalyticTcAutomationCountDto from a JSON string
analytic_tc_automation_count_dto_instance = AnalyticTcAutomationCountDto.from_json(json)
# print the JSON string representation of the object
print(AnalyticTcAutomationCountDto.to_json())

# convert the object into a dict
analytic_tc_automation_count_dto_dict = analytic_tc_automation_count_dto_instance.to_dict()
# create an instance of AnalyticTcAutomationCountDto from a dict
analytic_tc_automation_count_dto_from_dict = AnalyticTcAutomationCountDto.from_dict(analytic_tc_automation_count_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


