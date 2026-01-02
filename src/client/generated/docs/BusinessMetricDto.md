# BusinessMetricDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.business_metric_dto import BusinessMetricDto

# TODO update the JSON string below
json = "{}"
# create an instance of BusinessMetricDto from a JSON string
business_metric_dto_instance = BusinessMetricDto.from_json(json)
# print the JSON string representation of the object
print(BusinessMetricDto.to_json())

# convert the object into a dict
business_metric_dto_dict = business_metric_dto_instance.to_dict()
# create an instance of BusinessMetricDto from a dict
business_metric_dto_from_dict = BusinessMetricDto.from_dict(business_metric_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


