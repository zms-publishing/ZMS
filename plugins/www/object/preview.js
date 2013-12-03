// ************************************************************
// *** Empty API to display SCORM content in preview mode.
// ************************************************************

// Define exception/error codes
var _NoError = 0;
var _GeneralException = 101;
var _GeneralInitializationFailure = 102;
var _AlreadyInitialized = 103;
var _ContentInstanceTerminated = 104;
var _GeneralTerminationFailure = 111;
var _TerminationBeforeInitialization = 112;
var _TerminationAfterTermination = 113;
var _RetrieveDataBeforeInitialization = 122;
var _RetrieveDataAfterTermination = 123;
var _StoreDataBeforeInitialization = 132;
var _StoreDataAfterTermination = 133;
var _CommitBeforeInitialization = 142;
var _CommitAfterInitialization = 143;
var _GeneralArgumentError = 201;
var _GeneralGetFailure = 301;
var _GeneralSetFailure = 351;
var _GeneralCommitFailure = 391;
var _UndefinedDataModelElement = 401;
var _UnimplementedDataModelElement = 402;
var _DataModelElementValueNotInitialized = 403;
var _DataModelElementIsReadOnly = 404;
var _DataModelElementIsWriteOnly = 405;
var _DataModelElementTypeMismatch = 406;
var _DataModelElementValueOutOfRange = 407;
var _DataModelDependencyNotEstablished = 408;
var CMIBooleanTrue = "true";
var CMIBooleanFalse = "false";
var errCode = _NoError;
var errDiagnostic = "";

function findElement(arr, element) {
	for (var i=0;i<arr.length/2;i++) {
		key = arr[i*2];
		if (key==element)
			return i*2;
	}
	return -1;
}

function getElement(arr, element) {
	value = "";
	if (element.indexOf("cmi.core.")==0) {
		var i = findElement(arr,element);
		if (i>0)
			value = arr[i+1];
	}
	else if (element.indexOf("cmi.interactions.")==0) {
		var l = String("cmi.interactions.").length
		var k = parseInt(element.substring(l,l+element.substring(l).indexOf(".")));
		var node = element.substring(l+element.substring(l).indexOf(".")+1);
		var i = findElement(arr,"cmi.interactions");
		var arr2 = arr[i+1];
		if (arr2.length > k) {
			var arr3 = arr2[k]
			var j = findElement(arr3,node);
		if (j>0)
			value = arr3[j+1];
		}
	}
	return value;
}

function setElement(arr, element, value ) {
	if (element.indexOf("cmi.core.")==0) {
		var i = findElement(arr,element);
		if (i<0)
			i = arr.length;
		arr[i] = element;
		arr[i+1] = value;
	}
	else if (element.indexOf("cmi.interactions.")==0) {
		var l = String("cmi.interactions.").length
		var k = parseInt(element.substring(l,l+element.substring(l).indexOf(".")));
		var node = element.substring(l+element.substring(l).indexOf(".")+1);
		var i = findElement(arr,"cmi.interactions");
		var arr2 = arr[i+1];
		if (arr2.length<=k)
			arr2[k] = new Array();
		arr3 = arr2[k]
		var j = findElement(arr3,node);
		if (j<0) {
			j = arr3.length;
			arr3[j] = node;
		}
		arr3[j+1] = value;
	}
}

function LMSInitialize(parameter ) {
	if (parameter && parameter.length > 0) {
		errCode = _InvalidArgumentError;
		return CMIBooleanFalse;
	}
	var auth_user =$ZMI.getReqProperty('AUTHENTICATED_USER');
	setElement(this.cmi,"cmi.core.student_id",auth_user);
	setElement(this.cmi,"cmi.core.student_name",auth_user);
	setElement(this.cmi,"cmi.core.lesson_status","not attempted");
	// Return CMIBoolean-string.
	errCode = _NoError;
	return CMIBooleanTrue;
}

function LMSGetValue(element ) {
	var value = ""
	if (element=="cmi.interactions._count") {
		value = this.cmi_interactions_count;
		this.cmi_interactions_count++;
	}
	else {
		value = getElement(this.cmi,element);
	}
	return value;
}

function LMSSetValue(element, value ) {
	if (!(this.LMSGetValue("cmi.core.lesson_status")=="completed") &&
				!((this.LMSGetValue("cmi.core.lesson_status")=="passed" ||
				this.LMSGetValue("cmi.core.lesson_status")=="failed") &&
				element=="cmi.core.lesson_status" && value=="incomplete"))
			setElement(this.cmi,element,value);
	return errCode;
}

function LMSCommit(parameter ) {
	// Error-Code.
	if (parameter && parameter.length > 0) {
		errCode = _InvalidArgumentError;
	}
	if (errCode != _NoError) {
		return CMIBooleanFalse;
	}
	// Return CMIBoolean-string.
	errCode = _NoError;
	return CMIBooleanTrue;
}

