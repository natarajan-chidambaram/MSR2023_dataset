# MSR2023 Dataset

#### This repository provides the datasets of our work on the scientific paper titled - 
#### "A Dataset of Bot and Human Activities in GitHub"
The main goal of this scientific paper is to distribute a dataset of high-level activity types that were identified from low-level GitHub event types that were queried from GitHub Events API for the considered set of bots and human contributors. This dataset will be valuable for future empirical studies that focusses on bot-based studies as it contains around 600K activities performed by 384 bots and 585 humans involved in GitHub repositories. 

The activities that are identified from events is not one-to-one. Some activities are obtained by sequences of two events, where the second event is optional (marked with "?"). For example, in the following table, ReleaseEvent is mandatory for the activity Publishing a release, but CreateEvent is optional as it happens only when a new tag is created along with that release.

| Activity type | Event type | Payload |
| ------------- | ---------- | ------- |
| Publishing a release | ReleaseEvent | action = "published" |
|  | "?" CreateEvent | ref_type = "tag" |

Smilarly, some events lead to different activities depending on the value present in the payload. For example, in the following table, Creating repository, Creating branch and Creating tag are obtained form CreateEvent.

| Activity type | Event type | Payload |
| ------------- | ---------- | ------- |
| Creating repository | CreateEvent | ref_type = "repository" |
| Creating branch | CreateEvent | ref_type = "branch" |
| Creating tag | CreateEvent | ref_type = "tag" |

In total, we have identified 24 different activity types from 15 different event types.

| S.No | Activity type | Event type | Payload |
| -----| ------------- | ---------- | ------- |
| 1 | Creating repository | CreateEvent | ref_type = "repository" |
| 2 | Creating branch | CreateEvent | ref_type = "branch" |
| 3 | Creating tag | CreateEvent | ref_type = "tag" |
| 4 | Deleting tag | DeleteEvent | ref_type = "tag" |
| 5 | Deleting repository | DeleteEvent | ref_type = "branch" |
| 6 | Publishing a release | ReleaseEvent | action = "published" |
|   |                      | "?" CreateEvent | ref_type = "tag" |
| 7 | Making repository public | PublicEvent | - |
| 8 | Adding collaborator to repository | MemberEvent | action = "added" |
| 9 | Forking repository | ForkEvent | - |
| 10 | Starring repository | WatchEvent | action = "started" |
| 11 | Editing wiki page | GollumEvent | pages-->action = "created" or "edited" |
| 12 | Opening issue | IssuesEvent | action = "opened" |
| 13 | Closing issue | IssuesEvent | action = "opened" |
|    |               | "?" IssueCommentEvent | action = "created" |
| 14 | Reopening issue | IssuesEvent | action = "reopened" |
|    |               | "?" IssueCommentEvent | action = "created" |
| 15 | Transferring issue | IssuesEvent | action = "opened" |
| 16 | Commenting issue | IssueCommentEvent | action = "created" |
| 17 | Opening pull request | PullRequestEvent | action = "opened" |
| 18 | Closing pull request | PullRequestEvent | action = "closed" |
|    |               | "?" IssueCommentEvent | action = "created" |
| 19 | Reopening pull request | PullRequestEvent | action = "opened" |
|    |               | "?" IssueCommentEvent | action = "created" |
| 20 | Commenting pull request | IssueCommentEvent | action = "created" |
| 21 | Commenting pull request changes | PullrequestReviewCommentEvent | action = "created" |
|    |               | "?" PullRequestReviewEvent | action = "created" |
| 22 | Reviewing code | PullRequestReviewEvent | action = "created" |
| 23 | Commenting commits | CommitCommentEvent | action = "created" |
| 24 | Puhsing commits | PushEvent | - |

Following is an example of an activity - "Closing pull request"

```
{
  "date": "2022-11-25T18:49:09+00:00",
  "activity": "Closing pull request",
  "contributor": "typescript-bot",
  "repository": "DefinitelyTyped/DefinitelyTyped",
  "comment": {
      "length": 249,
      "GH_node": "IC_kwDOAFz6BM5PJG7l"
  },
  "pull_request": {
      "id": 62328,
      "title": "[qunit] Add `test.each()`",
      "created_at": "2022-09-19T17:34:28+00:00",
      "status": "closed",
      "closed_at": "2022-11-25T18:49:08+00:00",
      "merged": false,
      "GH_node": "PR_kwDOAFz6BM4_N5ib"
  },
  "conversation": {
      "comments": 19
  },
  "payload": {
      "pr_commits": 1,
      "pr_changed_files": 5
  }
}
```

## Activities and their field description

_Activities performed by GitHub contributors_

Type: `object`

