# LaunchMemberStatsDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**assignee** | **str** |  | [optional] 
**defects_count** | **int** |  | [optional] 
**duration_sum** | **int** |  | [optional] 
**first_name** | **str** |  | [optional] 
**last_name** | **str** |  | [optional] 
**muted_count** | **int** |  | [optional] 
**retried_count** | **int** |  | [optional] 
**statistic** | [**List[TestStatusCount]**](TestStatusCount.md) |  | [optional] 

## Example

```python
from src.client.generated.models.launch_member_stats_dto import LaunchMemberStatsDto

# TODO update the JSON string below
json = "{}"
# create an instance of LaunchMemberStatsDto from a JSON string
launch_member_stats_dto_instance = LaunchMemberStatsDto.from_json(json)
# print the JSON string representation of the object
print(LaunchMemberStatsDto.to_json())

# convert the object into a dict
launch_member_stats_dto_dict = launch_member_stats_dto_instance.to_dict()
# create an instance of LaunchMemberStatsDto from a dict
launch_member_stats_dto_from_dict = LaunchMemberStatsDto.from_dict(launch_member_stats_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