function LMSTerminate(parameter ) {
	// Error-Code.
	if (parameter && parameter.length > 0) {
		errCode = _InvalidArgumentError;
	}
	if (errCode != _NoError) {
		return CMIBooleanFalse;
	}
	// Return CMIBoolean-string.
	errCode = _NoError;
	this.terminated = true;
	return CMIBooleanTrue;
}

function LMSGetLastError() {
	return errCode;
}

  function LMSGetErrorString(errorCode)
  {
    var errString = "";    
    if (errCode==_NoError)
      errString = "No error";
    else if (errCode==_GeneralException)
      errString = "General exception";
    else if (errCode==_ServerBusy)
      errString = "Server is busy";
    else if (errCode==_InvalidArgumentError)
      errString = "Invalid argument erro";
    else if (errCode==_ElementCannotHaveChildren)
      errString = "Element can not have children";
    else if (errCode==_ElementIsNotAnArray)
      errString = "Element is not an array";
    else if (errCode==_NotInitialized)
      errString = "Not initialized";
    else if (errCode==_NotImplementedError)
      errString = "Not implemented error";
    else if (errCode==_InvalidSetValue)
      errString = "Invalid set value";
    else if (errCode==_ElementIsReadOnly)
      errString = "Element is read only";
    else if (errCode==_ElementIsWriteOnly)
      errString = "Element is write only";
    else if (errCode==_IncorrectDataType)
      errString = "Incorrect data type";
    else
      errString = "Unknown errCode="+errCode;
    return errString;
  }

function LMSGetDiagnostic(errorCode) {
	var errDiagnostic = "";    
	if (errCode==_NoError)
		errDiagnostic = "No error";
	else if (errCode==_GeneralException)
		errDiagnostic = "General Exception";
	else if (errCode==_GeneralInitializationFailure)
		errDiagnostic = "General Initialization Failure";
	else if (errCode==_AlreadyInitialized)
		errDiagnostic = "Already Initialized";
	else if (errCode==_ContentInstanceTerminated)
		errDiagnostic = "Content Instance Terminated";
	else if (errCode==_GeneralTerminationFailure)
		errDiagnostic = "General Termination Failure";
	else if (errCode==_TerminationBeforeInitialization)
		errDiagnostic = "Termination Before Initialization";
	else if (errCode==_TerminationAfterTermination)
		errDiagnostic = "Termination After Termination";
	else if (errCode==_RetrieveDataBeforeInitialization)
		errDiagnostic = "Retrieve Data Before Initialization";
	else if (errCode==_RetrieveDataAfterTermination)
		errDiagnostic = "Retrieve Data After Termination";
	else if (errCode==_StoreDataBeforeInitialization)
		errDiagnostic = "Store Data Before Initialization";
	else if (errCode==_StoreDataAfterTermination)
		errDiagnostic = "Store Data After Termination";
	else if (errCode==_CommitBeforeInitialization)
		errDiagnostic = "Commit Before Initialization";
	else if (errCode==_CommitAfterInitialization)
		errDiagnostic = "Commit After Initialization";
	else if (errCode==_GeneralArgumentError)
		errDiagnostic = "General Argument Error";
	else if (errCode==_GeneralGetFailure)
		errDiagnostic = "General Get Failure";
	else if (errCode==_GeneralSetFailure)
		errDiagnostic = "General Set Failure";
	else if (errCode==_GeneralCommitFailure)
		errDiagnostic = "General Commit Failure";
	else if (errCode==_UndefinedDataModelElement)
		errDiagnostic = "Undefined Data Model Element";
	else if (errCode==_UnimplementedDataModelElement)
		errDiagnostic = "Unimplemented Data Model Element";
	else if (errCode==_DataModelElementValueNotInitialized)
		errDiagnostic = "Data Model Element Value Not Initialized";
	else if (errCode==_DataModelElementIsReadOnly)
		errDiagnostic = "Data Model Element Is Read Only";
	else if (errCode==_DataModelElementIsWriteOnly)
		errDiagnostic = "Data Model Element Is Write Only";
	else if (errCode==_DataModelElementTypeMismatch)
		errDiagnostic = "Data Model Element Type Mismatch";
	else if (errCode==_DataModelElementValueOutOfRange)
		errDiagnostic = "Data Model Element Value Out Of Range";
	else if (errCode==_DataModelDependencyNotEstablished)
		errDiagnostic = "Data Model Dependency Not Established";
	else
		errDiagnostic = "Unknown errCode="+errCode;
	return errDiagnostic;
}

function APIClass() {
	this.version = "1.0";
	this.cmi = new Array();
	this.cmi[this.cmi.length] = "cmi.interactions";
	this.cmi[this.cmi.length] = new Array();
	this.initialized = false;
	this.terminated = false;
	this.Initialize = LMSInitialize;
	this.GetValue = LMSGetValue;
	this.SetValue = LMSSetValue;
	this.Commit = LMSCommit;
	this.Terminate = LMSTerminate;
	this.GetLastError = LMSGetLastError;
	this.GetErrorString = LMSGetErrorString;
	this.GetDiagnostic = LMSGetDiagnostic;
}

var API_1484_11 = new APIClass();