**_Properties_**

 - <b id="#/properties/date">date</b>
	 - _Date on which the activity is performed_
	 - _e.g., "2022-11-25T09:55:19+00:00"_
	 - Type: `string`
	 - String format must be a "date-time"
 - <b id="#/properties/activity">activity</b>
	 - _The activity performed by the contributor_
	 - _e.g., "Commenting pull request"_
	 - Type: `string`
 - <b id="#/properties/contributor">contributor</b>
	 - _The login name of the contributor who performed this activty_
	 - _e.g., "analysis-bot", "anonymised" in the case of a human contributor_
	 - Type: `string`
 - <b id="#/properties/repository">repository</b>
	 - _The repository in which the activity is performed_
	 - _e.g., "apache/spark", "anonymised" in the case of a human contributor_
	 - Type: `string`
 - <b id="#/properties/issue">issue</b>
	 - Issue information - provided for activities such as Opening issue, Closing issue, Reopening issue, Transferring issue and Commenting issue
	 - Type: `object`
	 - **_Properties_**
		 - <b id="#/properties/issue/properties/id">id</b>
			 - _Issue number_
			 -  _e.g., 35471_
			 - Type: `integer`
		 - <b id="#/properties/issue/properties/title">title</b>
			 - _Issue title_
			 - _e.g., "error building handtracking gpu example with bazel", "anonymised" in the case of a human contributor_
			 - Type: `string`
		 - <b id="#/properties/issue/properties/created_at">created_at</b>
			 - _The date on which this issue is created_
			 - _e.g., "2022-11-10T13:07:23+00:00"_
			 - Type: `string`
			 - String format must be a "date-time"
		 - <b id="#/properties/issue/properties/status">status</b>
			 - _Current state of the issue_
			 - _"open" or "closed"_
			 - Type: `string`
		 - <b id="#/properties/issue/properties/closed_at">closed_at</b>
			 - _The date on which this issue is closed. "null" will be provided if the issue is open_
			 - _e.g., "2022-11-25T10:42:39+00:00"_
			 - Types: `string`, `null`
			 - String format must be a "date-time"
		 - <b id="#/properties/issue/properties/resolved">resolved</b>
			 - _If the issue is resolved or not_planned/still open_
			 - _true or false_
			 - Type: `boolean`
		 - <b id="#/properties/issue/properties/GH_node">GH_node</b>
			 - _The GitHub node of this issue_
			 - _e.g., "IC_kwDOC27xRM5PHTBU",  "anonymised" in the case of a human contributor_
			 - Type: `string`
 - <b id="#/properties/pull_request">pull_request</b>
	 - Pull request information - provided for activities such as Opening pull request, Closing pull request, Reopening pull request, Commenting pull request changes and Reviewing code
	 - Type: `object`
	 - **_Properties_**
		 - <b id="#/properties/pull_request/properties/id">id</b>
			 - _Pull request number_
			 - _e.g., 35471_
			 - Type: `integer`
		 - <b id="#/properties/pull_request/properties/title">title</b>
			 - _Pull request title_
			 - _e.g., "error building handtracking gpu example with bazel", "anonymised" in the case of a human contributor_
			 - Type: `string`
		 - <b id="#/properties/pull_request/properties/created_at">created_at</b>
			 - _The date on which this pull request is created_
			 - _e.g., "2022-11-10T13:07:23+00:00"_
			 - Type: `string`
			 - String format must be a "date-time"
		 - <b id="#/properties/pull_request/properties/status">status</b>
			 - _Current state of the pull request
			 - _"open" or "closed"_
			 - Type: `string`
		 - <b id="#/properties/pull_request/properties/closed_at">closed_at</b>
			 - _The date on which this pull request is closed. "null" will be provided if the pull request is open_
			 - _e.g., "2022-11-25T10:42:39+00:00"_
			 - Types: `string`, `null`
			 - String format must be a "date-time"
		 - <b id="#/properties/pull_request/properties/merged">merged</b>
			 - _If the PR is merged or rejected/still open_
			 - _true or false_
			 - Type: `boolean`
		 - <b id="#/properties/pull_request/properties/GH_node">GH_node</b>
			 - _The GitHub node of this pull request_
			 - _e.g., "PR_kwDOC7Q2kM5Dsu3-", "anonymised" in the case of a human contributor_
			 - Type: `string`
 - <b id="#/properties/review">review</b>
	 - Pull request review information - provided for activity Reviewing code
	 - Type: `object`
	 - **_Properties_**
		 - <b id="#/properties/review/properties/status">status</b>
			 - _Status of the review_
			 - _"changes_requested" or "approved" or "dismissed"_
			 - Type: `string`
		 - <b id="#/properties/review/properties/GH_node">GH_node</b>
			 - _The GitHub node of this review_
			 - _e.g., "PRR_kwDOEBHXU85HLfIn", "anonymised" in the case of a human contributor_
			 - Type: `string`
 - <b id="#/properties/conversation">conversation</b>
	 - Comments information in issue or pull request - Provided for activities such as Opening issue, Closing issue, Reopening issue, Transferring issue, Commenting issue, Opening pull request, Closing pull request, Reopening pull request and Commenting pull request
	 - Type: `object`
	 - **_Properties_**
		 - <b id="#/properties/conversation/properties/comments">comments</b>
			 - _Number of comments present in corresponding issue or pull request_
			 - _e.g., 5_
			 - Type: `integer`
 - <b id="#/properties/conversation">comment</b>
	 - Comment information - Provided for all the activities for which issue and pull request are reported and additionally for commit comment
	 - Type: `object`
	 - **_Properties_**
		 - <b id="#/properties/comment/properties/length">length</b>
			 - _Length of the comment text or description text in place where comment is not expected_
			 - _e.g., 25_
			 - Type: `integer`
		 - <b id="#/properties/comment/properties/GH_node">GH_node</b>
			 - _The GitHub node of this comment or description. "null" will be provided if there is no comment expected
			 - _e.g., "IC_kwDOEj6V8c5PHT78", "anonymised" in the case of a human contributor_
			 - Types: `string`, `null`
 - <b id="#/properties/gitref">gitref</b>
	 - Tag information - provided for activities such as Creating branch, Creating tag, Deleting branch, Deleting tag, Editing wiki page and Publishing a release
	 - Type: `object`
	 - **_Properties_**
		 - <b id="#/properties/gitref/properties/type">type</b>
			 - _Type of the gitref
			 - _"tag" or "branch" or "commit"_
			 - Type: `string`
		 - <b id="#/properties/gitref/properties/name">name</b>
			 - _Name of the gitref_
			 - _e.g., "cherry-pick-11-to-release-4.10"_
			 - Type: `string`
		 - <b id="#/properties/gitref/properties/description_length">description_length</b>
			 - _Length of the description text provided while creating the gitref. "null" be provided if the type is "branch" or "commit" as they do not have any description_
			 - _e.g., 23_
			 - Types: `integer`, `null`
 - <b id="#/properties/release">release</b>
	 - Release information - provided for activity Publishing a release
	 - Type: `object`
	 - **_Properties_**
		 - <b id="#/properties/release/properties/name">name</b>
			 - _The name of the release that is created. "null" will be provided if the name is not provided_
			 - _e.g., "v0.65.9"_
			 - Types: `string`, `null`
		 - <b id="#/properties/release/properties/description_length">description_length</b>
			 - _Description of the release that is created_
			 - _e.g., 888_
			 - Type: `integer`
		 - <b id="#/properties/release/properties/created_at">created_at</b>
			 - _The date at which the release is created (activity date is the release published date)_
			 - _e.g., "2022-11-25T11:34:48+00:00"_
			 - Type: `string`
			 - String format must be a "date-time"
		 - <b id="#/properties/release/properties/prerelease">prerelease</b>
			 - _If the release that is created is a prerelease or not_
			 - _true or false_
			 - Type: `boolean`
		 - <b id="#/properties/release/properties/new_tag">new_tag</b>
			 - _If a new tag is created for this release or another tag is re-used_
			 - _true or false_
			 - Type: `boolean`
		 - <b id="#/properties/release/properties/GH_node">GH_node</b>
			 - _The corresponding release node id_
			 - _e.g., "RE_kwDOCm6M2s4FBGxT", "anonymised" in the case of a human contributor_
			 - Type: `string`
 - <b id="#/properties/page">page</b>
	 - Page information for documentation/wiki
	 - Type: `object`
	 - **_Properties_**
		 - <b id="#/properties/page/properties/name">name</b>
			 - _Name of the page_
			 - _e.g., "Workflow-status"_
			 - Type: `string`
		 - <b id="#/properties/page/properties/title">title</b>
			 - _Title of the page_
			 - _e.g., "Workflow status"_
			 - Type: `string`
		 - <b id="#/properties/page/properties/new">new</b>
			 - _If the page is created new or existing page is edited_
			 - _true or false_
			 - Type: `boolean`
 - <b id="#/properties/payload">payload</b>
     - Other additional details - Provided for activities such as Opening pull request, Closing pull request, Reopening pull request and pushing commits
	 - Type: `object`
	 - **_Properties_**
		 - <b id="#/properties/payload/properties/pr_changed_files">pr_changed_files</b>
			 - _The number of files that are changed in this pullrequest_
			 - _e.g., 2_
			 - Type: `integer`
		 - <b id="#/properties/payload/properties/pr_commits">pr_commits</b>
			 - _The number of commits in this pullrequest_
			 - _e.g., 3_
			 - Type: `integer`
		 - <b id="#/properties/payload/properties/pushed_commits">pushed_commits</b>
			 - _The number of commits in this pullrequest_
			 - _e.g., 4_
			 - Type: `integer`
		 - <b id="#/properties/payload/properties/distinct_pushed_commits">distinct_pushed_commits</b>
			 - _The distinct number of commits in this pullrequest_
			 - _e.g., 1_
			 - Type: `integer`
		 - <b id="#/properties/payload/properties/github_push_id">github_push_id</b>
			 - _The corresponding github push id_
			 - _e.g., 11790446870, "anonymised" in the case of a human contributor_
			 - Type: `integer`
	

## Files description

#### 1) bot_activities.json.zip & human_activities.json.zip 
These are the files that contain the activity details of the contributors

#### 2) JsonSchema
A json file used for validating the json file containing bot and human activities

#### 3) Code&Data
This has the corresponding groundtruth data and the scripts for curating the bot accounts, querying the events and identifying the activities
