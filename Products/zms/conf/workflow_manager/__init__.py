class workflow:
	"""
	python-representation of workflow
	"""

	# Id
	id = "workflow"

	# Revision
	revision = "0.0.1"

	# Activities
	class Activities:
		ac_changed = {"icon":""
			,"icon_clazz":"fas fa-pencil-alt text-primary wf-icon"
			,"id":"AC_CHANGED"
			,"name":"Bearbeitet"}

		ac_requested = {"icon":""
			,"icon_clazz":"far fa-bell text-primary wf-icon"
			,"id":"AC_REQUESTED"
			,"name":"Eingereicht"}

		ac_rejected = {"icon":""
			,"icon_clazz":"far fa-thumbs-down text-danger wf-icon"
			,"id":"AC_REJECTED"
			,"name":"Abgelehnt"}

		ac_committed = {"icon":""
			,"icon_clazz":"far fa-thumbs-up text-success wf-icon"
			,"id":"AC_COMMITTED"
			,"name":"Publiziert"}

		ac_rolledback = {"icon":""
			,"icon_clazz":"fas fa-reply text-danger wf-icon"
			,"id":"AC_ROLLEDBACK"
			,"name":"Frühere Version"}

	# Transitions
	class Transitions:
		tr_enter = {"from":[]
			,"icon_clazz":"fas fa-play-circle text-success"
			,"id":"TR_ENTER"
			,"name":"Enter Workflow"
			,"performer":[]
			,"to":["AC_CHANGED"]}

		tr_expresscommit = {"from":[]
			,"icon_clazz":"fas fa-external-link-alt"
			,"id":"TR_EXPRESSCOMMIT"
			,"name":"Sofort publizieren"
			,"performer":[]
			,"to":["AC_COMMITTED"]
			,"type":"Page Template"}

		tr_request = {"from":["AC_CHANGED"
				,"AC_REJECTED"]
			,"icon_clazz":"far fa-bell wf-icon"
			,"id":"TR_REQUEST"
			,"name":"Einreichen"
			,"performer":["ZMSAdministrator"
				,"ZMSEditor"
				,"ZMSAuthor"]
			,"to":["AC_REQUESTED"]
			,"type":"Page Template"}

		tr_reject = {"from":["AC_REQUESTED"]
			,"icon_clazz":"far fa-thumbs-down wf-icon"
			,"id":"TR_REJECT"
			,"name":"Ablehnen"
			,"performer":["ZMSAdministrator"
				,"ZMSEditor"]
			,"to":["AC_REJECTED"]
			,"type":"Page Template"}

		tr_commit = {"from":["AC_CHANGED"
				,"AC_REQUESTED"
				,"AC_REJECTED"]
			,"icon_clazz":"far fa-thumbs-up wf-icon"
			,"id":"TR_COMMIT"
			,"name":"Publizieren"
			,"performer":["ZMSAdministrator"
				,"ZMSEditor"]
			,"to":["AC_COMMITTED"]
			,"type":"Script (Python)"}

		tr_rollback = {"from":["AC_CHANGED"
				,"AC_REQUESTED"
				,"AC_REJECTED"]
			,"icon_clazz":"fas fa-reply wf-icon"
			,"id":"TR_ROLLBACK"
			,"name":"Zurückziehen"
			,"performer":["ZMSAdministrator"
				,"ZMSEditor"
				,"ZMSAuthor"]
			,"to":["AC_ROLLEDBACK"]
			,"type":"Script (Python)"}

		tr_leave = {"from":["AC_COMMITTED"
				,"AC_ROLLEDBACK"]
			,"icon_clazz":"fas fa-stop-circle text-danger"
			,"id":"TR_LEAVE"
			,"name":"Leave Workflow"
			,"performer":[]
			,"to":[]}
